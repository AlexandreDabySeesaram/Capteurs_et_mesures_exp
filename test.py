import numpy as np

import time 

N = 1000
A = np.random.rand(N, N).astype(np.float64)
B = np.random.rand(N, N).astype(np.float64)

for i in range(10):
    t_0 = time.time()
    # C = np.dot(A, B)
    C = np.einsum("ik,kj->ij",A, B)
    t_1 = time.time()
    t_1 = time.time()
    print(f"time (s) : {t_1-t_0} - iter {i}")
