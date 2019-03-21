from structs.pms import PMSConf
from structs.pms import FreqSet
from structs.device import DeviceConf
from mako.template import Template
from mako.runtime import Context
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
            freq_setting.fout = best_fout
            freq_setting.divr = best_divr
            freq_setting.divf = best_divf
            freq_setting.divq = best_divq
            return True


def get_divide_specs(freq_setting: FreqSet, device: DeviceConf):
    if freq_setting.frequency > device.clk_freq:
        print("ERROR")
        return False
    else:
        quotient = device.clk_freq/freq_setting.frequency
        # check if quotient is even
        if (quotient % 2) == 0:
            print("OK")
        else:
            print("ERROR")
            quotient -= 1
        divide_number = (quotient/2)-1
        freq_setting.divide_number = divide_number
        freq_setting.divide_number_size = int((math.log(divide_number) / math.log(2)) + 1)


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
    freq_counter = 0
    pll_used = False
    zero_used = False
    for freq in levels_list:
        if freq.frequency == device.clk_freq:
            freq.main_freq_bool = True
        elif freq.frequency == 0:
            zero_used = True
            freq.zero = True
        else:
            freq_counter += 1
            if not pll_used:
                if get_pll_specs(freq, device):
                    pll_used = True
                else:
                    get_divide_specs(freq, device)
            else:
                get_divide_specs(freq)
    # add slot for using main_clock
    if pll_used:
        freq_counter += 1
    if zero_used:
        freq_counter += 1
    freq_counter_size = int((math.log(freq_counter) / math.log(2)) + 1)
    return freq_counter, freq_counter_size, levels_list


def generate_verilog():
    mytemplate = Template(filename='data/cross_bus_template')
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
