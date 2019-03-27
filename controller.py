import analyzer
import generator
from structs.device import DeviceConf

def test_01():
    whaat = analyzer.analyze_file("data/pms_example.cpp")
    generator.generate_verilog2(whaat, DeviceConf())


def test_02():
    generator.generate_verilog()


def test_03():
    generator.test_struct()


def main():
    test_01()
    # test_02()
    # test_03()

if __name__ == "__main__":
    main()
