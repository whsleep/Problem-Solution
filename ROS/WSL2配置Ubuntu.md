# 环境

`windows11` `WSL2`

# WSL2 安装 Ubuntu20.04

## WSL2 常用指令

[WSL 的基本命令](https://learn.microsoft.com/zh-cn/windows/wsl/basic-commands)

```shell
wsl --shutdown
```

### 参考

[在Windows11中安装WSL2(Ubuntu20.04)并配置Anaconda环境](https://zhuanlan.zhihu.com/p/639611152)

安装较为简易，不再赘述，

#### `wsl: 检测到 localhost 代理配置，但未镜像到 WSL。NAT 模式下的 WSL 不支持 localhost 代理。`

采取[wsl: 检测到 localhost 代理配置，但未镜像到 WSL。NAT 模式下的 WSL 不支持 localhost 代理。](https://gitcode.csdn.net/65e83c781a836825ed78af39.html?dp_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MTgzNDk0OSwiZXhwIjoxNzM1NjExODU4LCJpYXQiOjE3MzUwMDcwNTgsInVzZXJuYW1lIjoid2VpeGluXzY4MjcwMDg3In0.I5WSAifBe_O1pHKXsYQLWC73RB6hykdsE8EH1sv4tXQ&spm=1001.2101.3001.6650.6&utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromBaidu%7Eactivity-6-135048661-blog-141285660.235%5Ev43%5Epc_blog_bottom_relevance_base9&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromBaidu%7Eactivity-6-135048661-blog-141285660.235%5Ev43%5Epc_blog_bottom_relevance_base9&utm_relevant_index=7)可以解决。


**注意**

- `WSL2` 安装的不是桌面版 `Ubuntu` 所以不会出现图形界面。
- 这里我只参考到 `3. Vscode连接WSL2(Ubuntu20.04)`，并未进行 `Anaconda` 安装。

## ROS 安装

使用 [小鱼的一键安装系列](https://fishros.org.cn/forum/topic/20/%E5%B0%8F%E9%B1%BC%E7%9A%84%E4%B8%80%E9%94%AE%E5%AE%89%E8%A3%85%E7%B3%BB%E5%88%97)

按照提示安装即可。

**注意**
- 一键安装系列可以更换系统源，可以进行系统换源。

## 仿真测试

使用 [r550_gazebo](https://github.com/whsleep/r550_gazebo) 进行测试。

请先安装 `git` 

```shell
sudo apt-get update
sudo apt-get install git
```
按照 [readme.md](https://github.com/whsleep/r550_gazebo/blob/main/readme.md) 配置即可

错误&警告参考 [issue](https://github.com/whsleep/r550_gazebo/issues/1)

**实际测试可以运行。**

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

## 安装 Anaconda

### 参考

[Anaconda 软件仓库镜像使用帮助](https://help.mirrors.cernet.edu.cn/anaconda/)

[从零开始配置WSL2下的Python开发环境，看这一篇就够了](https://ymzhangcs.com/posts/wsl-configuration/)

### 下载安装包

**⚠️注意：系统未换源请先进行换源**

```shell
cd ~
wget https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/Anaconda3-5.2.0-Linux-x86_64.sh
```

🎗️出现 `ERROR 403: Forbidden.`  **尝试以下输入，正常下载跳过这一步**
> [使用wget报错403](https://blog.csdn.net/m0_46225620/article/details/133769790)
>```shell
>wget --user-agent="Mozilla" https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/Anaconda3-5.2.0-Linux-x86_64.sh
>```

### 安装

```shell
bash Anaconda3-5.2.0-Linux-x86_64.sh
```

有提示按 `Enter` 或者 输入 `yes`

### 配置 Anaconda 国内镜像源

```shell
code ~/.condarc
```
🎗️ **WSL2的Ubuntu文件可以自己用windows文件资源管理器打开并修改**

替换成以下内容

使用[Anaconda 软件仓库镜像使用帮助](https://help.mirrors.cernet.edu.cn/anaconda/)选取合适的内容覆盖 `.condarc`

```shell
channels:
  - defaults
show_channel_urls: true
default_channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2
custom_channels:
  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  pytorch: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
```

### 添加环境变量 

**⚠️注意：请使用自己的 `anaconda3` 路径**

```shell
echo 'export PATH="/your_path/anaconda3/bin:$PATH"' >> ~/.bashrc
```

验证

```shell
source ~/.bashrc
which conda
```

输出路径即配置成功。

### 测试是否安装成功

**⚠️注意：关闭原来终端，使用新终端进行测试**

```shell
conda --version
```

终端返回版本号即安装成功。

[超全常用 conda 命令整理](https://zhuanlan.zhihu.com/p/24478448255)

### `Anaconda`替换本地 `python` 环境引起的问题及解决方案

#### `ROS:ModuleNotFoundError: No module named ‘rospkg‘`

[ROS:ModuleNotFoundError: No module named 'rospkg'](https://blog.csdn.net/qq_42995327/article/details/119357775)

ROS中原先的一些 `package` 在 `Anaconda`没有安装，使用以下指令安装即可

> 未安装 `pip` 首先安装 `sudo apt install pip`
> 永久换源
> ```shell
> cd ~
> mkdir .pip
> cd .pip
> touch pip.conf
> code pip.conf
> ```
>
> 以下内容放入 `pip.conf` 中
> ```shell
> [global]
> index-url=https://mirrors.aliyun.com/pypi/simple/
> timeout = 6000
> [install]
> trusted-host=pypi.tuna.tsinghua.edu.cn
> disable-pip-version-check = true
> ```

指令安装 

```shell
pip install catkin-tools rospkg pyyaml empy numpy defusedxml
```

