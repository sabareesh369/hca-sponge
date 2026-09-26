import numpy as np, sponge as ca
from hca_round import hca2_round
ca.ca_round=hca2_round
rng=np.random.default_rng(2026)
def stats(rounds,NM=1000,L=64):
    base=rng.integers(0,256,(NM,L),dtype=np.uint8); H0=ca.hash_batch([bytes(x) for x in base],rounds=rounds)
    dist=np.zeros((NM,L*8)); sac=np.zeros((L*8,512))
    for bit in range(L*8):
        m=base.copy(); m[:,bit//8]^=np.uint8(1<<(bit%8))
        d=np.unpackbits(H0^ca.hash_batch([bytes(x) for x in m],rounds=rounds),axis=1); dist[:,bit]=d.sum(1); sac[bit]=d.mean(0)
    a=dist/5.12
    return a.mean(),a.std(),a.min(),a.max(),np.abs(sac-0.5).max(),100*np.mean(np.abs(sac-0.5)<=0.05),dist.ravel()
for r in [24,12]:
    s=stats(r); print(f"HCA2 {r}R: aval {s[0]:.2f} +- {s[1]:.2f} min {s[2]:.2f} max {s[3]:.2f} | SAC maxdev {s[4]:.3f} within {s[5]:.1f}% | HD {s[6].mean():.2f}+-{s[6].std():.2f}",flush=True)
    if r==24: np.save("hd_hca2.npy",s[6][::4])
# linearity
a,b,c=[rng.integers(0,256,(200,71),dtype=np.uint8) for _ in range(3)]
H=lambda m: ca.hash_batch([bytes(x) for x in m])
print("linearity holds:",np.all((H(a)^H(b)^H(c)^H(a^b^c))==0,axis=1).sum(),"/200")
# truncated collisions
N=200000; msgs=[bytes(x) for x in rng.integers(0,256,(N,16),dtype=np.uint8)]
for r in [24,12]:
    h=ca.hash_batch(msgs,outlen=4,rounds=r).copy().view('<u4').ravel(); _,cnt=np.unique(h,return_counts=True)
    print(f"{r}R 32-bit collisions: {int((cnt*(cnt-1)//2).sum())} (expected 4.66)")
