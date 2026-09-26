import numpy as np
from bij import lanes_for_all, unpack, isbij, g
Lv=lambda s:{(x,y): g(s,x,y)^g(s,x,y-1)^g(s,x,y+1) for x in range(5) for y in range(5)}   # column circulant
Lh=lambda s:{(x,y): g(s,x,y)^g(s,x-1,y)^g(s,x+1,y) for x in range(5) for y in range(5)}   # row circulant
Xr=lambda s:{(x,y): g(s,x,y)^(~g(s,x+1,y)&g(s,x+2,y)) for x in range(5) for y in range(5)}   # chi rows
Xc=lambda s:{(x,y): g(s,x,y)^(~g(s,x,y+1)&g(s,x,y+2)) for x in range(5) for y in range(5)}   # chi cols
Xd=lambda s:{(x,y): g(s,x,y)^(~g(s,x+1,y+1)&g(s,x+2,y+2)) for x in range(5) for y in range(5)} # chi diagonals
NOT=lambda s:{k:~v for k,v in s.items()}
L=lanes_for_all()
for nm,f in [("B1' = chi_row(colXOR)",lambda s:Xr(Lv(s))),("B2' = chi_col(rowXOR)",lambda s:Xc(Lh(s))),
             ("B3' = NOT(chi_col(chi_row))",lambda s:NOT(Xc(Xr(s)))),("B4' = chi_diag",Xd)]:
    print(f"{nm:30s} bijective on all 2^25 = {isbij(unpack(f(L)))}",flush=True)
