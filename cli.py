import sys
from optparse import OptionParser, OptionGroup
import logging
import controller

logger = logging.getLogger("cli")


class LessThanFilter(logging.Filter):
    def __init__(self, exclusive_maximum, name=""):
        super(LessThanFilter, self).__init__(name)
        self.max_level = exclusive_maximum

    def filter(self, record):
        # non-zero return means we log this message
        return 1 if record.levelno < self.max_level else 0


def _process_options(options):
    # set default logging (stderr)
    root = logging.getLogger()
    root.setLevel(logging.NOTSET)
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

    std_err_handler = logging.StreamHandler(sys.stderr)
    std_err_handler.setLevel(logging.ERROR)
    std_err_handler.setFormatter(formatter)
    # always add std_err_handler
    root.addHandler(std_err_handler)
    # get the logging level and destination
    numeric_level = getattr(logging, options.log_mode.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s. Use DEBUG, INFO, WARNING, ERROR' % options.log_mode)
    if options.log:
        file_handler = logging.FileHandler(options.log)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
    else:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(numeric_level)
        stdout_handler.addFilter(LessThanFilter(logging.ERROR))
        stdout_handler.setFormatter(formatter)
        root.addHandler(stdout_handler)
    # get all possible options
    input_file = sys.stdin
    if options.input:
        input_file = options.input
    output_file = sys.stdout
    if options.output:
        output_file = options.output
    template_file = None
    if options.template:
        template_file = options.template
    device_setting = None
    if options.device:
        device_setting = options.device
    # what to do
    if options.version:
        logger.info("Version: 0.0.1")
        sys.exit(0)
    functions = ["analyze", "generate", "run", "create"]
    function_count = 0
    function = "run"
    for func in functions:
        if options.__dict__[func]:
            function_count += 1
            function = func
    if function_count > 1:
        logger.error("Can not do multiple functions at once, specify only one function option")
        sys.exit(1)
    if function == "analyze":
        controller.analyze(input_file, output_file)
    elif function == "generate":
        controller.generate(input_file, output_file, template_file, device_setting)
    elif function == "run":
        controller.run(input_file, output_file, template_file, device_setting)
    elif function == "create":
        controller.create_default_device(output_file)
    sys.exit(0)


def main():
    usage = "Usage: %prog [options] [function-options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-v", "--version", dest="version", action="store_true",
                      help="show program version and exit")
    parser.add_option("-i", "--input", dest="input",
                      help="choose the input file/directory for SystemC/PMS or JSON structure [default: stdin]")
    parser.add_option("-t", "--template", dest="template",
                      help="choose the template from which the verilog top code will be generated")
    parser.add_option("-o", "--output", dest="output",
                      help="choose the output directory [default: stdout]")
    parser.add_option("-d", "--device", dest="device",
                      help="choose the json device config [default: auto_ice40]",)
    parser.add_option("-l", "--log", dest="log",
                      help="choose the log output [default: stdout]")
    parser.add_option("-m", "--log-mode", dest="log_mode",
                      help="log mode: DEBUG, INFO, WARNING, ERROR [default: %default]", default="INFO")

    group = OptionGroup(parser, "Function Options", "Options to choose what to do")
    group.add_option("-a", "--analyze", dest="analyze", action="store_true",
                      help="analyze FILE (SystemC/PMS) and create OUTPUT (JSON)")
    group.add_option("-g", "--generate", dest="generate", action="store_true",
                     help="analyze FILE (JSON) and create OUTPUT (Verilog)")
    group.add_option("-r", "--run", dest="run", action="store_true",
                     help="analyze FILE (SystemC/PMS) and create OUTPUT (Verilog) [default]")
    group.add_option("-c", "--create-conf", dest="create", action="store_true",
                     help="create OUTPUT (default JSON device config)")
    parser.add_option_group(group)
    if len(sys.argv) == 1:
        # sys.argv.append("-h")
        pass
    (options, args) = parser.parse_args()
    _process_options(options)


if __name__ == "__main__":
    main()

