module BusAck_CrossDomain(
    input clkA,
    input rstA,
    input FlagIn_clkA,
    output Busy_clkA,
    input clkB,
    input rstB,
    output FlagOut_clkB,
    input [size:0] BusIn,
    output[size:0] BusOut
);

parameter size = 7;

reg FlagToggle_clkA;
reg [1:0] SyncB_clkA;
reg [7:0] BusReg;
always @(posedge rstA or posedge clkA) begin
    if (rstA) begin
        // reset
        FlagToggle_clkA <= 1'b0;
        SyncB_clkA <= 2'b00;
        BusReg <= 8'd0;

    end
    else begin
        FlagToggle_clkA <= FlagToggle_clkA ^ (FlagIn_clkA & ~Busy_clkA);
        SyncB_clkA <= {SyncB_clkA[0], SyncA_clkB[2]};
        if (FlagIn_clkA & ~Busy_clkA) begin
            BusReg <= BusIn;
        end
    end
end

reg [2:0] SyncA_clkB;
always @(posedge rstB or posedge clkB) begin
    if (rstB) begin
        //reset
        SyncA_clkB <= 3'b000;
    end
    else begin
        SyncA_clkB <= {SyncA_clkB[1:0], FlagToggle_clkA};
    end
end


assign FlagOut_clkB = (SyncA_clkB[2] ^ SyncA_clkB[1]);
assign Busy_clkA = FlagToggle_clkA ^ SyncB_clkA[1];
assign BusOut = BusReg;

endmodule