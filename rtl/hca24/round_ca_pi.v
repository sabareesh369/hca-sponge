// ============================================================
// round_ca_pi.v  (HCA-Sponge, bijective version)
// Theta -> rho' (lane-dependent rotation) -> B1 -> B2 -> B3 -> B4 -> Iota
//   B1 = rotL1 ( chi_row ( column XOR ) )
//   B2 = rotR7 ( chi_col ( row XOR ) )
//   B3 = rotL13( NOT chi_col ( chi_row ) )
//   B4 = rotR28( chi_diag )
// Every step is invertible, so the round is a permutation.
// ============================================================
module round_ca_pi(in, round_const, out);
    input  [1599:0] in;
    input  [63:0]   round_const;
    output [1599:0] out;
    genvar x, y;

    function integer rho_off;
        input integer xx, yy;
        integer tbl [0:24];
        begin
            tbl[0]=0;   tbl[1]=36;  tbl[2]=3;   tbl[3]=41;  tbl[4]=18;
            tbl[5]=1;   tbl[6]=44;  tbl[7]=10;  tbl[8]=45;  tbl[9]=2;
            tbl[10]=62; tbl[11]=6;  tbl[12]=43; tbl[13]=15; tbl[14]=61;
            tbl[15]=28; tbl[16]=55; tbl[17]=25; tbl[18]=21; tbl[19]=56;
            tbl[20]=27; tbl[21]=20; tbl[22]=39; tbl[23]=8;  tbl[24]=14;
            rho_off = tbl[5*xx+yy];
        end
    endfunction
    function [63:0] rotl;
        input [63:0] v; input integer n;
        begin rotl = (n==0) ? v : ((v << n) | (v >> (64-n))); end
    endfunction

    wire [63:0] a [0:4][0:4];  wire [63:0] c [0:4];  wire [63:0] d [0:4];
    wire [63:0] t [0:4][0:4];
    wire [63:0] s1[0:4][0:4];  wire [63:0] b1[0:4][0:4];
    wire [63:0] s2[0:4][0:4];  wire [63:0] b2[0:4][0:4];
    wire [63:0] s3[0:4][0:4];  wire [63:0] b3[0:4][0:4];
    wire [63:0] b4[0:4][0:4];

    generate
      for (y=0; y<5; y=y+1) begin : UNPACK_Y
        for (x=0; x<5; x=x+1) begin : UNPACK_X
          assign a[x][y] = in[(1599 - 64*(5*y+x)) -: 64];
        end
      end
      for (x=0; x<5; x=x+1) begin : THETA_C
        assign c[x] = a[x][0]^a[x][1]^a[x][2]^a[x][3]^a[x][4];
        assign d[x] = c[(x+4)%5] ^ rotl(c[(x+1)%5],1);
      end
      for (y=0; y<5; y=y+1) begin : ST1_Y
        for (x=0; x<5; x=x+1) begin : ST1_X
          assign t[x][y]  = rotl(a[x][y] ^ d[x], rho_off(x,y));                       // theta + rho'
          assign s1[x][y] = t[x][y] ^ t[x][(y+4)%5] ^ t[x][(y+1)%5];                  // column XOR
        end
      end
      for (y=0; y<5; y=y+1) begin : ST2_Y
        for (x=0; x<5; x=x+1) begin : ST2_X
          assign b1[x][y] = rotl(s1[x][y] ^ (~s1[(x+1)%5][y] & s1[(x+2)%5][y]), 1);  // chi rows
        end
      end
      for (y=0; y<5; y=y+1) begin : ST3_Y
        for (x=0; x<5; x=x+1) begin : ST3_X
          assign s2[x][y] = b1[x][y] ^ b1[(x+4)%5][y] ^ b1[(x+1)%5][y];               // row XOR
        end
      end
      for (y=0; y<5; y=y+1) begin : ST4_Y
        for (x=0; x<5; x=x+1) begin : ST4_X
          assign b2[x][y] = rotl(s2[x][y] ^ (~s2[x][(y+1)%5] & s2[x][(y+2)%5]), 57); // chi cols
          assign s3[x][y] = b2[x][y] ^ (~b2[(x+1)%5][y] & b2[(x+2)%5][y]);           // chi rows
        end
      end
      for (y=0; y<5; y=y+1) begin : ST5_Y
        for (x=0; x<5; x=x+1) begin : ST5_X
          assign b3[x][y] = rotl(~(s3[x][y] ^ (~s3[x][(y+1)%5] & s3[x][(y+2)%5])), 13); // chi cols + NOT
        end
      end
      for (y=0; y<5; y=y+1) begin : ST6_Y
        for (x=0; x<5; x=x+1) begin : ST6_X
          assign b4[x][y] = rotl(b3[x][y] ^ (~b3[(x+1)%5][(y+1)%5] & b3[(x+2)%5][(y+2)%5]), 36); // chi diag
          if (x==0 && y==0)
            assign out[(1599 - 64*(5*y+x)) -: 64] = b4[0][0] ^ round_const;
          else
            assign out[(1599 - 64*(5*y+x)) -: 64] = b4[x][y];
        end
      end
    endgenerate
endmodule
