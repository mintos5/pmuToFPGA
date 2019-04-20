#!/bin/bash
cpp_array=()
while IFS=  read -r -d $'\0'; do
    cpp_array+=("$REPLY")
done < <(find . -name "pms_*.cpp" -print0 -maxdepth 1)

for cpp in "${cpp_array[@]}"
do
    cpp_name=${cpp##*/}
    cpp_name=${cpp_name%.*}
    echo "Analyzing file: ${cpp}"
    python3 ../../cli.py -a -i ${cpp} -o ${cpp_name}.json -m DEBUG -l ${cpp_name}_log.txt
done

dev_array=()
while IFS=  read -r -d $'\0'; do
    dev_array+=("$REPLY")
done < <(find . -name "dev_*" -print0 -maxdepth 1)

pms_array=()
while IFS=  read -r -d $'\0'; do
    pms_array+=("$REPLY")
done < <(find . -name "pms_*.json" -print0 -maxdepth 1)

for pms in "${pms_array[@]}"
do
	for dev in "${dev_array[@]}"
    do
        out1=${pms##*/}
        out2=${dev##*/}
        out_name=${out1%.*}_${out2%.*}
        echo "Generating test: ${out_name}"
        mkdir -p test_results/${out_name}
        python3 ../../cli.py -g -i ${pms} -d ${dev} -t ../top.v -o test_results/${out_name}/top.v -m DEBUG -l test_results/${out_name}/log.txt
        cd test_results/${out_name}/power
        iverilog -s pmu_tb -o pmu_tb.vvp pmu_tb.v
	    vvp pmu_tb.vvp
	    cd ../../..
	    echo ""
    done
done