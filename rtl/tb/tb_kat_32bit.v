`timescale 1ns/1ps
module tb; reg clk=0,reset; reg [31:0] in; reg in_ready,is_last; reg [1:0] byte_num;
 wire bf; wire [511:0] out; wire out_ready; integer c;
 keccak_ca u(clk,reset,in,in_ready,is_last,byte_num,bf,out,out_ready);
 always #5 clk=~clk;
 task msg(input dot); begin
  reset=1;in_ready=0;is_last=0;in=0;byte_num=0; @(negedge clk);@(negedge clk); reset=0; @(negedge clk);
  in_ready=1; in="The ";@(negedge clk); in="quic";@(negedge clk); in="k br";@(negedge clk); in="own ";@(negedge clk);
  in="fox ";@(negedge clk); in="jump";@(negedge clk); in="s ov";@(negedge clk); in="er t";@(negedge clk);
  in="he l";@(negedge clk); in="azy ";@(negedge clk);
  if(dot) begin in="dog.";@(negedge clk); in=0;byte_num=0;is_last=1;@(negedge clk); end
  else begin in="dog ";byte_num=3;is_last=1;@(negedge clk); end
  in_ready=0;is_last=0; c=0; while(out_ready!==1) begin @(posedge clk); c=c+1; end
  $display("cycles=%0d hash=%h", c, out); end endtask
 initial begin msg(0); msg(1); $finish; end
endmodule
