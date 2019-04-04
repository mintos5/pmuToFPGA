`include "pmu.v"
`timescale 1us/1us

module tb_pmu;

    initial begin
        $dumpfile("l80soc.vcd");
        $dumpvars;
        delay(50);
        pmu_changerSpeed = 1;
        pmu_busSpeed = 8'b00000000;
        delay(800);
        $finish;
        //# 250E3 $finish;
        //# 1E6 $finish;
    end

    reg clk = 0;
    always #1 clk = !clk;
    reg clk2 = 0;
    always #2 clk2 = !clk2;

    reg reset = 0;
    reg pmu_changerSpeed = 0;
    reg [7:0] pmu_busSpeed = 8'b00000000;
    output slow_clock1;
    output slow_clock2;
    output slow_clock3;



    power_manager pmu (
    .clk(clk2),
    .pll_clk(clk),
    .reset(reset),
    .change(pmu_changerSpeed),
    .change_vector(pmu_busSpeed),
    .clock1(slow_clock1),
    .clock2(slow_clock2),
    .clock3(slow_clock3)
    );

    task delay(input integer N); begin
        repeat(N) @(posedge clk);
    end endtask


endmodule : tb_pmu
