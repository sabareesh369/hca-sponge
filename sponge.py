import numpy as np
M=np.uint64(0xFFFFFFFFFFFFFFFF)
def rotl(v,n):
    n%=64
    if n==0: return v
    return ((v<<np.uint64(n))|(v>>np.uint64(64-n)))
RC=[0x0000000000000001,0x0000000000008082,0x800000000000808A,0x8000000080008000,0x000000000000808B,0x0000000080000001,0x8000000080008081,0x8000000000008009,0x000000000000008A,0x0000000000000088,0x0000000080008009,0x000000008000000A,0x000000008000808B,0x800000000000008B,0x8000000000008089,0x8000000000008003,0x8000000000008002,0x8000000000000080,0x000000000000800A,0x800000008000000A,0x8000000080008081,0x8000000000008080,0x0000000080000001,0x8000000080008008]
def ca_round(a,r,use_theta=True,blended=True):
    # a[x][y] arrays of uint64
    if use_theta:
        c=[a[x][0]^a[x][1]^a[x][2]^a[x][3]^a[x][4] for x in range(5)]
        d=[c[(x-1)%5]^rotl(c[(x+1)%5],1) for x in range(5)]
        t=[[a[x][y]^d[x] for y in range(5)] for x in range(5)]
    else: t=a
    b1=[[rotl(t[x][y]^(~t[(x+1)%5][y]&t[(x+2)%5][y])^t[x][(y-1)%5]^t[x][(y+1)%5],1) for y in range(5)] for x in range(5)]
    b2=[[rotl(b1[x][y]^(~b1[x][(y+1)%5]&b1[x][(y+2)%5])^b1[(x-1)%5][y]^b1[(x+1)%5][y],64-7) for y in range(5)] for x in range(5)]
    b3=[[rotl(~(b2[x][y]^(~b2[(x-1)%5][y]&b2[(x+1)%5][y])^(~b2[x][(y-1)%5]&b2[x][(y+1)%5])),13) for y in range(5)] for x in range(5)]
    b4=[[rotl(b3[x][y]^(b3[(x-1)%5][y]&b3[x][(y-1)%5])^(~b3[(x+1)%5][y]&b3[x][(y+1)%5])^rotl(b3[x][y],32),64-28) for y in range(5)] for x in range(5)]
    b4[0][0]=b4[0][0]^np.uint64(RC[r])
    return b4
def perm(a,rounds=24):
    for r in range(rounds): a=ca_round(a,r)
    return a
def hash_batch(msgs,rate=72,outlen=64,rounds=24,pad_first=0x01):
    # msgs: list of equal-length bytes -> uint8 array (N,L)
    arr=np.frombuffer(b''.join(msgs),dtype=np.uint8).reshape(len(msgs),-1)
    N,L=arr.shape
    nblk=L//rate+1
    P=np.zeros((N,nblk*rate),dtype=np.uint8); P[:,:L]=arr
    P[:,L]^=pad_first; P[:,-1]^=0x80
    z=np.zeros(N,dtype=np.uint64)
    a=[[z.copy() for y in range(5)] for x in range(5)]
    for b in range(nblk):
        blk=P[:,b*rate:(b+1)*rate].copy().view('<u8')
        for i in range(rate//8):
            x,y=i%5,i//5; a[x][y]=a[x][y]^blk[:,i]
        a=perm(a,rounds)
    out=np.stack([a[i%5][i//5] for i in range(25)],1).astype('<u8').view(np.uint8)
    return out[:,:outlen]
if __name__=="__main__":
    f=b"The quick brown fox jumps over the lazy dog"
    for m in [f,f+b"."]:
        print(hash_batch([m])[0].tobytes().hex()[:32])
