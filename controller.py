import logging
import sys
import os
import re

import analyzer
import generator
from structs.device import DeviceConf
from structs.pms import PMSConf

logger = logging.getLogger(__name__)


def test_output(output_file, data_out):
    if not output_file:
        logger.error("Missing output file [%s]", output_file)
    elif output_file is sys.stdout:
        sys.stdout.write(data_out)
    else:
        try:
            file_obj = open(output_file, "w+")
        except IOError:
            logger.error("Output file problem")
        with file_obj:
            file_obj.write(data_out)


def analyze_test(input_file, output_file):
    if not input_file:
        logger.error("Missing input SystemC/PMS file [%s]", input_file)
    elif input_file is sys.stdin:
        pms_structure = analyzer.analyze_file_obj(os.getcwd(), input_file, "stdin")
        if pms_structure:
            test_output(output_file, pms_structure.to_json(4))
    else:
        # check if folder or file
        if os.path.isfile(input_file):
            file_directory = os.path.dirname(input_file)
            try:
                file_obj = open(input_file, "r")
            except IOError:
                logger.error("FILE problem")
            with file_obj:
                pms_structure = analyzer.analyze_file_obj(file_directory, file_obj, input_file)
                if pms_structure:
                    test_output(output_file, pms_structure.to_json(4))
        elif os.path.isdir(input_file):
            founded_file = False
            for file in os.listdir(input_file):
                if founded_file:
                    break
                good_file = re.search(r'.*\.(cpp|c|h)$', file)
                if good_file:
                    try:
                        file_obj = open(os.path.join(input_file, file), "r")
                    except IOError:
                        logger.error("FILE problem")
                    with file_obj:
                        pms_structure = analyzer.analyze_file_obj(input_file, file_obj, file)
                        if pms_structure:
                            test_output(output_file, pms_structure.to_json(4))
                            founded_file = True
            else:
                logger.error("No PMS structure found in directory %s", input_file)
        else:
            logger.error("Input file does not exists")


def generate_test(input_file, output_file, template_file, device_setting):
    pass


def run_test(input_file, output_file, template_file, device_setting):
    pass


def run_test(input_file, output_file, template_file, device_setting):
    pass


def create_test(output_file):
    pass



def test_01():
    whaat = analyzer.analyze_file_obj("data/", "pms_test.cpp")
    generator.generate_verilog(whaat, DeviceConf())


def test_02():
    generator.generate_verilog()


def test_03():
    generator.test_struct()

def test_04():
    logger.warning("WSDSD")


def main():
    test_01()
    # test_02()
    # test_03()

if __name__ == "__main__":
    main()
