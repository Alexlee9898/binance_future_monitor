# GitHub设置和推送指南

## 📋 步骤1：在本地创建Git仓库

请在您的Mac上执行以下命令（在刚才创建的trading-bot-aliyun目录中）：

```bash
cd /Users/vadar/Cursor file/trading bot/trading-bot-aliyun

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交更改
git commit -m "Initial commit: Trading bot for Aliyun deployment"

# 查看状态
git status
```

## 📋 步骤2：创建GitHub仓库

### 选项A：网页创建（推荐新手）
1. 打开浏览器访问：https://github.com/new
2. 输入仓库名称：`trading-bot-aliyun`
3. 添加描述：`币安持仓监控机器人 - 阿里云部署版`
4. 选择Public或Private
5. **不要**勾选"Initialize this repository with a README"
6. 点击"Create repository"

### 选项B：使用GitHub CLI（如果您已安装）
```bash
# 如果已安装GitHub CLI
gh repo create trading-bot-aliyun --public --description "币安持仓监控机器人 - 阿里云部署版"
```

## 📋 步骤3：推送到GitHub

创建仓库后，GitHub会显示推送命令。请执行：

```bash
# 添加远程仓库（替换为您的实际用户名）
git remote add origin https://github.com/YOUR_USERNAME/trading-bot-aliyun.git

# 推送到GitHub
git push -u origin main
```

**注意**：如果提示需要身份验证，您可能需要：
1. 使用GitHub用户名和密码
2. 或者使用Personal Access Token
3. 或者配置SSH密钥

## 📋 步骤4：验证推送

```bash
# 检查远程仓库
git remote -v

# 查看分支
git branch -a

# 检查提交历史
git log --oneline -5
```

## 📋 步骤5：在阿里云服务器上克隆

### 在您的阿里云服务器上执行：

```bash
# 确保已安装Git
yum install -y git

# 进入主目录
cd ~

# 克隆仓库
git clone https://github.com/YOUR_USERNAME/trading-bot-aliyun.git

# 进入项目目录
cd trading-bot-aliyun

# 查看文件
ls -la
```

## 📋 步骤6：完成部署

### 在服务器上完成部署：

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置Telegram
vim telegram_config.py

# 测试运行
./start_bot.sh test

# 生产部署
./start_bot.sh production
```

## 🔧 GitHub Personal Access Token创建指南

如果遇到身份验证问题，请创建Personal Access Token：

1. 访问：https://github.com/settings/tokens
2. 点击"Generate new token"
3. 选择过期时间（建议90天或更长）
4. 勾选权限：
   - ✅ repo (Full control of private repositories)
   - ✅ workflow (Update GitHub Action workflows)
5. 点击"Generate token"
6. **立即复制token**（只显示一次）

使用token代替密码：
```bash
# 当推送时提示输入密码，使用token
Username: YOUR_USERNAME
Password: YOUR_PERSONAL_ACCESS_TOKEN
```

## 📋 常见问题和解决方案

### 1. 推送被拒绝
```bash
# 如果提示推送被拒绝，先拉取再推送
git pull origin main --allow-unrelated-histories
git push origin main
```

### 2. 分支名称问题
```bash
# 如果默认分支是master而不是main
git branch -M master main
git push -u origin main
```

### 3. 大文件问题
如果文件太大，考虑添加.gitignore：
```bash
echo "*.log" > .gitignore
echo "*.db" >> .gitignore
echo "__pycache__/" >> .gitignore
git add .gitignore
git commit -m "Add gitignore"
git push
```

### 4. 网络问题
如果推送失败，可能是网络问题：
```bash
# 尝试增加超时时间
git config --global http.postBuffer 524288000
git push origin main
```

## 📋 验证GitHub仓库

推送成功后，请访问：
```
https://github.com/YOUR_USERNAME/trading-bot-aliyun
```

您应该能看到所有文件都已上传到GitHub。

## 🎯 下一步

完成GitHub推送后，请告诉我：
1. ✅ GitHub仓库是否创建成功？
2. ✅ 文件是否推送成功？
3. ✅ 仓库地址是什么？

然后我将指导您在阿里云服务器上克隆和部署！

## 📞 遇到问题？

如果在上传过程中遇到任何问题，请告诉我：
- 具体的错误信息
- 您执行到哪一步
- 任何报错提示

我会协助您解决问题！

---

🚀 **准备好开始GitHub推送了吗？**