from structs.pms import PMSConf, PmuInfo
from structs.pms import FreqSet
from structs.device import DeviceConf
from mako.template import Template
from mako.runtime import Context
from mako.lookup import TemplateLookup
from io import StringIO
import re
import math
import logging

logger = logging.getLogger(__name__)

def _insert_string(mystring, position, chartoinsert):
    mystring = mystring[:position] + chartoinsert + mystring[position:]
    return mystring


def get_pll_specs(freq_setting: FreqSet, device: DeviceConf):
    # check main_freq
    if device.clk_freq < device.pll_clk_in_min or device.clk_freq > device.pll_clk_in_max:
        logger.error("Input frequency is out of band, fall_backing to main_clock")
        return False
    else:
        if freq_setting.frequency < device.pll_clk_out_min or freq_setting.frequency > device.pll_clk_out_max:
            logger.error("Output frequency is out of band, fall_backing to main_clock")
            return False
        else:
            # calculate the freq
            found_something = False
            best_fout = 0
            for divr in range(16):
                f_pfd = device.clk_freq / (divr + 1)
                if f_pfd < 10 or f_pfd > 133:
                    continue
                for divf in range(128):
                    f_vco = f_pfd * (divf + 1)
                    if f_vco < 533 or f_vco > 1066:
                        continue
                    for divq in range(1, 7):
                        fout = f_vco * math.pow(2, -divq)
                        if math.fabs(fout - freq_setting.frequency) < math.fabs(
                                best_fout - freq_setting.frequency) or not found_something:
                            best_fout = fout
                            best_divr = divr
                            best_divf = divf
                            best_divq = divq
                            found_something = True
            if device.accepted_freq == 0:
                if freq_setting.frequency != best_fout:
                    logger.error("Can not achieve desired frequency for PLL")
                    return False
                else:
                    logger.debug("Achieved desired frequency")
            else:
                if freq_setting.frequency - (
                        freq_setting.frequency / device.accepted_freq) < best_fout > freq_setting.frequency + (
                        freq_setting.frequency / device.accepted_freq):
                    logger.debug("Achieved desired frequency for PLL in threshold")
                else:
                    logger.error("Can not achieve desired frequency for PLL with set threshold")
                    return False
            freq_setting.pll = True
            freq_setting.main_freq_bool = False
            freq_setting.fout = best_fout
            freq_setting.divr = best_divr
            freq_setting.divf = best_divf
            freq_setting.divq = best_divq
            return True


def get_divide_specs(freq_setting: FreqSet, device: DeviceConf, input_freq):
    if freq_setting.frequency > input_freq:
        logger.error("Output frequency is too big, fall_backing to main_clock")
        return False
    else:
        quotient = input_freq/freq_setting.frequency
        # check if quotient is even
        if (quotient % 2) == 0:
            logger.debug("quotient [%s] is OK", str(quotient))
        else:
            if device.accepted_freq == 0:
                logger.error("Can not achieve desired frequency for custom divider")
                return False
            else:
                logger.warning("quotient [%s] is not OK", str(quotient))
                quotient1 = quotient - (quotient % 2)
                quotient2 = quotient + (2 - (quotient % 2))
                if math.fabs(freq_setting.frequency - input_freq / quotient1) < math.fabs(
                        freq_setting.frequency - input_freq / quotient2):
                    # quotient1 is better
                    quotient = quotient1
                else:
                    # quotient2 is better
                    quotient = quotient2
                # test resulted frequency if in threshold
                if freq_setting.frequency - (
                        freq_setting.frequency / device.accepted_freq) < input_freq / quotient > freq_setting.frequency + (
                        freq_setting.frequency / device.accepted_freq):
                    logger.debug("Achieved desired frequency for custom divider in threshold")
                else:
                    logger.error("Can not achieve desired frequency for custom divider with set threshold")
                    return False
        divide_number = (quotient/2)-1
        freq_setting.main_freq_bool = False
        freq_setting.divide_number = int(divide_number)
        freq_setting.divide_number_size = int(divide_number).bit_length()
        return True


def get_levels(pms_structure: PMSConf, device: DeviceConf):
    pms_structure.clean_levels(True)
    levels_list = []
    for key, value in pms_structure.levels.items():
        level = FreqSet(key, value)
        levels_list.append(level)

    def sort_by_freq(item: FreqSet):
        return item.frequency

    levels_list.sort(reverse=True, key=sort_by_freq)

    # try to use main_freq
    pll_used = False
    pll_freq = 0
    for freq in levels_list:
        if freq.frequency == device.clk_freq:
            freq.main_freq_bool = True
        elif freq.frequency == 0:
            freq.zero = True
        else:
            if not pll_used:
                if get_pll_specs(freq, device):
                    pll_freq = freq.fout
                    pll_used = True
                else:
                    get_divide_specs(freq, device, device.clk_freq)
            else:
                if get_divide_specs(freq, device, device.clk_freq):
                    pass
                else:
                    if device.divide_pll:
                        freq.divide_from_pll = True
                        get_divide_specs(freq, device, pll_freq)

    return levels_list


def get_power_domains(pms_structure: PMSConf, device: DeviceConf):
    processed_pd = []
    for key, value in pms_structure.power_domains.items():
        freq_count = len(value[1])
        freq_count_size = int(freq_count-1).bit_length()
        if freq_count_size == 0:
            freq_count_size = 1
        logger.debug("processed_pd append: %s", value[1])
        processed_pd.append((freq_count, freq_count_size, value[1]))
    return processed_pd


def get_power_modes(pms_structure: PMSConf, device: DeviceConf, levels):
    processed_pm = []
    for key, value in pms_structure.power_modes.items():
        processed_pd = []
        for pd in value:
            if device.strict_freq:
                # find the position on power_domain
                if pd[1] in pms_structure.power_domains[pd[0]][1]:
                    position = pms_structure.power_domains[pd[0]][1].index(pd[1])
                    processed_pd.append(position)
            else:
                # find the position in levels
                for level_num in range(len(levels)):
                    if levels[level_num].name == pd[1]:
                        position = level_num
                        processed_pd.append(position)
                        break
        processed_pm.append((key, processed_pd))
    return processed_pm


def get_combined_levels(levels, pds):
    combined_levels = []
    for pd_num in range(len(pds)):
        for pd_level_num in range(pds[pd_num][0]):
            for level_num in range(len(levels)):
                if levels[level_num].name == pds[pd_num][2][pd_level_num]:
                    if levels[level_num].pll:
                        combined_levels.append((pd_num, pd_level_num, level_num))
                        continue
                    if levels[level_num].main_freq_bool and not levels[level_num].zero:
                        combined_levels.append((pd_num, pd_level_num, level_num))
                        continue
                    if levels[level_num].divide_number > 0 and not levels[level_num].zero:
                        combined_levels.append((pd_num, pd_level_num, level_num))
                        continue
    return combined_levels


def generate_pmu_verilog(pms_structure: PMSConf, device: DeviceConf, pmu_info: PmuInfo):
    processed_levels = get_levels(pms_structure, device)
    processed_levels_bitsize = int(len(processed_levels) - 1).bit_length()
    if processed_levels_bitsize == 0:
        processed_levels_bitsize = 1
    logger.debug("Processed levels: %s", processed_levels)
    # just array of FreqSet objects

    processed_pd = get_power_domains(pms_structure, device)
    processed_pd_bitsize = int(len(processed_pd)-1).bit_length()
    if processed_pd_bitsize == 0:
        processed_pd_bitsize = 1
    # array of tuples(number of freq for power_domain, number of bits for previous number, list of supported freq)

    processed_pm = get_power_modes(pms_structure, device, processed_levels)
    processed_pm_bitsize = int(len(processed_pm) - 1).bit_length()
    if processed_pm_bitsize == 0:
        processed_pm_bitsize = 1
    # array of tuples(name of power_mode, array of level positions)

    combined_levels = get_combined_levels(processed_levels, processed_pd)
    # array of tuples(number of power_domain, his own position of level, global position of level)

    pmu_info.levels_bitsize = processed_levels_bitsize
    pmu_info.pds_bitsize = processed_pd_bitsize
    pmu_info.pms_bitsize = processed_pm_bitsize

    processed_data = {}
    processed_data["levels"] = processed_levels
    processed_data["levels_bitsize"] = processed_levels_bitsize
    processed_data["pds"] = processed_pd
    processed_data["pds_bitsize"] = processed_pd_bitsize
    processed_data["pms"] = processed_pm
    processed_data["pms_bitsize"] = processed_pm_bitsize
    processed_data["combined_levels"] = combined_levels
    processed_data["use_pll"] = device.use_pll
    processed_data["divide_clock"] = device.divide_clock
    processed_data["divide_pll"] = device.divide_pll
    processed_data["ice40_reconfiguration"] = device.ice40_reconfiguration
    processed_data["ice40_confs"] = device.ice40_confs
    processed_data["strict_freq"] = device.strict_freq
    processed_data["all_freq"] = device.all_freq
    processed_data["pmu_type"] = device.pmu_type

    mylookup = TemplateLookup(directories=['data'])
    mytemplate = mylookup.get_template("pmu_inner.mako")
    buf = StringIO()
    ctx = Context(buf, **processed_data)
    mytemplate.render_context(ctx)
    return buf


def apply_pmu(top, pms_structure: PMSConf, device: DeviceConf, pmu_info: PmuInfo):
    top_string = top.read()
    # add includes:
    includes ='''`include "power/pmu.v"
`include "power/cross_bus.v"
`include "power/cross_flag.v"
'''
    top_string = _insert_string(top_string, 0, includes)
    # find the begin of the module
    module_regex = re.compile(r'module top.*?\(.*?\);', re.IGNORECASE | re.DOTALL)
    module = re.search(module_regex, top_string)
    if module:
        # generate clock buffers
        mylookup = TemplateLookup(directories=['data'])
        if device.use_explicit_clock_buffers:
            mytemplate = mylookup.get_template("global_buffer_template.mako")
            context_data = {}
            context_data["pmu_type"] = device.pmu_type
            context_data["num_clocks"] = len(pms_structure.power_domains.items())
            buf = StringIO()
            ctx = Context(buf, **context_data)
            mytemplate.render_context(ctx)
            top_string = _insert_string(top_string, module.end(), buf.getvalue())

        # generate PMU
        mytemplate = mylookup.get_template("pmu_template.mako")
        context_data = {}
        context_data["pmu_type"] = device.pmu_type
        context_data["num_clocks"] = len(pms_structure.power_domains.items())
        context_data["sync_control"] = device.sync_control

        buf = StringIO()
        ctx = Context(buf, **context_data)
        mytemplate.render_context(ctx)
        top_string = _insert_string(top_string, module.end(), buf.getvalue())

        # generate synchronizer for PMU
        if device.sync_control:
            if device.pmu_type == "LEVELS" or device.pmu_type == "COMBINED":
                mytemplate = mylookup.get_template("cross_bus_template.mako")
                context_data = {}
                context_data["notes"] = "clkA should be PMU clock, clkB should be clock of controlling component"
                context_data["bus_size"] = pmu_info.pds_bitsize + pmu_info.levels_bitsize
                context_data["cross_bus"] = "level_sync"
                context_data["bus_out_b"] = "level_synced"
                context_data["flag_out_b"] = "level_flag_synced"
                buf = StringIO()
                ctx = Context(buf, **context_data)
                mytemplate.render_context(ctx)
                top_string = _insert_string(top_string, module.end(), buf.getvalue())
            if device.pmu_type == "POWER_MODES" or device.pmu_type == "COMBINED":
                mytemplate = mylookup.get_template("cross_bus_template.mako")
                context_data = {}
                context_data["notes"] = "clkA should be PMU clock, clkB should be clock of controlling component"
                context_data["bus_size"] = pmu_info.pms_bitsize
                context_data["cross_bus"] = "power_sync"
                context_data["bus_out_b"] = "power_mode_synced"
                context_data["flag_out_b"] = "power_mode_flag_synced"
                buf = StringIO()
                ctx = Context(buf, **context_data)
                mytemplate.render_context(ctx)
                top_string = _insert_string(top_string, module.end(), buf.getvalue())

        pd_position = -1
        # generate list of power_domains, to have correct number
        power_domains = list(pms_structure.power_domains.keys())
        # find signals with multiple power_domains
        for key, value in pms_structure.signals.items():
            if len(value) > 1:
                # find out type of signal
                signal_regex = re.compile(r'wire \[(\d*):\d*\].*'+key+r'.*;', re.IGNORECASE)
                signal_size = re.search(signal_regex, top_string)
                sync_size = 0
                if signal_size:
                    sync_size = int(signal_size.group(1))
                    logger.debug("Signal: %s is %d bit long", key, sync_size)
                # nahradime texty
                producer_pds = []
                first_pd = None
                for pd, components in value.items():
                    if not first_pd:
                        first_pd = pd
                    for component in components:
                        outputing_component = False
                        if component[2] == "OUTPUT":
                            outputing_component = True
                    if outputing_component:
                        producer_pds.append(pd)
                if len(producer_pds) > 1:
                    logger.info("There are multiple output components in power_domain: %s", pd)
                if len(producer_pds) <= 0:
                    logger.warning("There are 0 output components in power_domains: %s ", pd)
                    producer_pds.append(first_pd)
                    logger.debug("Fixing with first as outputing component")
                counter = -1
                for pd, components in value.items():
                    # do not generate for outputing components
                    if pd in producer_pds:
                        continue
                    counter += 1
                    # loop through components and change output signal
                    for component in components:
                        if component[2] == "INPUT" or component[2] == "UNKNOWN":
                            component_regex = re.compile(r'(' + component[0] + r'[\n ]*\(.*?)(' + key + r')(.*?\);)', re.DOTALL)
                            test = re.search(component_regex, top_string)
                            top_string = re.sub(component_regex, r'\1\2_synced_' + str(counter) + r'\3', top_string)
                    for producer_pd in producer_pds:
                        # create sync_component
                        if sync_size > 1:
                            # create bus
                            mytemplate = mylookup.get_template("cross_bus_template.mako")
                            context_data = {}
                            context_data["bus_size"] = sync_size
                            context_data["cross_bus"] = key + "_" + producer_pd + "_" + pd
                            pd_position = -1
                            if producer_pd in power_domains:
                                pd_position = power_domains.index(producer_pd)
                            if device.use_explicit_clock_buffers:
                                context_data["clock_a"] = "gb_pd_clk_" + str(pd_position)
                            else:
                                context_data["clock_a"] = "pd_clk_" + str(pd_position)
                            if pd in power_domains:
                                pd_position = power_domains.index(pd)
                            if device.use_explicit_clock_buffers:
                                context_data["clock_b"] = "gb_pd_clk_" + str(pd_position)
                            else:
                                context_data["clock_b"] = "pd_clk_" + str(pd_position)
                            context_data["bus_in_a"] = key
                            context_data["bus_out_b"] = key + "_synced_" + str(counter)
                            buf = StringIO()
                            ctx = Context(buf, **context_data)
                            mytemplate.render_context(ctx)
                            top_string = _insert_string(top_string, module.end(), buf.getvalue())
                        else:
                            # just flag
                            mytemplate = mylookup.get_template("cross_flag_template.mako")
                            context_data = {}
                            context_data["cross_flag"] = key + "_" + producer_pd + "_" + pd
                            pd_position = -1
                            if producer_pd in power_domains:
                                pd_position = power_domains.index(producer_pd)
                            if device.use_explicit_clock_buffers:
                                context_data["clock_a"] = "gb_pd_clk_" + str(pd_position)
                            else:
                                context_data["clock_a"] = "pd_clk_" + str(pd_position)
                            if pd in power_domains:
                                pd_position = power_domains.index(pd)
                            if device.use_explicit_clock_buffers:
                                context_data["clock_b"] = "gb_pd_clk_" + str(pd_position)
                            else:
                                context_data["clock_b"] = "pd_clk_" + str(pd_position)
                            context_data["flag_a"] = key
                            context_data["flag_out_b"] = key + "_synced_" + str(counter)
                            buf = StringIO()
                            ctx = Context(buf, **context_data)
                            mytemplate.render_context(ctx)
                            top_string = _insert_string(top_string, module.end(), buf.getvalue())
    return top_string
