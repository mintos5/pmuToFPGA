module FlagAck_CrossDomain(
    input clkA,
    input rstA,
    input FlagIn_clkA,
    output Busy_clkA,
    input clkB,
    input rstB,
    output FlagOut_clkB
);

reg FlagToggle_clkA = 1'b0;
reg [1:0] SyncB_clkA = 2'b00;
always @(posedge rstA or posedge clkA) begin
	if (rstA) begin
		// reset
		FlagToggle_clkA <= 1'b0;
		SyncB_clkA <= 2'b00;

	end
	else begin
		FlagToggle_clkA <= FlagToggle_clkA ^ (FlagIn_clkA & ~Busy_clkA);
		SyncB_clkA <= {SyncB_clkA[0], SyncA_clkB[2]};
	end
end

reg [2:0] SyncA_clkB = 3'b000;
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

endmodule
