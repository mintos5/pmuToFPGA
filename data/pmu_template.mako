
power_manager pmu(
	//.clk(),
	.reset(0'b),
<%
    from structs.device import PmuType
%>\
% if pmu_type == PmuType.LEVELS or pmu_type == PmuType.COMBINED:
    //.change_level_flag(),
    //.change_level(),
% endif
% if pmu_type == PmuType.POWER_MODES or pmu_type == PmuType.COMBINED:
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
