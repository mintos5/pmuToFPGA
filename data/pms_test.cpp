#include "systemc.h"
#include  "pms.h"
SC_MODULE(Sys){
	sc_in<bool> clk, clk1, ctrl; //input variables
	sc_out<data> bcd_out; //output variable
	sc_signal<data> s1, s2,s3; //internal signals
	sc_signal<data> test, cpu_dout;
	data BR; //state variable
	PowerDomain PD_1; //declaration of power domain PD_1
	PowerDomain PD_2;
	PowerMode on_mode; //declaration of power mode on_mode
	PowerMode off_mode;
	lfsr LFSR; //instance LFSR of component lfsr
	counter COUNT;
	bcd_converter BCD;
    /*
    asdasdasd
    asdasdasd
    */
    //asdaasda
	SC_CTOR(Sys) : LFSR("LFSR"), COUNT("COUNT"), BCD("BCD"){
		SetLevel(NORMAL, 1V, 12MHz); //blocks in normal state operate at 1V supply voltage and 50MHz operation frequency
		SetLevel(DIFF_LEVEL(1), 1.1V, 0.12MHz);
		SetLevel(DIFF_LEVEL(2), 2.1V, 100MHz);
		PD_1 = PD    (    NORMAL    , OFF); //power states assignment to PD_1
		PD_2 = PD (   NORMAL, DIFF_LEVEL(1), DIFF_LEVEL(2), HOLD   );
		PD_1.AddComponent("cpu");
		PD_2.AddComponent("RS232");

		cpu.nieco(cpu_dout);
		RS232.nieco2(cpu_dout);

		on_mode = PM(NORMAL, DIFF_LEVEL(1)); //power mode specification – contains active states of power domains
		off_mode = PM  (OFF, HOLD);
		POWER_MODE = on_mode; //current power mode initialization
		LFSR.clk(clk1); //communications mapping
		LFSR.data_out(s1);
		COUNT.clk(clk);
		//COUNT.data_in(s1);
		COUNT.data_out(s2);
		BCD.clk(clk);
		BCD.data_in(s2);
		BCD.data_out(s3);
		SC_THREAD(Global);
		Sensitive_pos << clk;
	}

	void Global(){ //functional modelling
		while (true){
			do
			{
				First();
				wait();
			} while (ctrl);
			Second();
		}
	}

	void First(){
		if (ctrl) POWER_MODE = off_mode;
		else POWER_MODE = on_mode; //variable POWER_MODE updates its value based on value of ctrl input variable
		BR = s3.read(); //state variable is updated
	}
	void Second(){
		bcd_out.write(BR); //variable value is sent to output
	}
};
