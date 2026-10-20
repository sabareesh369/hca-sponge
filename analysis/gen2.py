import numpy as np, sponge as ca, sys
from hca_round import hca2_round
ca.ca_round=hca2_round; R=int(sys.argv[1])
N=195313; ctr=np.arange(N,dtype='<u8').view(np.uint8).reshape(N,8); msgs=[bytes(x) for x in ctr]
out=[ca.hash_batch(msgs[i:i+50000],rounds=R) for i in range(0,N,50000)]
open(f"bits_hca2_{R}.bin","wb").write(np.concatenate(out).tobytes()[:12500000])
