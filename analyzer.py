from structs.pms import PMSConf
import re
import pyparsing as pp
import os


# simple comments remover
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


def analyze_file(file_name):
    # read and clean file_obj
    full_file = ""
    with open(file_name, "r") as file_obj:
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
            print(full_file[start_point:end_point + 1])
            pms_name = os.path.basename(file_name)
            pms_name = os.path.splitext(pms_name)[0]
            pms = analyze_module(full_file[start_point:end_point + 1], pms_name)
            break
    return pms


def analyze_module(module_string, pms_name):
    # generate structure
    pms_structure = PMSConf(pms_name)
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
        print(match)
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
        print(match)
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
        power_domain_levels = power_domain_levels[0]
        print(power_domain_levels)
        power_add_component = pp.Literal(".AddComponent").suppress()
        parser = power_domain + power_add_component + symbol_parentheses1 + symbol_quotes + symbol_variable + \
                         symbol_quotes + symbol_parentheses2
        power_domain_components = []
        for component in parser.scanString(module_string):
            power_domain_components.extend(component[0])
        print(power_domain_components)
        pms_structure.add_power_domain(pd, power_domain_components, power_domain_levels)
        for component in power_domain_components:
            pms_structure.add_component(component, pd)

    # find signals
    signal1 = pp.Literal("sc_signal<")
    signal12 = pp.Word(pp.alphanums)
    signal2 = pp.Literal(">")
    signal_name = pp.Suppress(pp.Combine(signal1 + signal12 + signal2))
    parser = signal_name + symbol_variable + pp.Optional(symbol_variable_more)
    founded_signals = []
    for match in parser.scanString(module_string):
        print(match)
        founded_signals.extend(match[0])

    component_name = pp.Word(pp.alphanums + '_')
    component_function = pp.Literal(".").suppress() + pp.Word(pp.alphanums + '_').suppress() + symbol_parentheses1
    print("SIGNAL")
    # bind signals to components and power_domains
    pd0_components = []
    for signal in founded_signals:
        parser = component_name + component_function + pp.Literal(signal) + symbol_parentheses2;
        for match in parser.scanString(module_string):
            component = match[0][0]
            connected_signal = match[0][1]
            if component in pms_structure.components:
                pms_structure.add_signal(connected_signal, pms_structure.components[component], component)
            else:
                # add virtual power_domain
                print("found signal with component without power_domain")
                pd0_components.append(component)
                pms_structure.add_component(component, "PD0")
                pms_structure.add_signal(connected_signal, "PD0", component)
    if pd0_components:
        pms_structure.add_power_domain("PD0", pd0_components, ["NORMAL"])
    # power modes
    parser = symbol_variable + symbol_equals + pp.Literal("PM").suppress() + symbol_parentheses1 + symbol_func + \
        pp.Optional(symbol_func_more) + symbol_parentheses2
    power_modes = parser.searchString(module_string).asList()
    print(power_modes)
    for power_mode in power_modes:
        counter = 1
        for pd in founded_pd:
            pms_structure.add_power_mode(power_mode[0], pd, power_mode[counter])
            counter += 1
    print(pms_structure)

    return pms_structure
