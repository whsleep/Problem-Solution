# WSL2 配置 Docker

## 参考

[容器安装](https://docs.omniverse.nvidia.com/isaacsim/latest/installation/install_container.html#)

[WSL 2 上的 Docker 远程容器入门](https://learn.microsoft.com/zh-cn/windows/wsl/tutorials/wsl-containers)

## 环境信息

打开 `windows` 的 `power shell` ,输入以下指令查看版本。

```shell
 wsl.exe -v
```

我的输出结果为

```shell
WSL 版本： 2.4.13.0
内核版本： 5.15.167.4-1
WSLg 版本： 1.0.65
MSRDC 版本： 1.2.5716
Direct3D 版本： 1.611.1-81528511
DXCore 版本： 10.0.26100.1-240331-1435.ge-release
Windows 版本： 10.0.22631.4751
```

## 安装

> 借助 Docker Desktop for Windows 中支持的 WSL 2 后端，可以在基于 Linux 的开发环境中工作并生成基于 Linux 的容器。

我们只需要在 `windows` 下安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/) 即可，不需要再 `ubuntu` 的虚拟环境中安装。

> 检查系统内核，`power shell` 输入
> 
> ```shell
> systeminfo
> ```
>
> 检查 `System Type:` 标签内容，`x64-based PC` 即为 `amd64`

选择 `amd64` 版本下载安装即可。

下载后打开 `Docker Desktop`，依次打开 `设置` $\rightarrow$ `Resource` $\rightarrow$ `WSL integration` 

再 `Enable integration with additional distros:` 选项中启用你需要的系统发行版本。

使用 `WSL2` 打开你勾选的系统，输入以下指令测试是否安装成功

```shell
docker --version
```

出现版本号即安装成功。

测试是否正常运行

⚠ **注意：这里可能需要科学上网**，请参考[Ubuntu 配置 clash](https://github.com/whsleep/Problem-Solution/blob/main/ROS/Ubuntu%E9%85%8D%E7%BD%AEClash.md)

```shell
docker run hello-world
# 返回 Hello from Docker! 即正常运行
```

## 安装 NVIDIA Container Toolkit

```shell
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list \
  && \
    sudo apt-get update

sudo apt-get install -y nvidia-container-toolkit
```

```shell
sudo systemctl restart docker
```
⚠ **注意：这一步可能会提示重启失败，可尝试关闭 `WSL2` 重新进入虚拟系统。**

---

```shell
sudo tee /etc/docker/daemon.json <<EOF
{
"runtimes": {
"nvidia": {
"path": "nvidia-container-runtime",
"runtimeArgs": []
}
}
}
EOF

sudo nvidia-ctk runtime configure --runtime=docker
```

```shell
sudo systemctl restart docker
```
⚠ **注意：这一步可能会提示重启失败，可尝试关闭 `WSL2` 重新进入虚拟系统。**

### 验证安装

```shell
docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi
```

⚠ **注意：这里大概率因为网络问题报错，解决方案如下**

```shell
sudo nano /etc/resolv.conf
```

打开 `resolv.conf` 输入

```shell
nameserver 8.8.8.8
nameserver 8.8.4.4
```

键盘 `ctrl` + `o` 再按 `enter` 保存，`ctrl` + `x` 退出。

如果仍有问题建议重启 `WSL2`。

最后输出

```shell
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 575.51.03              Driver Version: 576.28         CUDA Version: 12.9     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 4060 ...    On  |   00000000:01:00.0  On |                  N/A |
| N/A   49C    P5              7W /   81W |    1351MiB /   8188MiB |     31%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|    0   N/A  N/A              33      G   /Xwayland                             N/A      |
|    0   N/A  N/A            1194      G   /Xwayland                             N/A      |
+-----------------------------------------------------------------------------------------+
```

即安装成功。


