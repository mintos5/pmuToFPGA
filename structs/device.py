class DeviceConf:
    def __init__(self, name="dev_conf_0"):
        self.name = name
        self.clk_freq = 12
        self.pll_clk_in_min = 10
        self.pll_clk_in_max = 133
        self.pll_clk_out_min = 16
        self.pll_clk_out_max = 275
