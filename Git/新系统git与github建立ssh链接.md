# 新系统git与github建立ssh链接

## 参考

[新电脑安装Git并建立与GitHub的ssh连接（好记性不如烂笔头~）](https://blog.csdn.net/Gabriel_wei/article/details/122270707)

## 先决条件

### `git` 检测

```shell
git --version
# 如未安装请使用以下指令安装
sudo apt update
sudo apt install git
```

## 设置 `git` 用户信息

⚠️ **注意：`your_Email_to_sign_up_for_github` 必须为你注册`github`的邮箱。**

```shell
git config --global user.name your_computer_name
git config --global user.email your_Email_to_sign_up_for_github

# 输入以下指令检测是否配置成功，终端返回配置信息即成功
git config --global user.name
git config --global user.email
```

## 配置 `ssh`

```shell
ssh-keygen -t rsa -C "your_Email_to_sign_up_for_github"
```

⚠️ **注意：终端提示选项默认 `enter` 即可。**

## 将公钥设置到 `GitHub`

按照以下选项进入公匙设置或者直接点击[此处](https://github.com/settings/ssh/new)进入

`settings` $\rightarrow$ `SSH and GPG keys` $\rightarrow$ `New SSH key`

#### `Title`

🎗️ **这里 `Title` 尽量配置自己明白的内容，我将其配置为 `WSL2_Ubuntu20.04`，你可以自定义你需要的内容。** 

#### `Key`

终端输入 

```shell
vim ~/.ssh/id_rsa.pub
```
 
复制 `id_rsa.pub` 所有内容，按下 `esc`后输入 `:q` 退出 `id_rsa.pub`。

将复制内容全部粘贴到 `Key` 编辑框中。

最后，点击 `Add SSH key`保存即可。

## 验证配置

终端输入

```shell
ssh -T git@github.com
```

> ⚠️ 注意：首次链接会出现 
>
> ```shell
> Are you sure you want to continue connecting (yes/no/[fingerprint])?
> ```
> 输入 `yes` 即可

链接成功终端会返回 

```shell
Hi whsleep! You've successfully authenticated, but GitHub does not provide shell access.
```

