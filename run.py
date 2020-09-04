import time
from threadpool_executor_shrink_able import ThreadPoolExecutorShrinkAble
from strech_thread_pool import ThreadPoolExecutorStrech

pool = ThreadPoolExecutorStrech(200)

def f1(a):
    time.sleep(0.2)
    print(f"{a}")

for i in range(200):
    time.sleep(0.2)
    pool.submit(f1,str(i))

time.sleep(1000)
