import re
import pyparsing as pp
import os
import logging

from structs.pms import PMSConf
from structs.pms import ComponentSet


logger = logging.getLogger(__name__)


def analyze_file_component(file_folder, files_list, components_structure: {}):
    full_file = ""
    files_processed = {}
    i = 0
    while i < len(files_list):
        file_name = files_list[i]
        if file_name in files_processed:
            i += 1
            continue
        try:
            file_obj = open(os.path.join(file_folder, file_name), "r")
        except IOError:
            logger.warning("Can not open file %s", os.path.join(file_folder, file_name))
            files_processed[file_name] = True
            i += 1
            continue
        with file_obj:
            for line in file_obj:
                if not line.isspace():
                    full_file += line
        # remove unnecessary comments
        full_file = comment_remover(full_file)
        # find other includes
        files_list.extend(_find_includes(full_file))
        # loop over components
        for key, value in components_structure.items():
            # do not process finished components
            if value.done:
                continue
            component_type = value.type
            component_signals = value.signals
            block_regex = re.compile(r'SC_MODULE\(' + component_type + r'\)', re.IGNORECASE)
            component_block = block_regex.search(full_file)
            if component_block:
                # look for signals in this file
                for component_signal, is_signal_in in component_signals.items():
                    port_found = False
                    component_regex_in = re.compile(r'sc_in.*' + component_signal + r'[ ,;].*$', re.IGNORECASE | re.MULTILINE)
                    component_regex_out = re.compile(r'sc_out.*' + component_signal + r'[ ,;].*$', re.IGNORECASE | re.MULTILINE)
                    for regex_match in component_regex_in.finditer(full_file):
                        port_found = True
                        logger.debug("Port %s on component %s:%s is input", component_signal,
                                     component_type, key)
                        component_signals[component_signal] = True
                        break
                    for regex_match in component_regex_out.finditer(full_file):
                        port_found = True
                        logger.debug("Port %s on component %s:%s is output", component_signal,
                                     component_type, key)
                        component_signals[component_signal] = False
                        break
                    if not port_found:
                        logger.warning("Port %s not found in component %s:%s", component_signal, component_type, key)
                # set the component as processed
                value.done = True
        # set component as done
        files_processed[file_name] = True
        i += 1


def _get_component_type(name, components_structure, module_string):
    block_regex = re.compile(r'^.*' + name + r'[ ,;].*$', re.IGNORECASE | re.MULTILINE)
    regex_out = ""
    for regex_match in block_regex.finditer(module_string):
        regex_out = regex_match.group()
        break

    py_parser_out = "UNKNOWN_TYPE"
    symbol_variable = pp.Word(pp.alphanums + '_')
    for match in symbol_variable.scanString(regex_out):
        py_parser_out = match[0][0]
        break
    else:
        logger.warning("Can not find type of component %s", name)
    components_structure[name] = ComponentSet(py_parser_out)
    return py_parser_out


def _find_includes(file_string):
    included_files = []
    include_regex = re.compile(r'#include[ ]+"(.*)"', re.IGNORECASE | re.MULTILINE)
    for regex_match in include_regex.finditer(file_string):
        logger.debug("Found new include file %s",regex_match.group(1))
        included_files.append(regex_match.group(1))
    return included_files


def analyze_module(module_string, pms_name, file_folder, include_files):
    # generate structure
    pms_structure = PMSConf(pms_name)
    # generate helper structure for components
    components_structure = {}
    # common symbols for parsing
    symbol_comma = pp.Literal(",").suppress()
    symbol_variable = pp.Word(pp.alphanums + '_')
    symbol_variable_more = pp.OneOrMore(symbol_comma + symbol_variable)
    symbol_func = pp.Combine(
        pp.Word(pp.alphanums + '_') + pp.Optional(pp.Literal("(") + pp.Word(pp.nums) + pp.Literal(")")))
    symbol_func_more = pp.OneOrMore(symbol_comma + symbol_func)
    symbol_parentheses1 = pp.Literal("(").suppress()
    symbol_parentheses2 = pp.Literal(")").suppress()
    symbol_quotes = pp.Literal(r'"').suppress()
    symbol_equals = pp.Literal("=").suppress()

    # find all levels
    set_level_str = pp.Suppress("SetLevel(")
    set_level_values = pp.Combine(
        pp.Word(pp.alphanums + '_' + '.') + pp.Optional(
            pp.Combine(pp.Literal('(') + pp.Word(pp.nums) + pp.Literal(')'))))
    set_level_str_end = pp.Suppress(");")
    parser = set_level_str + set_level_values + symbol_comma + set_level_values + symbol_comma + \
                     set_level_values + set_level_str_end
    levels = parser.searchString(module_string).asList()

    for match in levels:
        logger.debug("Found level: %s", match)
        match[1] = re.search(r'-?\d+\.?\d*', match[1]).group(0)
        match[2] = re.search(r'-?\d+\.?\d*', match[2]).group(0)
        pms_structure.add_level(match[0], float(match[1]), float(match[2]))
    # Generate automatic levels, with default values
    pms_structure.add_level("HOLD", 0, 0)
    pms_structure.add_level("OFF", 0, 0)
    pms_structure.add_level("OFF_RET", 0, 0)

    # PowerDomains
    parser = pp.Literal("PowerDomain").suppress() + symbol_variable + pp.Optional(symbol_variable_more)
    founded_pd = []
    for match in parser.scanString(module_string):
        logger.debug("Found power_domain: %s", match[0])
        founded_pd.extend(match[0])
    # PowerDomains settings
    for pd in founded_pd:
        power_domain = pp.Literal(pd).suppress()
        power_constructor = pp.Literal("PD").suppress()
        parser = power_domain + symbol_equals + power_constructor + symbol_parentheses1 + symbol_func + \
                        pp.Optional(symbol_func_more) + symbol_parentheses2
        power_domain_levels = parser.searchString(module_string).asList()
        # get just the first PD assigment
        # todo aks if PD can be multiple
        power_domain_level = power_domain_levels[0]
        logger.debug("Power domain: %s has these levels: %s", pd, power_domain_level)
        power_add_component = pp.Literal(".AddComponent").suppress()
        parser = power_domain + power_add_component + symbol_parentheses1 + symbol_quotes + symbol_variable + \
            symbol_quotes + symbol_parentheses2
        power_domain_components = []
        for component in parser.scanString(module_string):
            power_domain_components.extend(component[0])
        logger.debug("Power domain: %s has these components: %s", pd, power_domain_components)
        pms_structure.add_power_domain(pd, power_domain_components, power_domain_level)
        for component in power_domain_components:
            pms_structure.add_component(component, pd,
                                        _get_component_type(component, components_structure, module_string))

    # find signals
    signal1 = pp.Literal("sc_signal<")
    signal12 = pp.Word(pp.alphanums)
    signal2 = pp.Literal(">")
    signal_name = pp.Suppress(pp.Combine(signal1 + signal12 + signal2))
    parser = signal_name + symbol_variable + pp.Optional(symbol_variable_more)
    founded_signals = []
    for match in parser.scanString(module_string):
        logger.debug("Found levels: %s", match[0])
        founded_signals.extend(match[0])

    component_name = pp.Word(pp.alphanums + '_')
    component_function = pp.Literal(".").suppress() + pp.Word(pp.alphanums + '_') + symbol_parentheses1
    # bind signals to components and power_domains
    pd0_components = []
    for signal in founded_signals:
        pd0_temp_components = []
        parser = component_name + component_function + pp.Literal(signal) + symbol_parentheses2
        signal_in_real_pd = False
        for match in parser.scanString(module_string):
            component = match[0][0]
            component_wire = match[0][1]
            if component in pms_structure.components:
                pms_structure.add_signal(signal, pms_structure.components[component][0], component, component_wire)
                components_structure[component].signals[component_wire] = True
                signal_in_real_pd = True
            else:
                # add virtual power_domain
                logger.warning("Found signal %s connected to component %s without power domain", signal, component)
                pd0_temp_components.append((component, component_wire))
        if signal_in_real_pd:
            for comp in pd0_temp_components:
                logger.debug("Creating extra component %s to power_domain PD_GEN", comp[0])
                pd0_components.append(comp[0])
                pms_structure.add_component(comp[0], "PD_GEN",
                                            _get_component_type(comp[0], components_structure, module_string))
                pms_structure.add_signal(signal, "PD_GEN", comp[0], comp[1])
                components_structure[comp[0]].signals[comp[1]] = True
    # found out if signal is IN or OUT
    analyze_file_component(file_folder, include_files, components_structure)
    # update_signals from function
    for signal, power_domain_dict in pms_structure.signals.items():
        for pd, components in power_domain_dict.items():
            for component in components:
                if components_structure[component[0]].signals[component[1]]:
                    component[2] = "INPUT"
                else:
                    component[2] = "OUTPUT"
    # add power domain
    if pd0_components:
        logger.debug("Creating extra power_domain PD_GEN")
        pms_structure.add_power_domain("PD_GEN", pd0_components, ["NORMAL"])
    # power modes
    parser = symbol_variable + symbol_equals + pp.Literal("PM").suppress() + symbol_parentheses1 + symbol_func + \
        pp.Optional(symbol_func_more) + symbol_parentheses2
    power_modes = parser.searchString(module_string).asList()
    logger.debug("Found power_models: %s", power_modes)
    for power_mode in power_modes:
        counter = 1
        for pd in founded_pd:
            pms_structure.add_power_mode(power_mode[0], pd, power_mode[counter])
            counter += 1
        if pd0_components:
            # if PD_0 exists we need add to power mode
            pms_structure.add_power_mode(power_mode[0], "PD_GEN", "NORMAL")
    return pms_structure


def comment_remover(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " "  # note: a space and not an empty string
        else:
            return s

    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)


def analyze_file_obj(file_folder, file_obj, file_name):
    logger.info("analyze file %s", file_name)
    # generate empty pms
    pms = None
    # read and clean file_obj
    full_file = ""
    for line in file_obj:
        if not line.isspace():
            full_file += line
    # remove unnecessary comments
    full_file = comment_remover(full_file)
    block_regex = re.compile(r'(SC_MODULE|SC_CTOR|\{|\})', re.IGNORECASE)
    sc_module_count = -1
    for regex_match in block_regex.finditer(full_file):
        if regex_match.group(0) == "SC_MODULE":
            start_point = regex_match.start()
            continue
        if regex_match.group(0) == "SC_CTOR":
            sc_module_count = 0
            continue
        if sc_module_count >= 0 and regex_match.group(0) == r'{':
            sc_module_count += 1
            continue
        if sc_module_count >= 0 and regex_match.group(0) == r'}':
            sc_module_count -= 1
        if sc_module_count == 0:
            sc_module_count = -1
            end_point = regex_match.start()
            # call function
            pms_name = os.path.basename(file_name)
            pms_name = os.path.splitext(pms_name)[0]
            pms = analyze_module(full_file[start_point:end_point + 1], pms_name, file_folder, _find_includes(full_file))
            break
    if not pms:
        logger.info("No SC_MODULE or SC_CTOR in file %s", file_name)
    return pms
