import numpy as np
from hca_round import hca2_round
from cube import keccak_round
rng=np.random.default_rng(21); N=1<<16
def rand_state(): return [[rng.integers(0,2**63,N,dtype=np.uint64)*np.uint64(2)+rng.integers(0,2,N,dtype=np.uint64) for y in range(5)] for x in range(5)]
def perm(rf,st,R):
    for r in range(R): st=rf(st,r)
    return st
diffs={"1-bit":[((0,0),1)],"1-bit (lane 3,2)":[((3,2),1<<37)],"2-bit":[((0,0),1),((1,0),1)]}
thr=4.5/np.sqrt(N)   # ~ max bias expected for random over 1600 bits
print(f"random-noise level for max |p-0.5| over 1600 bits with 2^16 samples: ~{thr:.4f}")
for nm,rf in [("Keccak-f",keccak_round),("HCA-Sponge",hca2_round)]:
    for dn,dd in diffs.items():
        row=[]
        for R in [1,2,3,4]:
            A=rand_state(); B=[[A[x][y].copy() for y in range(5)] for x in range(5)]
            for (x,y),m in dd: B[x][y]^=np.uint64(m)
            PA,PB=perm(rf,A,R),perm(rf,B,R)
            mx=0
            for x in range(5):
                for y in range(5):
                    D=PA[x][y]^PB[x][y]
                    p=np.unpackbits(D.view(np.uint8).reshape(N,8),axis=1).mean(0)
                    mx=max(mx,np.abs(p-0.5).max())
            row.append(f"{R}R:{mx:.3f}")
        print(f"{nm:10s} {dn:17s}", "  ".join(row),flush=True)
