# Linear-correlation and large-sample differential tests, HCA-Sponge vs Keccak-f.
import numpy as np, json, sys, os
from hca_round import hca2_round
from cube import keccak_round
PERM={"keccak":keccak_round,"hca":hca2_round}
B=1<<16
def rs(rng): return [[rng.integers(0,2**63,B,dtype=np.uint64)*np.uint64(2)+rng.integers(0,2,B,dtype=np.uint64) for y in range(5)] for x in range(5)]
def bitcount(st):   # number of ones per bit position, 1600 entries
    return np.concatenate([np.unpackbits(st[i%5][i//5].view(np.uint8).reshape(B,8),axis=1,bitorder='little').sum(0,dtype=np.int64) for i in range(25)])
def pm1(st):        # B x 1600 as +-1 float32
    return np.concatenate([np.unpackbits(st[i%5][i//5].view(np.uint8).reshape(B,8),axis=1,bitorder='little') for i in range(25)],axis=1).astype(np.float32)*2-1
def run(name, test, batches, seed):
    rf=PERM[name]; rng=np.random.default_rng(seed)
    if test=="lin":
        inb=[(k%25,(k*7)%64) for k in range(64)]; acc=np.zeros((4,64,1600))
        for _ in range(batches):
            st=rs(rng); X=np.stack([((st[l%5][l//5]>>np.uint64(z))&np.uint64(1)).astype(np.float32) for l,z in inb],1)*2-1
            for r in range(4): st=rf(st,r); acc[r]+=X.T@pm1(st)
        return acc/(batches*B)
    diffs=[[(0,0,0)],[(3,2,37)],[(0,0,0),(1,0,0)],[(2,3,5),(2,4,5)]]
    cnt=np.zeros((len(diffs),4,1600))
    for _ in range(batches):
        A=rs(rng)
        for di,dd in enumerate(diffs):
            C=[[A[x][y].copy() for y in range(5)] for x in range(5)]
            for x,y,z in dd: C[x][y]^=np.uint64(1<<z)
            a,c=A,C
            for r in range(4):
                a=rf(a,r); c=rf(c,r); cnt[di,r]+=bitcount([[a[x][y]^c[x][y] for y in range(5)] for x in range(5)])
    return cnt
if __name__=="__main__":
    name,test,batches,seed=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4])
    np.save(f"tb_{name}_{test}_{seed}.npy",run(name,test,batches,seed))
