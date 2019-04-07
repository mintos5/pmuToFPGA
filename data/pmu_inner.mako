<%namespace name="pmu" file="pmu_inner_func.mako"/>
module power_manager(
    input clk,                  // The master clock for this module
    input reset,                  // Synchronous reset
${pmu.make_control_input()}\
${pmu.make_pds_clock()}
);
// wire and pll module
wire pll_clk;

${pmu.make_pll()}

// reg and warmboot module for reconfiguration
${pmu.make_reconf_setter()}
${pmu.make_warmboot()}

// Generated levels
${pmu.make_levels_defines()}

// Inner registers for divider
${pmu.make_counter_reg()}
${pmu.make_counters()}

// Power domains registers and assigns
% if strict_freq == True:
${pmu.make_strict_setters()}
${pmu.make_strict_assigns()}
% else:
${pmu.make_setters()}
${pmu.make_assigns()}
% endif

// Synchronous sequential logic
always @ (posedge clk) begin
    if (reset) begin
${pmu.reset_counter(2,False)}\
    end
    else begin
${pmu.make_counting(2,False)}
        // Controllers
${pmu.make_controller(2)}
    end
end

% if divide_pll:
always @ (posedge pll_clk) begin
    if (reset) begin
${pmu.reset_counter(2,True)}
    end
    else begin

${pmu.make_counting(2,True)}
    end
end
% endif
endmodule
