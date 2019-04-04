
power_manager pmu(
	//.clk(),
	.reset(1'b0),
% if pmu_type == "LEVELS" or pmu_type == "COMBINED":
    //.change_level_flag(),
    //.change_level(),
% endif
% if pmu_type == "POWER_MODE" or pmu_type == "COMBINED":
    //.change_power_mode_flag(),
    //.change_power_mode(),
% endif
% for number in range(num_clocks):
    .power_domain_clk_${number}(pd_clk_${number})\
    % if (number+1) < num_clocks:
,
    % endif
% endfor

);

% for number in range(num_clocks):
wire pd_clk_${number};
% endfor
