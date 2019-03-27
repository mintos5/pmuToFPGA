from structs.pms import PMSConf
from structs.pms import FreqSet
from structs.device import DeviceConf
from mako.template import Template
from mako.runtime import Context
from mako.lookup import TemplateLookup
from io import StringIO
import math


def get_pll_specs(freq_setting: FreqSet, device: DeviceConf):
    # check main_freq
    if device.clk_freq < device.pll_clk_in_min or device.clk_freq > device.pll_clk_in_max:
        print("ERROR")
        return False
    else:
        if freq_setting.frequency < device.pll_clk_out_min or freq_setting.frequency > device.pll_clk_out_max:
            print("ERROR")
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
            # todo check if is the corect or just simmiliar
            freq_setting.pll = True
            freq_setting.main_freq_bool = False
            freq_setting.fout = best_fout
            freq_setting.divr = best_divr
            freq_setting.divf = best_divf
            freq_setting.divq = best_divq
            return True


def get_divide_specs(freq_setting: FreqSet, input_freq):
    if freq_setting.frequency > input_freq:
        print("ERROR")
        return False
    else:
        quotient = input_freq/freq_setting.frequency
        # check if quotient is even
        if (quotient % 2) == 0:
            print("OK")
        else:
            print("ERROR")
            quotient -= 1
        divide_number = (quotient/2)-1
        freq_setting.main_freq_bool = False
        freq_setting.divide_number = divide_number
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
                    get_divide_specs(freq, device.clk_freq)
            else:
                if get_divide_specs(freq, device.clk_freq):
                    pass
                else:
                    if device.divide_pll:
                        freq.divide_from_pll = True
                        get_divide_specs(freq, pll_freq)

    return levels_list


def test_generate(configuration):
    mylookup = TemplateLookup(directories=['data'])
    mytemplate = mylookup.get_template("pmu_inner.mako")
    buf = StringIO()
    ctx = Context(buf, **configuration)
    mytemplate.render_context(ctx)
    print(buf.getvalue())
    # sem bude spracovanie kam to pojde....


def get_power_domains(pms_structure: PMSConf, device: DeviceConf):
    processed_pd = []
    for key, value in pms_structure.power_domains.items():
        print(value[1])
        freq_count = len(value[1])
        freq_count_size = int(freq_count-1).bit_length()
        if freq_count_size == 0:
            freq_count_size = 1
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
                #find the position in levels
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


def generate_verilog2(pms_structure: PMSConf, device: DeviceConf):
    # tu uz budu len ciste data...
    processed_levels = get_levels(pms_structure, device)
    processed_levels_bitsize = int(len(processed_levels) - 1).bit_length()
    if processed_levels_bitsize == 0:
        processed_levels_bitsize = 1
    print(processed_levels)
    # just array of FreqSet objects

    processed_pd = get_power_domains(pms_structure, device)
    processed_pd_bitsize = int(len(processed_pd)-1).bit_length()
    if processed_pd_bitsize == 0:
        processed_pd_bitsize = 1
    # array of tuples(number of freq for power_domain, number of bits for previous number, list of supported freq)

    device.strict_freq = True
    device.all_freq = False

    processed_pm = get_power_modes(pms_structure, device, processed_levels)
    processed_pm_bitsize = int(len(processed_pm) - 1).bit_length()
    if processed_pm_bitsize == 0:
        processed_pm_bitsize = 1
    # array of tuples(name of power_mode, array of level positions)

    combined_levels = get_combined_levels(processed_levels, processed_pd)
    # array of tuples(number of power_domain, his own position of level, global position of level)

    #todo strict_frequencies
    # zistit kolko freq, ma power domain
    # toto je zle, je tam pocet freq a nie power domain....
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

    test_generate(processed_data)

def generate_verilog():
    mytemplate = Template(filename='data/cross_bus_template.mako')
    buf = StringIO()
    ctx = Context(buf, cross_bus="cross_bus_1", clock_a="hodiny_a", reset_a="RESET", flag_a="in_a", busy_out_a="out_a",
                  clock_b="hodiny_b", reset_b="RESET_B", flag_out_b="out_b", bus_in_a="BUS_A", bus_out_b="BUS_B")
    mytemplate.render_context(ctx)
    print(buf.getvalue())


def test_struct():
    test_string = """
{
  "__class__": "PMSConf",
  "__module__": "structs.pms",
  "name": "pms_conf_0",
  "levels": {
    "normal": [
      1222.22,
      122.3
    ],
    "low_power": [
      122,
      55
    ]
  },
  "power_domains": {
    "ahoj": [
      "component1",
      "component2",
      "component2"
    ]
  },
  "signals": {
    "signal1": {
      "ahoj": [
        "comp1",
        "comp2"
      ]
    }
  },
  "components": {
    "component1": "ahoj",
    "component2": "ahoj"
  },
  "power_modes": {
    "on_mode": [
      [
        "ahoj_pd",
        "level"
      ],
      [
        "ahoj_pd2",
        "level223i32"
      ]
    ]
  }
}
"""
    test = PMSConf()
    test.add_level("normal", 1222.22, 122.3)
    test.add_level("low_power", 122, 55)
    test.add_power_domain("ahoj", ["component1", "component2", "component2"])
    test.add_component("component1", "ahoj")
    test.add_component("component2", "ahoj")
    test.add_signal("signal1", "ahoj", ["comp1", "comp2"])
    test.add_power_mode("on_mode", "ahoj_pd", "level")
    test.add_power_mode("on_mode", "ahoj_pd2", "level223")
    print(test)

    newObject = PMSConf.from_json(test_string)
    print(newObject)
