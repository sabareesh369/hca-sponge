import numpy as np, sponge as ca, rho_offsets as ca2
from sponge import rotl, RC
R_=ca2.RHO
def noand(a,r):
    c=[a[x][0]^a[x][1]^a[x][2]^a[x][3]^a[x][4] for x in range(5)]
    d=[c[(x-1)%5]^rotl(c[(x+1)%5],1) for x in range(5)]
    t=[[rotl(a[x][y]^d[x],R_[x][y]) for y in range(5)] for x in range(5)]
    b1=[[rotl(t[x][y]^t[x][(y-1)%5]^t[x][(y+1)%5],1) for y in range(5)] for x in range(5)]
    b2=[[rotl(b1[x][y]^b1[(x-1)%5][y]^b1[(x+1)%5][y],57) for y in range(5)] for x in range(5)]
    b3=[[rotl(~b2[x][y],13) for y in range(5)] for x in range(5)]
    b4=[[rotl(b3[x][y]^rotl(b3[x][y],32),36) for y in range(5)] for x in range(5)]
    b4[0][0]=b4[0][0]^np.uint64(RC[r%24]); return b4
rng=np.random.default_rng(9)
for nm,rf in [("no AND terms",noand),("full HCA-Sponge",ca2.make_round("rho"))]:
    ca.ca_round=rf
    a,b,c=[rng.integers(0,256,(200,71),dtype=np.uint8) for _ in range(3)]
    H=lambda m: ca.hash_batch([bytes(x) for x in m])
    z=H(a)^H(b)^H(c)^H(a^b^c); print(nm, np.all(z==0,axis=1).sum(),"/200 hold")
