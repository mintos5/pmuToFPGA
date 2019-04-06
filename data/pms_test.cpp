#include "systemc.h"
#include  "pms.h"
#include "cpu.h"
#include "rs232.h"

SC_MODULE(Sys){
	sc_signal<data> s1, s2,s3; //internal signals
	sc_signal<data> test, cpu_dout, txValid;
	data BR; //state variable
	PowerDomain PD_1; //declaration of power domain PD_1
	PowerDomain PD_2; //declaration of power domain PD_2
	PowerDomain PD_3; //declaration of power domain PD_2
	PowerMode on_mode; //declaration of power mode on_mode
	PowerMode off_mode;
	cpuType CPU;
	serialType RS232;
	cpuType CPU2;
    /*
    asdasdasd
    asdasdasd
    */
    //asdaasda
	SC_CTOR(Sys) : CPU("CPU"), RS232("RS232"){
		SetLevel(NORMAL, 5V, 12MHz); //blocks in normal state operate at 1V supply voltage and 50MHz operation frequency
		SetLevel(DIFF_LEVEL(1), 5V, 0.12MHz);
		SetLevel(DIFF_LEVEL(2), 5V, 48MHz);
		PD_1 = PD    (    NORMAL    , OFF); //power states assignment to PD_1
		PD_2 = PD (   NORMAL, DIFF_LEVEL(1), DIFF_LEVEL(2), OFF);
		PD_3 = PD (   NORMAL, DIFF_LEVEL(1), DIFF_LEVEL(2), OFF);
		PD_1.AddComponent("RS232");
		PD_2.AddComponent("CPU");
		PD_3.AddComponent("CPU2");

		CPU.data_out(cpu_dout);
		CPU2.data_out(cpu_dout);
		RS232.tx_byte(cpu_dout);

		CPU.virtual_tx_valid(txValid);
		RS232.transmit(txValid)



		on_mode = PM(NORMAL, DIFF_LEVEL(1), DIFF_LEVEL(1)); //power mode specification – contains active states of power domains
		off_mode = PM  (OFF, OFF, OFF);
	}
};
