`include "pmu.v"
`timescale 1us/1us

module pmu_tb;

    initial begin
        $dumpfile("pmu_tb.vcd");
        $dumpvars;
        delay(500);
        pmu_changerSpeed = 1;
        pmu_busSpeed = 3'b101;
        delay(1);
        pmu_changerSpeed = 0;
        delay(800);
        $finish;
        //# 250E3 $finish;
        //# 1E6 $finish;
    end

    reg clk = 0;
    always #1 clk = !clk;
    reg clk2 = 0;
    always #2 clk2 = !clk2;

    reg pmu_changerSpeed = 0;
    reg [2:0] pmu_busSpeed = 3'b101;
    output pd_clk_0;
    output pd_clk_1;
    output pd_clk_2;



    power_manager pmu(
	.clk(clk),
	.reset(1'b0),
    .change_level_flag(pmu_changerSpeed),
    .change_level(pmu_busSpeed),
    //.change_power_mode_flag(),
    //.change_power_mode(),
    .power_domain_clk_0(pd_clk_0),
    .power_domain_clk_1(pd_clk_1)
    );

    task delay(input integer N); begin
        repeat(N) @(posedge clk);
    end endtask


endmodule
