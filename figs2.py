import numpy as np, sponge as ca, hashlib, matplotlib, json
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from eval4 import make
plt.rcParams.update({"font.size":9,"font.family":"serif"})
rng=np.random.default_rng(31); base=rng.integers(0,256,(150,64),dtype=np.uint8)
def av(rf,r):
    ca.ca_round=rf; H0=ca.hash_batch([bytes(x) for x in base],rounds=r); t=[]
    for bit in range(0,512,32):
        m=base.copy(); m[:,bit//8]^=np.uint8(1<<(bit%8))
        t.append(np.unpackbits(H0^ca.hash_batch([bytes(x) for x in m],rounds=r),axis=1).mean())
    return 100*np.mean(t)
R=list(range(1,33)); o=[av(make(True,False),r) for r in R]; n=[av(make(True,True),r) for r in R]
json.dump({"uniform":o,"hca":n},open("sweep2.json","w"))
fig,ax=plt.subplots(figsize=(3.5,2.2))
ax.plot(R,o,"o-",ms=3,label="Uniform rotations (variant)"); ax.plot(R,n,"s-",ms=3,label="Lane-dependent rotations (HCA-Sponge)")
ax.axhline(50,ls="--",c="gray",lw=0.8); ax.axvline(12,ls=":",c="k",lw=0.8); ax.axvline(24,ls=":",c="k",lw=0.8)
ax.set_xlabel("Number of rounds"); ax.set_ylabel("Mean avalanche (%)"); ax.set_ylim(0,55)
ax.legend(fontsize=7,loc="center right"); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig("fig_rounds_v2.pdf")
print("uniform",[round(x,1) for x in o[:4]],round(o[11],1),round(o[23],1),round(o[31],1)); print("hca",[round(x,1) for x in n[:4]])
# histogram
hd=np.load("hd_hca2.npy"); b2=rng.integers(0,256,(1000,64),dtype=np.uint8)
S0=np.array([np.frombuffer(hashlib.sha3_512(bytes(x)).digest(),np.uint8) for x in b2]); ds=[]
for bit in range(0,512,4):
    m=b2.copy(); m[:,bit//8]^=np.uint8(1<<(bit%8))
    ds+=list(np.unpackbits(S0^np.array([np.frombuffer(hashlib.sha3_512(bytes(x)).digest(),np.uint8) for x in m]),axis=1).sum(1))
fig,ax=plt.subplots(figsize=(3.5,2.2)); bb=np.arange(200,313,3)
ax.hist(hd,bins=bb,alpha=.6,density=True,label="HCA-Sponge (24 rounds)"); ax.hist(ds,bins=bb,alpha=.6,density=True,label="SHA3-512")
ax.axvline(256,ls="--",c="k",lw=.8); ax.set_xlabel("Output Hamming distance (bits of 512)"); ax.set_ylabel("Density")
ax.legend(fontsize=7); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig("fig_hd_hist_v2.pdf")
print("HD hca %.2f+-%.2f n=%d | sha %.2f+-%.2f n=%d"%(hd.mean(),hd.std(),len(hd),np.mean(ds),np.std(ds),len(ds)))
