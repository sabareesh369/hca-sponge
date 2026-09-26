import numpy as np, sponge as ca, cube, hca_round as hca2
from sponge import rotl, RC
from hca_round import G, RHO
def make(theta=True, rho=True):
    def rnd(a,r):
        if theta:
            c=[a[x][0]^a[x][1]^a[x][2]^a[x][3]^a[x][4] for x in range(5)]
            d=[c[(x-1)%5]^rotl(c[(x+1)%5],1) for x in range(5)]
            a=[[a[x][y]^d[x] for y in range(5)] for x in range(5)]
        t=[[rotl(a[x][y],RHO[x][y]) if rho else a[x][y] for y in range(5)] for x in range(5)]
        s=[[G(t,x,y)^G(t,x,y-1)^G(t,x,y+1) for y in range(5)] for x in range(5)]
        b1=[[rotl(G(s,x,y)^(~G(s,x+1,y)&G(s,x+2,y)),1) for y in range(5)] for x in range(5)]
        s=[[G(b1,x,y)^G(b1,x-1,y)^G(b1,x+1,y) for y in range(5)] for x in range(5)]
        b2=[[rotl(G(s,x,y)^(~G(s,x,y+1)&G(s,x,y+2)),57) for y in range(5)] for x in range(5)]
        s=[[G(b2,x,y)^(~G(b2,x+1,y)&G(b2,x+2,y)) for y in range(5)] for x in range(5)]
        b3=[[rotl(~(G(s,x,y)^(~G(s,x,y+1)&G(s,x,y+2))),13) for y in range(5)] for x in range(5)]
        b4=[[rotl(G(b3,x,y)^(~G(b3,x+1,y+1)&G(b3,x+2,y+2)),36) for y in range(5)] for x in range(5)]
        b4[0][0]=b4[0][0]^np.uint64(RC[r%24]); return b4
    return rnd
if __name__=='__main__':
    rng=np.random.default_rng(12); base=rng.integers(0,256,(300,64),dtype=np.uint8)
    def av(rf,r):
        ca.ca_round=rf; H0=ca.hash_batch([bytes(x) for x in base],rounds=r); t=[];dead=None
        for bit in range(0,512,16):
            m=base.copy(); m[:,bit//8]^=np.uint8(1<<(bit%8))
            D=np.unpackbits(H0^ca.hash_batch([bytes(x) for x in m],rounds=r),axis=1); t.append(D.mean())
            if bit==0: dead=int((D.mean(0)==0).sum())
        return 100*np.mean(t),dead
    for nm,rf in [("B only",make(False,False)),("theta+B (uniform rot)",make(True,False)),("rho'+B",make(False,True)),("theta+rho'+B (HCA)",make(True,True))]:
        print(nm, "24R: %.2f%% dead %d"%av(rf,24), flush=True)
    print("uniform-rot sweep:", [round(av(make(True,False),r)[0],1) for r in [1,2,4,8,12,16,20,24,28,32]])
    print("rho sweep noθ:", [round(av(make(False,True),r)[0],1) for r in [1,2,3,4]])
    # cube test
    for rounds in [1,2,3]:
        dmin=None
        for d in range(2,19):
            if cube.zero_sum(make(True,True),rounds,d,trials=4 if d>14 else 8): dmin=d; break
        print(f"HCA2 cube {rounds}R:", dmin, flush=True)
