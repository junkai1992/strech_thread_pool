# python基于python封装线程池
## python线程池封装

### 1.功能介绍

```
1. 实现自动缩容（类似于Java keepAliveTime ,当线程池中数量大于核心线程数量或设置了allowCoreThreadTimeOut时，线程会根据keepAliveTime的值进行活性检测，一旦超时便销毁线程）
2.节制开启的多线程（只需要直接增加1个线程可以）。
3.线程池放入任务队列为有边界队列
4.此线程池运行函数出错时候，直接显示线程错误。
```

### 2.例子

```python
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
```

