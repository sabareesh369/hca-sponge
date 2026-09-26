import numpy as np, sponge as ca
from sponge import rotl, RC
RHO=[[0,36,3,41,18],[1,44,10,45,2],[62,6,43,15,61],[28,55,25,21,56],[27,20,39,8,14]]  # Keccak rho r[x][y]
def make_round(fix):
    def rnd(a,r):
        c=[a[x][0]^a[x][1]^a[x][2]^a[x][3]^a[x][4] for x in range(5)]
        d=[c[(x-1)%5]^rotl(c[(x+1)%5],1) for x in range(5)]
        t=[[a[x][y]^d[x] for y in range(5)] for x in range(5)]
        if fix=="rho": t=[[rotl(t[x][y],RHO[x][y]) for y in range(5)] for x in range(5)]
        b1=[[rotl(t[x][y]^(~t[(x+1)%5][y]&t[(x+2)%5][y])^t[x][(y-1)%5]^t[x][(y+1)%5],1) for y in range(5)] for x in range(5)]
        b2=[[rotl(b1[x][y]^(~b1[x][(y+1)%5]&b1[x][(y+2)%5])^b1[(x-1)%5][y]^b1[(x+1)%5][y],57) for y in range(5)] for x in range(5)]
        b3=[[rotl(~(b2[x][y]^(~b2[(x-1)%5][y]&b2[(x+1)%5][y])^(~b2[x][(y-1)%5]&b2[x][(y+1)%5])),13) for y in range(5)] for x in range(5)]
        sw=(lambda v: v) if fix=="noswap" else (lambda v: rotl(v,32))
        b4=[[rotl(b3[x][y]^(b3[(x-1)%5][y]&b3[x][(y-1)%5])^(~b3[(x+1)%5][y]&b3[x][(y+1)%5])^(0 if fix=="noswap" else sw(b3[x][y])),36) for y in range(5)] for x in range(5)]
        b4[0][0]=b4[0][0]^np.uint64(RC[r%24]); return b4
    return rnd
def run(fix,rounds,base,m):
    ca.ca_round=make_round(fix)
    H0=ca.hash_batch([bytes(x) for x in base],rounds=rounds); H1=ca.hash_batch([bytes(x) for x in m],rounds=rounds)
    D=np.unpackbits(H0^H1,axis=1); p=D.mean(0); return D.mean()*100,(p==0).sum()
if __name__=="__main__":
    rng=np.random.default_rng(7)
    base=rng.integers(0,256,(300,64),dtype=np.uint8); m=base.copy(); m[:,5]^=1
    for fix in ["orig","rho"]:
        for r in ([24,28,31,32,34,40,48] if fix=="orig" else [1,2,3,4,5,6,8,24]):
            a,dd=run(fix,r,base,m); print(fix,"rounds %2d avalanche %.2f%% dead %d"%(r,a,dd),flush=True)
    