import numpy as np, time
N=1<<25; W=N//64; j=np.arange(64,dtype=np.uint64)
def lanes_for_all():
    L={}
    for k in range(25):
        x,y=k%5,k//5
        if k<6: word=np.uint64(sum(((jj>>k)&1)<<jj for jj in range(64)))
        w=np.arange(W,dtype=np.uint64)
        L[(x,y)]= np.full(W,word,dtype=np.uint64) if k<6 else np.where(((w<<np.uint64(6))>>np.uint64(k))&np.uint64(1)==1,np.uint64(0xFFFFFFFFFFFFFFFF),np.uint64(0))
    return L
def unpack(O):
    v=np.zeros(N,dtype=np.uint32)
    for k in range(25):
        x,y=k%5,k//5
        v|=(((O[(x,y)][:,None]>>j)&np.uint64(1)).astype(np.uint32).ravel()<<np.uint32(k))
    return v
def isbij(v): return np.bincount(v,minlength=N).max()==1
g=lambda s,x,y: s[(x%5,y%5)]
B1=lambda s:{(x,y): g(s,x,y)^(~g(s,x+1,y)&g(s,x+2,y))^g(s,x,y-1)^g(s,x,y+1) for x in range(5) for y in range(5)}
B2=lambda s:{(x,y): g(s,x,y)^(~g(s,x,y+1)&g(s,x,y+2))^g(s,x-1,y)^g(s,x+1,y) for x in range(5) for y in range(5)}
B3=lambda s:{(x,y): ~(g(s,x,y)^(~g(s,x-1,y)&g(s,x+1,y))^(~g(s,x,y-1)&g(s,x,y+1))) for x in range(5) for y in range(5)}
F4=lambda s:{(x,y): g(s,x,y)^(g(s,x-1,y)&g(s,x,y-1))^(~g(s,x+1,y)&g(s,x,y+1)) for x in range(5) for y in range(5)}
L=lanes_for_all()
for nm,f in [("B1",B1),("B2",B2),("B3",B3),("B4 slice part f",F4)]:
    t=time.time(); v=unpack(f(L)); b=isbij(v)
    print(f"{nm}: bijective on all 2^25 slices = {b}  (distinct outputs {np.unique(v).size})",flush=True)
