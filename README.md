# pmuToFPGA

* Simple python tool to analyze SystemC/PMS code
* From analyzed data this tool can create simple verilog module (PMU) which can create multiple clock domains
* This module can be appended to other top verilog code
* Small GUI created in Qt for simpler control

## Requirements

* Python 3.7
* pip3 install pyparsing
* pip3 install Mako
* pip3 install PyQt5

## Usage
```
Usage: cli.py [options] [function-options]

Options:
  -h, --help            show this help message and exit
  -v, --version         show program version and exit
  -i INPUT, --input=INPUT
                        choose the input file/directory for SystemC/PMS or
                        JSON structure [default: stdin]
  -t TEMPLATE, --template=TEMPLATE
                        choose the template from which the verilog top code
                        will be generated
  -o OUTPUT, --output=OUTPUT
                        choose the output directory [default: stdout]
  -d DEVICE, --device=DEVICE
                        choose the json device config [default: auto_ice40]
  -l LOG, --log=LOG     choose the log output [default: stdout]
  -m LOG_MODE, --log-mode=LOG_MODE
                        log mode: DEBUG, INFO, WARNING, ERROR [default: INFO]

  Function Options:
    Options to choose what to do

    -a, --analyze       analyze FILE (SystemC/PMS) and create OUTPUT (JSON)
    -g, --generate      analyze FILE (JSON) and create OUTPUT (Verilog)
    -r, --run           analyze FILE (SystemC/PMS) and create OUTPUT (Verilog)
                        [default]
    -c, --create-conf   create OUTPUT (default JSON device config)
```

## Examples
* Analyze SystemC/PMS
```
python3 clip.py -a -i examples/pms_test.cpp -o export/pms_struct.json
```
* Create verilog PMU and append to verilog template
```
python3 clip.py -r -i examples/pms_test.cpp -o export/pms_struct.json -t examples/top.v
```