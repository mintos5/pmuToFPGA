import json


class PMSConf:
    def __init__(self, name="pms_conf_0", levels=None, power_domains=None, signals=None, components=None, power_modes=None):
        self.name = name
        if levels is None:
            self.levels = {}
        else:
            self.levels = levels
        if power_domains is None:
            self.power_domains = {}
        else:
            self.power_domains = power_domains
        if signals is None:
            self.signals = {}
        else:
            self.signals = signals
        if components is None:
            self.components = {}
        else:
            self.components = components
        if power_modes is None:
            self.power_modes = {}
        else:
            self.power_modes = power_modes

    def __str__(self):
        return self.to_json(indent=2)

    def add_level(self, name, frequency, voltage):
        self.levels[name] = (frequency, voltage)

    def add_power_domain(self, name, components, levels):
        self.power_domains[name] = (components, levels)

    def add_signal(self, name, power_domain, component, component_map, component_type="UNKNOWN"):
        if name not in self.signals:
            self.signals[name] = {power_domain: [[component, component_map, component_type]]}
        else:
            if power_domain not in self.signals[name]:
                self.signals[name][power_domain] = [[component, component_map, component_type]]
            else:
                self.signals[name][power_domain].append([component, component_map, component_type])

    def add_component(self, name, power_domain, component_type):
        self.components[name] = (power_domain, component_type)

    def add_power_mode(self, name, power_domain, level):
        if name not in self.power_modes:
            self.power_modes[name] = [(power_domain, level)]
        else:
            self.power_modes[name].append((power_domain, level))

    def check_power_modes(self):
        for key, value in self.power_modes.items():
            for power_domain in value:
                print(power_domain[0] + "   " + power_domain[1])
                print(self.power_domains[power_domain[0]][1])
                if power_domain[1] not in self.power_domains[power_domain[0]][1]:
                    return False
        return True

    def clean_levels(self, remove):
        levels_removed = False
        correct_levels = []
        for pd, pd_value in self.power_domains.items():
            correct_levels.extend(pd_value[1])
        for key in list(self.levels.keys()):
                if key not in correct_levels:
                    levels_removed = True
                    if remove:
                        del self.levels[key]
        return levels_removed

    def to_json(self, indent):
        return json.dumps(self,default=convert_to_dict,indent=indent)

    @staticmethod
    def from_json(json_string):
        return json.loads(json_string,object_hook=dict_to_obj)


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
        obj = PMSConf(**our_dict)
    else:
        obj = our_dict
    return obj


class FreqSet:
    def __init__(self, name, volt_freq, pll=False, main_freq=True, zero=False, divide_from_pll=False):
        self.name = name
        self.pll = pll
        self.main_freq_bool = main_freq
        self.zero = zero
        self.divide_from_pll = divide_from_pll
        self.voltage = volt_freq[0]
        self.frequency = volt_freq[1]
        self.position = 0

        self.fout = 0
        self.divr = 0
        self.divf = 0
        self.divq = 0
        self.divide_number = -1
        self.divide_number_size = 0

    def __str__(self):
        return self.name + " " + str(self.frequency)

    def __repr__(self):
        return self.name + " " + str(self.frequency)


class ComponentSet:
    def __init__(self, comp_type, done=False, signals=None):
        self.type = comp_type
        self.done = done
        if signals is None:
            self.signals = {}
        else:
            self.signals = signals
