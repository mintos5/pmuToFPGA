import logging
import sys
import os
import re
import shutil

import analyzer
import generator
from structs.device import DeviceConf
from structs.pms import PMSConf, PmuInfo

logger = logging.getLogger(__name__)


def _test_output(output_file, data_out):
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
            logger.info("Writing to file %s", output_file)


def _test_output_cp(file_to_copy, output_file, to_folder):
    if not output_file:
        logger.error("Missing output file [%s]", output_file)
    elif output_file is sys.stdout:
        logger.info("Printing file %s to stdout", file_to_copy)
        try:
            file_obj = open(file_to_copy, "r")
        except IOError:
            logger.error("FILE %s can not be opened", file_to_copy)
        with file_obj:
            sys.stdout.write(file_obj.read())
    else:
        file_directory = os.path.dirname(output_file)
        file_directory = os.path.join(file_directory, to_folder)
        file_name = os.path.basename(file_to_copy)
        try:
            os.mkdir(file_directory)
        except FileExistsError:
            pass
        except OSError:
            logger.error("Cannot create folder [%s]", file_directory)
        try:
            shutil.copyfile(file_to_copy, os.path.join(file_directory, file_name))
            logger.info("Copying file %s", file_to_copy)
        except IOError:
            logger.error("FILE %s can not be created", os.path.join(file_directory, file_name))


def _get_pms_structure(input_file):
    pms_structure = None
    if not input_file:
        logger.error("Missing input SystemC/PMS file [%s]", input_file)
    elif input_file is sys.stdin:
        pms_structure = analyzer.analyze_file_obj(os.getcwd(), input_file, "stdin")
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
                        founded_file = True
            else:
                logger.error("No PMS structure found in directory %s", input_file)
        else:
            logger.error("Input file does not exists")
    return pms_structure


def _get_pms_structure_json(input_file):
    pms_structure = None
    if not input_file:
        logger.error("Missing input json file [%s]", input_file)
    elif input_file is sys.stdin or os.path.isfile(input_file):
        full_file = ""
        if input_file is sys.stdin:
            full_file = sys.stdin.read()
        else:
            try:
                file_obj = open(input_file, "r")
            except IOError:
                logger.error("FILE problem")
            with file_obj:
                full_file = file_obj.read()
        pms_structure = PMSConf.from_json(full_file)
    else:
        logger.error("Input file does not exists")
    return pms_structure


def analyze(input_file, output_file):
    pms_structure = _get_pms_structure(input_file)
    if pms_structure:
        _test_output(output_file, pms_structure.to_json(4))
    else:
        logger.error("Can not create pms_structure")


def generate_with_callback(input_file, output_file, template_file, device_setting, get_pms):
    # generate device_conf always
    device_conf = DeviceConf()
    if not device_setting:
        logger.info("Generating PMU with default device config")
    else:
        if os.path.isfile(device_setting):
            try:
                device_obj = open(device_setting, "r")
            except IOError:
                logger.error("FILE problem")
            full_file = ""
            with device_obj:
                full_file = device_obj.read()
            device_conf = DeviceConf.from_json(full_file)
        else:
            logger.warning("Device config file does not exists, generating with default")
    # get PMS structure
    pms_structure = get_pms(input_file)
    if pms_structure:
        # copy sync_components
        data_folder = os.path.join(os.getcwd(), "data")
        _test_output_cp(os.path.join(data_folder, "cross_flag.v"), output_file, "power")
        _test_output_cp(os.path.join(data_folder, "cross_bus.v"), output_file, "power")
        _test_output_cp(os.path.join(data_folder, "pmu_tb.v"), output_file, "power")
        # generate PMU
        pmu_info = PmuInfo()
        sio = generator.generate_pmu_verilog(pms_structure, device_conf, pmu_info)
        if not output_file:
            logger.error("Missing output file [%s]", output_file)
        elif output_file is sys.stdout:
            logger.info("PMU to stdout")
            _test_output(output_file, sio.getvalue())
        else:
            pmu_output_file = os.path.dirname(output_file)
            pmu_output_file = os.path.join(pmu_output_file, "power")
            pmu_output_file = os.path.join(pmu_output_file, "pmu.v")
            _test_output(pmu_output_file, sio.getvalue())
        # apply PMU to top.v
        if not template_file:
            logger.error("Missing template file [%s]", template_file)
        else:
            try:
                file_obj = open(template_file, "r")
            except IOError:
                logger.error("Template file problem")
            with file_obj:
                processed_top = generator.apply_pmu(file_obj, pms_structure, device_conf, pmu_info)
            _test_output(output_file, processed_top)
        return pms_structure
    else:
        logger.error("Can not generate")
        return None


def generate(input_file, output_file, template_file, device_setting):
    return generate_with_callback(input_file, output_file, template_file, device_setting, _get_pms_structure_json)


def run(input_file, output_file, template_file, device_setting):
    return generate_with_callback(input_file, output_file, template_file, device_setting, _get_pms_structure)


def create_default_device(output_file):
    device_conf = DeviceConf()
    _test_output(output_file, device_conf.to_json(4))


def update_device(input_file, **kwargs):
    device_conf = load_device(input_file)
    device_conf.update(kwargs)
    _test_output(input_file, device_conf.to_json(4))


def load_device(input_file):
    device_conf = DeviceConf()
    if not input_file:
        logger.info("Loading PMU info with default device config")
    else:
        if os.path.isfile(input_file):
            try:
                device_obj = open(input_file, "r")
            except IOError:
                logger.error("FILE problem")
            full_file = ""
            with device_obj:
                full_file = device_obj.read()
            device_conf = DeviceConf.from_json(full_file)
        else:
            logger.warning("Device config file does not exists, loading with default info")
    return device_conf
