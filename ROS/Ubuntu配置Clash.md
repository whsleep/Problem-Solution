## Ubuntu 配置 `clash`

## 参考

[Ubuntu 使用 Clash For Linux 客户端](https://www.zywvvd.com/notes/tools/clash/ubuntu-clash-usage/ubuntu-clash-usage/)

## 下载

[Clash-Premium](https://github.com/DustinWin/proxy-tools/releases/tag/Clash-Premium)

选择 `clashpremium-release-linux-amd64.tar.gz` 版本

放置到指文件夹，

✨**这里我在用户目录下新建 `clash` 文件夹放置压缩包**

```shell
cd ~
mkdir clash
```

## 解压&重命名

```shell
cd ~
cd clash
tar -zxvf clashpremium-release-linux-amd64.tar.gz

# 给予权限
chmod +x CrashCore

# 重命名
mv CrashCore clash

# 查看版本
./clash -v
```

终端输出版本号即正常。

## 配置

**⚠ 注意：考虑到 `ubuntu` 还未配置成功，建议在可以科学上网的系统上准备好下面两个文件。**

### `Country.mmdb`

[Country.mmdb](https://gitee.com/mirrors/Pingtunnel/blob/master/GeoLite2-Country.mmdb)

⚠ 注意：下载后重命名为 `Country.mmdb`。

### `config.yaml`

需要到你自己使用的机场网站，或者客户端下载配置文件。

⚠ 注意：下载后重命名为 `config.yaml`。

### `.config` 配置

将上述 `Country.mmdb` 和 `config.yaml` 拷贝到 `clash`文件夹

```shell
cd ~
cd clash
mv Country.mmdb ~/.config/clash/
mv config.yaml ~/.config/clash/
```

### `.bashrc` 配置

打开 `.bashrc` 将以下内容填入

```shell
export http_proxy="http://127.0.0.1:7890"
export HTTP_PROXY="http://127.0.0.1:7890"
export https_proxy="http://127.0.0.1:7890"
export HTTPS_PROXY="http://127.0.0.1:7890"
```

### 设置界面 `NetWork` 配置

输入指令打开设置-网络界面

```shell
gnome-control-center network
```

将 `Network Proxy` 参考 [Ubuntu 使用 Clash For Linux 客户端](https://www.zywvvd.com/notes/tools/clash/ubuntu-clash-usage/ubuntu-clash-usage/) **网络代理** 进行修改。



## 启动

新建终端

```shell
cd ~
cd clash
./clash
```

⚠ 注意：启动终端不要关闭。

### 验证

新建终端

```shell
curl -x http://127.0.0.1:7890 http://ipinfo.io/json
```

返回代理信息即成功。

可进入 [clash](https://clash.razord.top/#/proxies) 进行界面管理。

### 开启 `clash` 后无法访问国内网站

将 `~/.config/clash/config.yaml` 文件中的 `dns` 替换为以下内容

```shell
dns:
  enable: true
  ipv6: false
  default-nameserver: [223.5.5.5, 119.29.29.29, 114.114.114.114]
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.1/16
  use-hosts: true
  nameserver:
    - 223.5.5.5
    - 119.29.29.29
    - 114.114.114.114
```

保存后重新打开 `clash` 进行测试。
