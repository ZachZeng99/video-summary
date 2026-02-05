# Video Summary - 视频内容总结工具

自动提取 YouTube 和 Bilibili 视频字幕并生成结构化总结。

## ✨ 功能特点

- 🎬 支持 YouTube 和 Bilibili 双平台
- 📝 自动提取视频字幕/CC字幕
- 🧠 智能分段总结（支持长视频）
- 📊 生成结构化报告（概述、分段要点、核心观点、关键词）
- 🔒 本地保存认证信息，安全可靠

## 🚀 快速开始

### 1. 安装依赖
欠缺的Agent应该会自己安装

```bash
pip install -r scripts/requirements.txt
```

依赖清单：
- `yt-dlp` - YouTube 视频提取
- `bilibili-api-python` - Bilibili API 接口
- `requests` - HTTP 请求

### 2. 配置 Bilibili 认证（非常重要，必须配置）

**⚠️ 重要提示**

- **YouTube 视频**：无需配置，直接使用
- **Bilibili 视频**：需要先获取 SESSDATA 并配置

#### 获取 SESSDATA

**方法 1：使用文档（推荐）**
1. 访问：https://nemo2011.github.io/bilibili-api/#/get-credential
2. 按照页面说明操作
3. 复制获取到的 SESSDATA

**方法 2：手动获取**
1. 打开 Chrome/Edge 浏览器
2. 访问 https://www.bilibili.com 并**登录**你的账号
3. 按 `F12` 打开开发者工具
4. 点击 **Application** (应用) 标签
5. 左侧找到 **Storage** → **Cookies** → `https://www.bilibili.com`
6. 在右侧列表中找到 **SESSDATA** 行
7. 双击 Value 列的值，复制完整内容

#### 配置认证

创建 `config/auth.json` 文件：

```json
{
  "sessdata": "你的SESSDATA值粘贴到这里",
  "platform": "bilibili"
}
```

**提示**：首次使用 Bilibili 功能时，请务必先配置 SESSDATA！

### 3.完成！像使用普通skill一样使用它！
  例如：帮我总结一下 https://www.bilibili.com/video/BV1k44mzWEvq
