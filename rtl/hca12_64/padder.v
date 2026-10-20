// padder64.v - 64-bit input version of the Hsing padder (576-bit block = 9 words)
// "is_last" == 0 means 8 bytes are valid; otherwise byte_num (0..7) bytes are valid.
module padder(clk, reset, in, in_ready, is_last, byte_num, buffer_full, out, out_ready, f_ack);
    input              clk, reset;
    input      [63:0]  in;
    input              in_ready, is_last;
    input      [2:0]   byte_num;
    output             buffer_full;
    output reg [575:0] out;
    output             out_ready;
    input              f_ack;
    reg                state;
    reg                done;
    reg        [8:0]   i;
    wire       [63:0]  v0;
    reg        [63:0]  v1;
    wire               accept, update;
    assign buffer_full = i[8];
    assign out_ready   = buffer_full;
    assign accept = (~ state) & in_ready & (~ buffer_full);
    assign update = (accept | (state & (~ buffer_full))) & (~ done);
    always @ (posedge clk)
      if (reset) out <= 0;
      else if (update) out <= {out[575-64:0], v1};
    always @ (posedge clk)
      if (reset) i <= 0;
      else if (f_ack | update) i <= {i[7:0], 1'b1} & {9{~ f_ack}};
    always @ (posedge clk)
      if (reset) state <= 0;
      else if (is_last) state <= 1;
    always @ (posedge clk)
      if (reset) done <= 0;
      else if (state & out_ready) done <= 1;
    padder1 p0 (in, byte_num, v0);
    always @ (*)
      begin
        if (state) begin v1 = 0; v1[7] = v1[7] | i[7]; end
        else if (is_last == 0) v1 = in;
        else begin v1 = v0; v1[7] = v1[7] | i[7]; end
      end
endmodule

// padder1 (64-bit): keep byte_num leading bytes, append 0x01, zero the rest
module padder1(in, byte_num, out);
    input      [63:0] in;
    input      [2:0]  byte_num;
    output reg [63:0] out;
    always @ (*)
      case (byte_num)
        0: out = 64'h0100000000000000;
        1: out = {in[63:56], 56'h01000000000000};
        2: out = {in[63:48], 48'h010000000000};
        3: out = {in[63:40], 40'h0100000000};
        4: out = {in[63:32], 32'h01000000};
        5: out = {in[63:24], 24'h010000};
        6: out = {in[63:16], 16'h0100};
        7: out = {in[63:8],   8'h01};
      endcase
endmodule
