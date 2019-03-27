FlagAck_CrossDomain ${cross_flag}(
	.clkA(${clock_a}),
	.rstA(${reset_a}),
	.FlagIn_clkA(${flag_a}),
	.Busy_clkA(${busy_out_a}),
	.clkB(${clock_b}),
	.rstB(${reset_b}),
	.FlagOut_clkB(${flag_out_b})
);