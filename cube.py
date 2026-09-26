import numpy as np, rho_offsets as ca2
from sponge import rotl, RC
RHO=ca2.RHO
def keccak_round(a,r):
    c=[a[x][0]^a[x][1]^a[x][2]^a[x][3]^a[x][4] for x in range(5)]
    d=[c[(x-1)%5]^rotl(c[(x+1)%5],1) for x in range(5)]
    a=[[a[x][y]^d[x] for y in range(5)] for x in range(5)]
    b=[[None]*5 for _ in range(5)]
    for x in range(5):
        for y in range(5): b[y][(2*x+3*y)%5]=rotl(a[x][y],RHO[x][y])
    a=[[b[x][y]^(~b[(x+1)%5][y]&b[(x+2)%5][y]) for y in range(5)] for x in range(5)]
    a[0][0]=a[0][0]^np.uint64(RC[r]); return a
hca=ca2.make_round("rho")
rng=np.random.default_rng(5)
def zero_sum(rnd,rounds,d,trials=8):
    # cube over d bits of lane (0,0) (bits 0..d-1), other state bits random; all output bits summed
    ok=0
    N=1<<d; idx=np.arange(N,dtype=np.uint64)
    for t in range(trials):
        base=[[np.uint64(rng.integers(0,2**63))*np.uint64(2)+np.uint64(rng.integers(0,2)) for y in range(5)] for x in range(5)]
        st=[[np.full(N,base[x][y],dtype=np.uint64) for y in range(5)] for x in range(5)]
        st[0][0]=(st[0][0] & ~np.uint64((1<<d)-1)) | idx
        for r in range(rounds): st=rnd(st,r)
        s=np.uint64(0)
        acc=0
        for x in range(5):
            for y in range(5): acc|=int(np.bitwise_xor.reduce(st[x][y]))
        ok+= (acc==0)
    return ok==trials
if __name__=='__main__':
    for name,rnd in [("Keccak-f",keccak_round),("HCA-Sponge",hca)]:
        out=[]
        for rounds in [1,2,3,4]:
            dmin=None
            for d in range(2,19):
                if zero_sum(rnd,rounds,d,trials=4 if d>14 else 8): dmin=d; break
            out.append(f"{rounds}R: {'cube 2^%d'%dmin if dmin else 'none up to 2^18'}")
        print(f"{name:11s}", " | ".join(out), flush=True)
