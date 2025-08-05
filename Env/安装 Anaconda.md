## 安装 Anaconda

### 参考

[Anaconda 软件仓库镜像使用帮助](https://help.mirrors.cernet.edu.cn/anaconda/)

[从零开始配置WSL2下的Python开发环境，看这一篇就够了](https://ymzhangcs.com/posts/wsl-configuration/)

### 如何卸载

[Unbuntu卸载anaconda(最新最全亲测)](https://blog.csdn.net/KIK9973/article/details/118795049)

### 下载安装包

**⚠️注意：系统未换源请先进行换源**

```shell
cd ~
wget https://mirrors.pku.edu.cn/anaconda/archive/Anaconda3-2024.10-1-Linux-x86_64.sh
```

🎗️出现 `ERROR 403: Forbidden.`  **尝试以下输入，正常下载跳过这一步**
> [使用wget报错403](https://blog.csdn.net/m0_46225620/article/details/133769790)
>```shell
>wget --user-agent="Mozilla" https://mirrors.pku.edu.cn/anaconda/archive/Anaconda3-2024.10-1-Linux-x86_64.sh
>```

### 安装

```shell
bash Anaconda3-2024.10-1-Linux-x86_64.sh
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
  - https://mirrors.pku.edu.cn/anaconda/pkgs/main
  - https://mirrors.pku.edu.cn/anaconda/pkgs/r
  - https://mirrors.pku.edu.cn/anaconda/pkgs/msys2
custom_channels:
  conda-forge: https://mirrors.pku.edu.cn/anaconda/cloud
  pytorch: https://mirrors.pku.edu.cn/anaconda/cloud
```

### 添加环境变量 

**⚠️注意：请使用自己的 `anaconda3` 路径，如果已添加可跳过这一步**

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
