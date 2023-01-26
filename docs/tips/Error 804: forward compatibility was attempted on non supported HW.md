This error may happen because the except nvidia-driver version in the nvidia/cuda image is not the same as the host driver.
if your intrested, please check this link: https://zhuanlan.zhihu.com/p/361545761

please follow the setps:

1. Check the libcuda\* and find the nvidia-dirver version that is same with host:

```sh
[container]
ls -l /usr/lib/x86_64-linux-gnu | grep libcuda
```

2. And re-link libcuda.so.1 to the current libcuda.so.<nvidia-driver-ver>

```sh
[container]
mv /usr/lib/x86_64-linux-gnu/libcuda.so.1 /usr/lib/x86_64-linux-gnu/libcuda.so.1.bk
ln -s libcuda.so.<nvidia-driver-ver> /usr/lib/x86_64-linux-gnu/libcuda.so.1
```

3. if it can load model now, but can not work, please reboot in the host.

```sh
[host]
sudo reboot
```
