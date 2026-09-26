import numpy as np, sponge as ca, rho_offsets as ca2
from sponge import rotl, RC
RHO=ca2.RHO
def G(s,x,y): return s[x%5][y%5]
def hca2_round(a,r):
    c=[a[x][0]^a[x][1]^a[x][2]^a[x][3]^a[x][4] for x in range(5)]
    d=[c[(x-1)%5]^rotl(c[(x+1)%5],1) for x in range(5)]
    t=[[rotl(a[x][y]^d[x],RHO[x][y]) for y in range(5)] for x in range(5)]
    s=[[G(t,x,y)^G(t,x,y-1)^G(t,x,y+1) for y in range(5)] for x in range(5)]
    b1=[[rotl(G(s,x,y)^(~G(s,x+1,y)&G(s,x+2,y)),1) for y in range(5)] for x in range(5)]
    s=[[G(b1,x,y)^G(b1,x-1,y)^G(b1,x+1,y) for y in range(5)] for x in range(5)]
    b2=[[rotl(G(s,x,y)^(~G(s,x,y+1)&G(s,x,y+2)),57) for y in range(5)] for x in range(5)]
    s=[[G(b2,x,y)^(~G(b2,x+1,y)&G(b2,x+2,y)) for y in range(5)] for x in range(5)]
    b3=[[rotl(~(G(s,x,y)^(~G(s,x,y+1)&G(s,x,y+2))),13) for y in range(5)] for x in range(5)]
    b4=[[rotl(G(b3,x,y)^(~G(b3,x+1,y+1)&G(b3,x+2,y+2)),36) for y in range(5)] for x in range(5)]
    b4[0][0]=b4[0][0]^np.uint64(RC[r%24]); return b4
