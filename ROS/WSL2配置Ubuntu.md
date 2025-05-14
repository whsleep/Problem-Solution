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


