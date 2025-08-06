# Docker 安装

## 卸载已安装/系统自带的 `Docker`

```shell
# 删除所有容器、网络、卷（可选，按需）
sudo docker system prune -a --volumes -f
# 卸载 Docker 相关软件包（Ubuntu/Debian）
sudo apt-get purge -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
# 删除残留目录（可选）
sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd
# 如曾手动安装过旧版 docker.io / docker-compose，可一起卸载
sudo apt-get autoremove -y --purge docker.io docker-compose
```

## 安装

```shell
    sudo apt-get update
    sudo apt-get upgrade
```

**安装依赖**

```shell
sudo apt-get install apt-transport-https ca-certificates curl software-properties-common
```

**添加 Docker 的 GPG 密钥**

```shell
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```

**注意: 终端返回 `OK` 才是添加成功**

**安装 Docker 存储库**

```shell
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu  $(lsb_release -cs)  stable"
```

**注意: 需要全部命中, 网络问题请参考[Ubuntu 配置 Clash.md](Ubuntu配置Clash.md)**

```shell
~$ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu  $(lsb_release -cs)  stable"
命中:1 http://mirrors.tuna.tsinghua.edu.cn/ubuntu bionic InRelease
命中:2 http://mirrors.tuna.tsinghua.edu.cn/ubuntu bionic-updates InRelease
命中:3 http://mirrors.tuna.tsinghua.edu.cn/ubuntu bionic-backports InRelease
命中:4 http://mirrors.aliyun.com/docker-ce/linux/ubuntu bionic InRelease
命中:5 http://mirrors.tuna.tsinghua.edu.cn/ubuntu bionic-security InRelease
命中:6 http://mirrors.tuna.tsinghua.edu.cn/ros/ubuntu bionic InRelease
命中:7 http://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu bionic InRelease
命中:8 https://packages.microsoft.com/repos/edge stable InRelease
命中:9 http://ppa.launchpad.net/ubuntu-mozilla-security/ppa/ubuntu bionic InRelease
命中:10 http://ppa.launchpad.net/peek-developers/stable/ubuntu bionic InRelease
命中:11 https://download.docker.com/linux/ubuntu bionic InRelease
正在读取软件包列表... 完成
```

**安装 Docker**

安装

```shell
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
```

把当前用户加入 docker 组

```shell
sudo usermod -aG docker $USER   # $USER 即当前用户名
newgrp docker                   # 让当前 shell 立即生效，无需重启
```

测试是否安装成功

```shell
sudo systemctl daemon-reload
sudo systemctl restart docker
docker run hello-world
```

弹出 `Hello from Docker!` 即安装成功

## 参考

- [ubuntu 安装 Docker（超级详细，常见错误解决方案也有附上）（军师不上战场，上了就是小丑王，都是笔者自己踩过的坑，）](https://blog.csdn.net/Apricity_L/article/details/137064982)

- [Docker 完整安装与使用入门教程（ubuntu18.04）2023 年](https://zhuanlan.zhihu.com/p/657300467)

```

```
