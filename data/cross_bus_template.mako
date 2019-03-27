BusAck_CrossDomain ${cross_bus}(
	.clkA(${clock_a}),
	.rstA(${reset_a}),
	.FlagIn_clkA(${flag_a}),
	.Busy_clkA(${busy_out_a}),
	.clkB(${clock_b}),
	.rstB(${reset_b}),
	.FlagOut_clkB(${flag_out_b}),
	.BusIn(${bus_in_a}),
	.BusOut(${bus_out_b})
);
