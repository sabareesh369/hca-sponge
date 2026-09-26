`timescale 1ns/1ps
module tb; reg clk=0,reset; reg [63:0] in; reg in_ready,is_last; reg [2:0] byte_num;
 wire bf; wire [511:0] out; wire out_ready; integer cyc=0, n=0, first=0, last=0;
 keccak_ca u(clk,reset,in,in_ready,is_last,byte_num,bf,out,out_ready);
 always #5 clk=~clk;
 always @(posedge clk) begin cyc=cyc+1; if (u.f_ack) begin n=n+1; if(n==5) first=cyc; if(n==35) last=cyc; end end
initial begin reset=1;in_ready=0;is_last=0;in=0;byte_num=0; @(negedge clk);@(negedge clk); reset=0;
 in_ready=1; repeat(40*9) begin @(negedge clk); while(bf) @(negedge clk); in=64'h0123456789abcdef; end @(negedge clk); in_ready=0;
  $display("steady-state cycles per block = %0f", (last-first)/30.0); $finish; end
endmodule
