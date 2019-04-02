
% for number in range(num_clocks):
SB_GB global_buffer_${number} (
   .USER_SIGNAL_TO_GLOBAL_BUFFER (pd_clk_${number}),
   .GLOBAL_BUFFER_OUTPUT (gb_pd_clk_${number}) );

% endfor

% for number in range(num_clocks):
wire gb_pd_clk_${number};
% endfor
