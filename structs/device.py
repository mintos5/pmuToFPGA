from enum import Enum
import json


class DeviceConf:
    def __init__(self, name="dev_conf_0", clk_freq=12, device_type="ice40", use_pll=True, pmu_type="COMBINED",
                 pll_clk_in_min=10, pll_clk_in_max=133, pll_clk_out_min=16, pll_clk_out_max=275, divide_clock=True,
                 divide_pll=False, use_explicit_clock_buffers=False, strict_freq=False, all_freq=False,
                 ice40_reconfiguration=True, ice40_confs=[False, False, False, False], sync_control=False,
                 accepted_freq=0):
        self.name = name
        self.clk_freq = clk_freq
        self.device_type = device_type
        self.use_pll = use_pll
        self.pmu_type = pmu_type
        self.pll_clk_in_min = pll_clk_in_min
        self.pll_clk_in_max = pll_clk_in_max
        self.pll_clk_out_min = pll_clk_out_min
        self.pll_clk_out_max = pll_clk_out_max
        self.divide_clock = divide_clock
        self.divide_pll = divide_pll
        self.use_explicit_clock_buffers = use_explicit_clock_buffers
        self.strict_freq = strict_freq
        self.all_freq = all_freq
        self.ice40_reconfiguration = ice40_reconfiguration
        self.ice40_confs = ice40_confs
        self.sync_control = sync_control
        self.accepted_freq = accepted_freq

    def to_json(self, indent):
        return json.dumps(self, default=convert_to_dict, indent=indent)

    def update(self, newdata):
        for key, value in newdata.items():
            setattr(self, key, value)

    @staticmethod
    def from_json(json_string):
        return json.loads(json_string, object_hook=dict_to_obj)


def convert_to_dict(obj):
    """
    From: https://medium.com/python-pandemonium/json-the-python-way-91aac95d4041
    A function takes in a custom object and returns a dictionary representation of the object.
    This dict representation includes meta data such as the object's module and class names.
    """

    #  Populate the dictionary with object meta data
    obj_dict = {
        "__class__": obj.__class__.__name__,
        "__module__": obj.__module__
    }

    #  Populate the dictionary with object properties
    obj_dict.update(obj.__dict__)

    return obj_dict


def dict_to_obj(our_dict):
    """
    From: https://medium.com/python-pandemonium/json-the-python-way-91aac95d4041
    Function that takes in a dict and returns a custom object associated with the dict.
    This function makes use of the "__module__" and "__class__" metadata in the dictionary
    to know which object type to create.
    """
    if "__class__" in our_dict:
        # Pop ensures we remove metadata from the dict to leave only the instance arguments
        class_name = our_dict.pop("__class__")

        # Get the module name from the dict and import it
        module_name = our_dict.pop("__module__")



        # Use dictionary unpacking to initialize the object
        obj = DeviceConf(**our_dict)
    else:
        obj = our_dict
    return obj