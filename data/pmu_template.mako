
% for number in range(num_clocks):
wire pd_clk_${number};
% endfor
% if sync_control:
    % if pmu_type == "LEVELS" or pmu_type == "COMBINED":
wire level_flag_synced;
wire [${level_size-1}:0] level_synced;
    % endif
    % if pmu_type == "POWER_MODE" or pmu_type == "COMBINED":
wire power_mode_flag_synced;
wire [${power_mode_size-1}:0] power_mode_synced;
    % endif
% endif

power_manager pmu(
	//.clk(_PMU_CLOCK_),
	.reset(1'b0),
% if pmu_type == "LEVELS" or pmu_type == "COMBINED":
    % if sync_control:
    .change_level_flag(level_flag_synced),
    .change_level(level_synced),
    % else:
    //.change_level_flag(),
    //.change_level(),
    % endif
% endif
% if pmu_type == "POWER_MODE" or pmu_type == "COMBINED":
    % if sync_control:
    .change_power_mode_flag(power_mode_flag_synced),
    .change_power_mode(power_mode_synced),
    % else:
    //.change_power_mode_flag(),
    //.change_power_mode(),
    % endif
% endif
% for number in range(num_clocks):
    .power_domain_clk_${number}(pd_clk_${number})\
    % if (number+1) < num_clocks:
,
    % endif
% endfor

);
