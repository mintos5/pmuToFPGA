#include "systemc.h"
#include  "pms.h"
#include "cpu.h"
#include "rs232.h"

SC_MODULE(Sys){
	sc_signal<data> cpu_dout, txValid, rxValid;
	PowerDomain PD_1; //declaration of power domain PD_1
	PowerDomain PD_2; //declaration of power domain PD_2
	PowerDomain PD_3; //declaration of power domain PD_3
	PowerMode on_mode; //declaration of power mode on_mode
	PowerMode off_mode;
	cpuType CPU;
	serialType RS232;
	serialType RS232_copy;

	SC_CTOR(Sys) : CPU("CPU"), RS232("RS232"){
		SetLevel(NORMAL, 5V, 12MHz);
		SetLevel(DIFF_LEVEL(1), 5V, 0.12MHz);
		SetLevel(DIFF_LEVEL(2), 5V, 48MHz);
		PD_1 = PD    (    NORMAL    , OFF);
		PD_2 = PD (   NORMAL, DIFF_LEVEL(1), DIFF_LEVEL(2), OFF);
		PD_3 = PD(NORMAL, DIFF_LEVEL(2), OFF);
		PD_1.AddComponent("RS232");
		PD_2.AddComponent("CPU");
		PD_3.AddComponent("RS232_copy");

		CPU.data_out(cpu_dout);
		RS232.tx_byte(cpu_dout);
		RS232_copy.tx_byte(cpu_dout);

		CPU.virtual_tx_valid(txValid);
		RS232.transmit(txValid);
		RS232_copy.transmit(txValid);
		CPU.virtual_rx_valid(rxValid);
		RS232.received(rxValid);



		on_mode = PM(NORMAL, DIFF_LEVEL(1), DIFF_LEVEL(2));
		off_mode = PM  (OFF, OFF, OFF);
	}
};
