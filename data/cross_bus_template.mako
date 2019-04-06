
% if notes:
//${notes}
% endif
BusAck_CrossDomain #(
    .size(${bus_size})
    ) ${cross_bus}(
% if clock_a:
	.clkA(${clock_a}),
% else:
	//.clkA(),
% endif
	.rstA(1'b0),
	//.FlagIn_clkA(),
	//.Busy_clkA(),
% if clock_b:
	.clkB(${clock_b}),
% else:
	//.clkB(),
% endif
	.rstB(1'b0),
% if flag_out_b:
	.FlagOut_clkB(${flag_out_b}),
% else:
	//.FlagOut_clkB(),
% endif
% if bus_in_a:
	.BusIn(${bus_in_a}),
% else:
	//.BusIn(),
% endif
	.BusOut(${bus_out_b})
);
