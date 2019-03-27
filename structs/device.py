from enum import Enum


class PmuType(Enum):
    LEVELS, POWER_MODES, COMBINED = range(3)


class DeviceConf:
    def __init__(self, name="dev_conf_0"):
        self.name = name
        self.clk_freq = 12
        self.device_type = "ice40"
        self.use_pll = True
        self.pmu_type = PmuType.COMBINED
        self.pll_clk_in_min = 10
        self.pll_clk_in_max = 133
        self.pll_clk_out_min = 16
        self.pll_clk_out_max = 275
        self.divide_clock = True
        self.divide_pll = False
        self.use_explicit_clock_buffers = False
        self.strict_freq = False
        self.all_freq = True
        self.ice40_reconfiguration = True
        self.ice40_confs = [False, True, False, False]
