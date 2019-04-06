
% if generate_wires:
wire ${flag_out_b};
% endif
FlagAck_CrossDomain ${cross_flag}(
	.clkA(${clock_a}),
	.rstA(1'b0),
	.FlagIn_clkA(${flag_a}),
	//.Busy_clkA(),
	.clkB(${clock_b}),
	.rstB(1'b0),
	.FlagOut_clkB(${flag_out_b})
);
