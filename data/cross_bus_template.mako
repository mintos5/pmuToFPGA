
BusAck_CrossDomain #(
    .size(${bus_size})
    ) ${cross_bus}(
	.clkA(${clock_a}),
	.rstA(1'b0),
	//.FlagIn_clkA(),
	//.Busy_clkA(),
	.clkB(${clock_b}),
	.rstB(1'b0),
	//.FlagOut_clkB(),
	.BusIn(${bus_in_a}),
	.BusOut(${bus_out_b})
);
