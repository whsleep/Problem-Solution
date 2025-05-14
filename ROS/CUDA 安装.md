## CUDA 安装

### 参考

[在WSL2中卸载Anaconda](https://blog.csdn.net/Yellow_S_D/article/details/143080434)

[WSL——卸载、安装CUDA](https://blog.csdn.net/weixin_45100742/article/details/134499492)

[在 WSL 上启用 NVIDIA CUDA](https://learn.microsoft.com/zh-cn/windows/ai/directml/gpu-cuda-in-wsl)

[WSL 2 上的 NVIDIA GPU 加速计算](https://docs.nvidia.com/cuda/wsl-user-guide/index.html#getting-started-with-cuda-on-wsl)


#### 查看允许安装的CUDA版本

打开 `Windows PowerShell` 输入 

```shell
nvidia-smi
```

我的终端输出为

```shell
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 576.28                 Driver Version: 576.28         CUDA Version: 12.9     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                  Driver-Model | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 4060 ...  WDDM  |   00000000:01:00.0  On |                  N/A |
| N/A   51C    P0             17W /   91W |    1026MiB /   8188MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|    0   N/A  N/A            3844    C+G   ...xyewy\ShellExperienceHost.exe      N/A      |
|    0   N/A  N/A            6224    C+G   ..._cw5n1h2txyewy\SearchHost.exe      N/A      |
|    0   N/A  N/A           12860    C+G   ...t\Edge\Application\msedge.exe      N/A      |
|    0   N/A  N/A           14260    C+G   ...8bbwe\PhoneExperienceHost.exe      N/A      |
|    0   N/A  N/A           16016    C+G   ...y\StartMenuExperienceHost.exe      N/A      |
|    0   N/A  N/A           16300    C+G   C:\Windows\explorer.exe               N/A      |
|    0   N/A  N/A           18664    C+G   ...efSharp.BrowserSubprocess.exe      N/A      |
|    0   N/A  N/A           20316    C+G   ...ntrolPanel\SystemSettings.exe      N/A      |
|    0   N/A  N/A           20700    C+G   ...munity\Common7\IDE\devenv.exe      N/A      |
|    0   N/A  N/A           24940    C+G   ...7efx6bt\app\PredatorSense.exe      N/A      |
|    0   N/A  N/A           27140    C+G   ...26wp6bftszj\TranslucentTB.exe      N/A      |
|    0   N/A  N/A           27572    C+G   ...ms\Microsoft VS Code\Code.exe      N/A      |
|    0   N/A  N/A           27820    C+G   ...App_cw5n1h2txyewy\LockApp.exe      N/A      |
|    0   N/A  N/A           29184    C+G   ...t\Edge\Application\msedge.exe      N/A      |
|    0   N/A  N/A           29232    C+G   ...iceHub.ThreadedWaitDialog.exe      N/A      |
|    0   N/A  N/A           29280    C+G   ...5n1h2txyewy\TextInputHost.exe      N/A      |
|    0   N/A  N/A           29876    C+G   ...dgb7efx6bt\app\QuickPanel.exe      N/A      |
|    0   N/A  N/A           30352    C+G   ...yb3d8bbwe\WindowsTerminal.exe      N/A      |
+-----------------------------------------------------------------------------------------+
```

#### 安装CUDA

我的适合安装版本为 `CUDA Version: 12.9`

[最新版](https://developer.nvidia.com/cuda-downloads)

[历史版本](https://developer.nvidia.com/cuda-toolkit-archive)

使用上面两个链接找到合适的安装版本

限制选项依次为

`Linux` $\rightarrow$ `x86_64` $\rightarrow$ `WSL-Ubuntu` $\rightarrow$ `2.0` $\rightarrow$ `deb(local)`

选取完成后，该界面会更新安装指令(**⚠️注意：请按照你的版本信息进行指令安装，下面的指令不一定适用**)

```shell
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-wsl-ubuntu.pin
sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/12.9.0/local_installers/cuda-repo-wsl-ubuntu-12-9-local_12.9.0-1_amd64.deb
sudo dpkg -i cuda-repo-wsl-ubuntu-12-9-local_12.9.0-1_amd64.deb
sudo cp /var/cuda-repo-wsl-ubuntu-12-9-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-9
```

#### 更新 `.bashrc`

`.bashrc`加入下述代码(**⚠️注意：请按照你的CUDA版本进行修改**)

```shell
export PATH="$PATH:/usr/local/cuda-12.9/bin"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/cuda-12.9/lib64/"
export LIBRARY_PATH="$LIBRARY_PATH:/usr/local/cuda-12.9/lib64"
```

更新

```shell
source ~/.bashrc
```

检查是否安装成功

```shell
nvcc -V
```

终端输出

```shell
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2019 NVIDIA Corporation
Built on Sun_Jul_28_19:07:16_PDT_2019
Cuda compilation tools, release 10.1, V10.1.243
```
即安装成功。
