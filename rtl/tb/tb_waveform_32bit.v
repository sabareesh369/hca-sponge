`timescale 1ns/1ps
module tb; reg clk=0,reset; reg [31:0] in; reg in_ready,is_last; reg [1:0] byte_num;
 wire bf; wire [511:0] out; wire out_ready; integer f, cyc=0;
 keccak_ca u(clk,reset,in,in_ready,is_last,byte_num,bf,out,out_ready);
 always #5 clk=~clk;
 always @(posedge clk) begin
   $fdisplay(f,"%0d,%b,%b,%b,%b,%b,%b,%h,%h,%h",cyc,reset,in_ready,is_last,bf,u.f_permutation_ca_.calc,out_ready,in,u.f_permutation_ca_.out[1599:1568],out[511:480]);
   cyc=cyc+1; end
 initial begin f=$fopen("wave.csv","w");
  reset=1;in_ready=0;is_last=0;in=0;byte_num=0; @(negedge clk);@(negedge clk); reset=0; @(negedge clk);
  in_ready=1; in="The ";@(negedge clk); in="quic";@(negedge clk); in="k br";@(negedge clk); in="own ";@(negedge clk);
  in="fox ";@(negedge clk); in="jump";@(negedge clk); in="s ov";@(negedge clk); in="er t";@(negedge clk);
  in="he l";@(negedge clk); in="azy ";@(negedge clk); in="dog ";byte_num=3;is_last=1;@(negedge clk);
  in_ready=0;is_last=0;in=0; while(out_ready!==1) @(posedge clk);
  repeat(3) @(posedge clk); $display("digest %h",out); $fclose(f); $finish; end
endmodule
