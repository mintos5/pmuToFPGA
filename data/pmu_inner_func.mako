<%def name="make_tabs(number)">\
    % for num in range(number):
    \
    % endfor
</%def>\


<%def name="make_bits(size, number)">\
<%
special_number = '{num:{fill}{width}b}'.format(num=number, fill='0', width=size)
%>\
${size}'b${special_number}\
</%def>\

<%def name="make_control_input()">\
    % if pmu_type == "LEVELS" or pmu_type == "COMBINED":
<%
    levels_count = pds_bitsize + levels_bitsize
%>\
    input change_level_flag,
    input [${levels_count-1}:0] change_level,        // First ${pds_bitsize} bits select power_domain
    % endif
    % if pmu_type == "POWER_MODES" or pmu_type == "COMBINED":
    input change_power_mode_flag,
        % if pms_bitsize == 1:
    input change_power_mode,        // Signal to change power_mode
        % else:
    input [${pms_bitsize - 1}:0] change_power_mode,        // Signal to select power_mode
        % endif
    % endif
</%def>\


<%def name="make_pds_clock()">\
    % for number in range(len(pds)):
    output wire power_domain_clk_${number}\
    % if (number+1) < len(pds):
,
    % endif
    % endfor
</%def>\


<%def name="make_pll()">\
    % if use_pll:
    % for level in levels:
        % if level.pll:
SB_PLL40_CORE #(.FEEDBACK_PATH("SIMPLE"),
                  .PLLOUT_SELECT("GENCLK"),
                  .DIVR(${make_bits(4,level.divr)}),
                  .DIVF(${make_bits(7,level.divf)}),
                  .DIVQ(${make_bits(3,level.divq)}),
                  .FILTER_RANGE(3'b001)
                 ) uut (
                         .REFERENCECLK(clk),
                         .PLLOUTCORE(pll_clk),
                         //.PLLOUTGLOBAL(clk),
                         // .LOCK(D5),
                         .RESETB(1'b1),
                         .BYPASS(1'b0)
                        );
        % endif
    % endfor
    % else:
// PLL is disabled
assign pll_clk = clk;
    % endif
</%def>\


<%def name="make_reconf_setter()">\
    % if ice40_reconfiguration:
reg [2:0] reconf_setter = 3'b000;
    % endif
</%def>\


<%def name="make_warmboot()">\
    % if ice40_reconfiguration:
SB_WARMBOOT  my_warmboot_i  (
    .BOOT (reconf_setter[2]),
    .S1 (reconf_setter[1]),
    .S0 (reconf_setter[0])
);
    % endif
</%def>\


<%def name="make_levels_defines()">\
    % if strict_freq == True:
        % for pd_num in range(len(pds)):
            % for level_num in range(pds[pd_num][0]):
`define SET_PD${pd_num}_FR${level_num} ${make_bits(pds[pd_num][1],level_num)}      // use for setting ${pds[pd_num][2][level_num]} on PD_${pd_num}
            % endfor
        % endfor
    % else:
        % for level_num in range(len(levels)):
`define SET_FR${level_num} ${make_bits(levels_bitsize,level_num)}      // use for setting ${levels[level_num]}
        % endfor
    % endif
</%def>\


<%def name="make_strict_setters()">\
    % for pd_num in range(len(pds)):
        % if pds[pd_num][1] == 1:
reg power_domain_${pd_num}_setter = ${make_bits(pds[pd_num][1],pms[0][1][pd_num])};
        % else:
reg [${pds[pd_num][1]-1}:0] power_domain_${pd_num}_setter = ${make_bits(pds[pd_num][1],pms[0][1][pd_num])};
        % endif
    % endfor
</%def>\


<%def name="make_setters()">\
    % for pd_num in range(len(pds)):
        % if levels_bitsize == 1:
reg power_domain_${pd_num}_setter = ${make_bits(levels_bitsize,pms[0][1][pd_num])};
        % else:
reg [${levels_bitsize-1}:0] power_domain_${pd_num}_setter = ${make_bits(levels_bitsize,pms[0][1][pd_num])};
        % endif
    % endfor
</%def>\


<%def name="make_strict_assigns()">\
    % for pd_num in range(len(pds)):
assign power_domain_clk_${pd_num} = \
        % for level in combined_levels:
            % if level[0] == pd_num:
(power_domain_${pd_num}_setter == `SET_PD${level[0]}_FR${level[1]}) ? ${get_source(level[2])} : \
                % endif
        % endfor
1'b0;
    % endfor
</%def>\


<%def name="make_assigns()">\
    % for pd_num in range(len(pds)):
assign power_domain_clk_${pd_num} = \
        % if all_freq:
            % for level_num in range(len(levels)):
                % if not levels[level_num].zero:
(power_domain_${pd_num}_setter == `SET_FR${level_num}) ? ${get_source(level_num)} : \
                % endif
            % endfor
1'b0;
        % else:
            % for level in combined_levels:
                % if level[0] == pd_num:
(power_domain_${pd_num}_setter == `SET_FR${level[2]}) ? ${get_source(level[2])} : \
                % endif
            % endfor
1'b0;
        % endif
    % endfor
</%def>\


<%def name="get_source(position)">\
    % if levels[position].main_freq_bool:
clk\
    % endif
    % if levels[position].pll:
pll_clk\
    % endif
        % if levels[position].divide_number > 0:
counter_reg_${position}\
    % endif
</%def>\


<%def name="make_counter_reg()">\
    % for number in range(len(levels)):
        % if levels[number].divide_number > 0:
reg counter_reg_${number} = 1'b0;
        % endif
    % endfor
</%def>\


<%def name="make_counters()">\
    % for level_num in range(len(levels)):
        % if levels[level_num].divide_number > 0:
            % if levels[level_num].divide_number == 1:
reg counter_${level_num} = ${levels[level_num].divide_number_size}'h0;
            % else:
reg [${levels[level_num].divide_number_size-1}:0] counter_${level_num} = ${levels[level_num].divide_number_size}'h0;
            % endif
        % endif
    % endfor
</%def>\


<%def name="reset_counter(tabs, pll_clock)">\
    % for level_num in range(len(levels)):
        % if levels[level_num].divide_number > 0 and levels[level_num].divide_from_pll == pll_clock:
${make_tabs(tabs)}counter_${level_num} = ${levels[level_num].divide_number_size}'h0;
        % endif
    % endfor
</%def>\


<%def name="make_counting(tabs, pll_clock)">\
    % for level_num in range(len(levels)):
        % if levels[level_num].divide_number > 0 and levels[level_num].divide_from_pll == pll_clock:
            % if levels[level_num].divide_number == 0:
${make_tabs(tabs)}if (!counter_reg_${level_num}) begin
${make_tabs(tabs)}    counter_reg_${level_num} <= 1'b1;
${make_tabs(tabs)}end
${make_tabs(tabs)}else begin
${make_tabs(tabs)}    counter_reg_${level_num} <= 1'b0;
${make_tabs(tabs)}end
            % else:
${make_tabs(tabs)}if (counter_${level_num}) begin
${make_tabs(tabs)}    counter_${level_num} <= counter_${level_num} - ${levels[level_num].divide_number_size}'d1;
${make_tabs(tabs)}end
${make_tabs(tabs)}else begin
${make_tabs(tabs)}    counter_${level_num} <= ${levels[level_num].divide_number_size}'d${levels[level_num].divide_number};
${make_tabs(tabs)}    if (!counter_reg_${level_num}) begin
${make_tabs(tabs)}        counter_reg_${level_num} <= 1'b1;
${make_tabs(tabs)}    end
${make_tabs(tabs)}    else begin
${make_tabs(tabs)}        counter_reg_${level_num} <= 1'b0;
${make_tabs(tabs)}    end
${make_tabs(tabs)}end
            % endif
        % endif
    % endfor
</%def>\


<%def name="make_controller(tabs)">\
    % if strict_freq:
        % if pmu_type == "LEVELS" or pmu_type == "COMBINED":
${make_tabs(tabs)}if (change_level_flag) begin
${make_strict_levels_controller(tabs+1)}\
${make_tabs(tabs)}end
        % endif
        % if pmu_type == "POWER_MODES" or pmu_type == "COMBINED":
${make_tabs(tabs)}if (change_power_mode_flag) begin
${make_strict_pms_controller(tabs+1)}\
${make_tabs(tabs)}end
        % endif
    % else:
        % if pmu_type == "LEVELS" or pmu_type == "COMBINED":
${make_tabs(tabs)}if (change_level_flag) begin
${make_levels_controller(tabs+1)}\
${make_tabs(tabs)}end
        % endif
        % if pmu_type == "POWER_MODES" or pmu_type == "COMBINED":
${make_tabs(tabs)}if (change_power_mode_flag) begin
${make_pms_controller(tabs+1)}\
${make_tabs(tabs)}end
        % endif
    % endif
</%def>\


<%def name="make_levels_controller(tabs)">\
<%
    levels_count = pds_bitsize + levels_bitsize
%>\
    % for pd_num in range(len(pds)):
${make_tabs(tabs)}if (change_level[${levels_count-1}:${levels_bitsize}] == ${make_bits(pds_bitsize,pd_num)}) begin
${make_tabs(tabs)}    power_domain_${pd_num}_setter <= change_level[${levels_bitsize-1}:0];
${make_tabs(tabs)}end
    % endfor
</%def>\


<%def name="make_strict_levels_controller(tabs)">\
<%
    levels_count = pds_bitsize + levels_bitsize
%>\
    % for pd_num in range(len(pds)):
${make_tabs(tabs)}if (change_level[${levels_count-1}:${levels_bitsize}] == ${make_bits(pds_bitsize,pd_num)}) begin
        % if pds[pd_num][1] == 1:
${make_tabs(tabs)}    power_domain_${pd_num}_setter <= change_level[0];
        % else:
${make_tabs(tabs)}    power_domain_${pd_num}_setter <= change_level[${pds[pd_num][1]-1}:0];
        % endif
${make_tabs(tabs)}end
    % endfor
</%def>\


<%def name="make_pms_controller(tabs)">\
    % for pm_num in range(len(pms)):
${make_tabs(tabs)}if (change_power_mode == ${make_bits(pms_bitsize,pm_num)}) begin
    % if pm_num < 4 and ice40_confs[pm_num]:
${make_tabs(tabs)}    reconf_setter = ${make_bits(2,pm_num)}
    % else:
        % for pd_num in range(len(pds)):
            % if levels_bitsize == 1:
${make_tabs(tabs)}    power_domain_${pd_num}_setter <= ${make_bits(levels_bitsize,pms[pm_num][1][pd_num])};
            % else:
${make_tabs(tabs)}    power_domain_${pd_num}_setter <= ${make_bits(levels_bitsize,pms[pm_num][1][pd_num])};
            % endif
        % endfor
    % endif
${make_tabs(tabs)}end
    % endfor
</%def>\

<%def name="make_strict_pms_controller(tabs)">\
    % for pm_num in range(len(pms)):
${make_tabs(tabs)}if (change_power_mode == ${make_bits(pms_bitsize,pm_num)}) begin
    % if pm_num < 4 and ice40_confs[pm_num]:
${make_tabs(tabs)}    reconf_setter = ${make_bits(2,pm_num)}
    % else:
        % for pd_num in range(len(pds)):
            % if levels_bitsize == 1:
${make_tabs(tabs)}    power_domain_${pd_num}_setter <= ${make_bits(pds[pd_num][1],pms[pm_num][1][pd_num])};
            % else:
${make_tabs(tabs)}    power_domain_${pd_num}_setter <= ${make_bits(pds[pd_num][1],pms[pm_num][1][pd_num])};
            % endif
        % endfor
    % endif
${make_tabs(tabs)}end
    % endfor
</%def>\