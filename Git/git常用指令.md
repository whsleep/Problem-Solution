# 常用指令

## 配置用户名和 📫

```shell
# 全局配置用户名和邮箱
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

## 查看用户名和 📫

```shell
git config --list
```

## 仓库初始化和克隆

```shell
# 初始化本地仓库
git init
# 克隆远程仓库
git clone <仓库URL>
```

## 查看工作区状态

```shell
# 查看工作区状态
git status
```

会弹出以下信息

```shell
# 当前分支名（如 main 或 dev）
On branch feature-auth 
# 与远程分支的同步状态：
Your branch is ahead of 'origin/feature-auth' by 2 commits.
  (use "git push" to publish your local commits)
# 暂存区（Staged）状态
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        modified:   login.js
        new file:   auth.js
# 工作区（未暂存）状态
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes)
        modified:   README.md
#  未跟踪的新文件
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        debug.log
```

## 修改保存暂存区

假设修改了 `robot_world.yaml`

```shell
git add robot_world.yaml
```

> ```shell
> git add .
> ```
> 会自动将修改过的所有内容保存到暂存区

可以使用 `git status` 查看当前状态

```shell
$ git status
On branch main
Your branch is up to date with 'origin/main'.

Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        modified:   robot_world.yaml
```

可以看到 `robot_world.yam` 已经进入暂存区了

## 删除暂存区内容

```shell
# 指定文件
git reset HEAD robot_world.yaml
# 一次撤销所有修改 
git reset HEAD
```

可以使用 `git status` 查看当前状态

```shell
$ git status
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   robot_world.yaml

no changes added to commit (use "git add" and/or "git commit -a")
```

可以看到 `robot_world.yam` 暂存区内容以被删除

## 查看暂存区内容

```shell
git diff --cached
```

假设 `robot_world.yam` 的修改已经保存暂存区

```shell
$ git diff --cached
diff --git a/robot_world.yaml b/robot_world.yaml
index ec78b10..12a2d6d 100644
--- a/robot_world.yaml
+++ b/robot_world.yaml
@@ -22,7 +22,7 @@ robot:
         range_min: 0
         range_max: 4
         angle_range: 6.28
-        number: 360
+        number: 100
         noise: True
         std: 0.02
         angle_std: 0.05
```

可以看到本次代码中的修改内容

## 查看提交历史

```shell
# 简洁显示
git log --oneline
# 分支图
git log --graph --all    
```

```shell
$ git log --oneline
162a69d (HEAD -> main, origin/main, origin/HEAD) fix
c200843 Merge commit '2be79606113fb315a44c813b90685a29d8300f7d' into main
2be7960 add global plan
aa0cd73 add random obs
82bf041 add lidar sim
0c7f2bb 2025-7-18
9fdde8f add robotfootprint
e967196 add polygon obstacles
0e38db5 update README,md
bc39fed the first avaiable version
5a29b80 compute_currentGoal
3d36167 new version
f33cf77 first version
1929941 add g2opy example
791ad80 first commit
522ee1f Initial commit
```

可以看到我每次提交的 "哈希值"（commit hash）和 "commit" 内容

## 分支操作

### 查看分支

```shell
# 查看分支
git branch               # 本地分支
git branch -r            # 远程分支
git branch -a            # 所有分支
```

本地分支为保存在本地并未发布的分支，远程分支为已经发布在服务器的分支

```shell
$ git branch 
  dev
* main
$ git branch -r
  origin/HEAD -> origin/main
  origin/dev
  origin/main
$ git branch -a
  dev
* main
  remotes/origin/HEAD -> origin/main
  remotes/origin/dev
  remotes/origin/main
```

### 切换到分支

```shell
# 创建并切换到新分支
git checkout -b <分支名>
# 切换分支
git checkout <分支名>
```

以下步骤为 切换 `dev` 分支 ， 创建并切换 `test` 分支

```shell
$ git checkout dev 
Switched to branch 'dev'
Your branch is up to date with 'origin/dev'.
$ git checkout -b test
Switched to a new branch 'test'
$ git branch 
  dev
  main
* test
```

⚠️ **Git 创建新分支时默认是以 HEAD 当前指向的提交为起点（即以当前分支为“副本”）, 这里是以 `dev` 分支为副本创建 `test` 分支**

### 合并分支

这里将 `main` 分支合并到 `test` 分支 

```shell
git merge <要合并的分支>
```

```shell
$ git merge main 
Auto-merging sim.py
CONFLICT (content): Merge conflict in sim.py
Auto-merging robot_world.yaml
CONFLICT (content): Merge conflict in robot_world.yaml
Auto-merging TebSolver.py
CONFLICT (content): Merge conflict in TebSolver.py
Auto-merging README.md
CONFLICT (content): Merge conflict in README.md
Automatic merge failed; fix conflicts and then commit the result.
$ git add .
$ git status
On branch test
All conflicts fixed but you are still merging.
  (use "git commit" to conclude merge)

Changes to be committed:
        modified:   README.md
        modified:   TebSolver.py
        modified:   robot_world.yaml
        modified:   sim.py

```

合并后的冲突需要手动解决，解决后需要保存到暂存区并提交修改

### 删除分支

```shell
# 删除分支
git branch -d <分支名>   # 安全删除（检查是否已合并）
git branch -D <分支名>   # 强制删除
```

删除 `test` 分支

```shell
$ git branch -d test 
error: Cannot delete branch 'test' checked out at '/home/anin/Documents/Minimal_TEB'

$ git checkout main 
Switched to branch 'main'
Your branch is up to date with 'origin/main'.

$ git branch -d test 
error: The branch 'test' is not fully merged.
If you are sure you want to delete it, run 'git branch -D test'.

$ git branch -D test 
Deleted branch test (was 0c1752a).

$ git branch 
  dev
* main
```

⚠️ **注意：不能删除你当前所在分支，需要切换到其他分支再删除。**

## 远程操作

```shell
# 关联远程仓库
git remote add origin <仓库URL>

# 拉取远程更新
git pull origin <分支名>

# 推送本地分支到远程
git push origin <分支名>

# 首次推送本地分支到远程
git push -u origin <分支名>

# 查看远程仓库信息
git remote -v
```

## 撤销与回退

```shell
# 撤销工作区修改（未add）
git checkout -- <文件名>

# 撤销暂存区文件（已add未commit）
git reset HEAD <文件名>

# 回退到上一个提交（保留工作区修改）
git reset --soft HEAD^

# 彻底回退（丢弃所有修改）
git reset --hard HEAD^

# 回退到指定提交
git reset --hard <提交ID>
```