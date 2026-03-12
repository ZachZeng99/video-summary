# Video Summary

> 自动提取 YouTube 和 Bilibili 视频字幕并生成结构化总结。

## 功能特点

| 特性 | 说明 |
|------|------|
| 多平台支持 | YouTube 和 Bilibili |
| 字幕提取 | 自动提取视频字幕 / CC 字幕 |
| 智能分段 | 支持长视频分段总结 |
| 结构化输出 | 概述、分段要点、核心观点、关键词 |

## 快速开始

### 第一步：安装依赖

```bash
pip install -r scripts/requirements.txt
```

依赖包：

- `yt-dlp` — YouTube 视频提取
- `youtube-transcript-api` — YouTube 字幕备用方案
- `bilibili-api-python` — Bilibili API 接口
- `requests` — HTTP 请求

### 第二步：配置 Bilibili 认证

- **YouTube 视频**：无需配置，直接使用
- **Bilibili 视频**：需要先配置 SESSDATA

#### 获取 SESSDATA

**方法一（推荐）**：访问 [bilibili-api 文档](https://nemo2011.github.io/bilibili-api/#/get-credential) 按说明操作。

**方法二（手动获取）**：

1. 打开 Chrome/Edge，访问 [bilibili.com](https://www.bilibili.com) 并登录
2. 按 `F12` 打开开发者工具
3. 进入 **Application → Storage → Cookies → `https://www.bilibili.com`**
4. 找到 **SESSDATA**，复制其 Value

#### 写入配置文件

创建 `config/auth.json`：

```json
{
  "sessdata": "你的SESSDATA值",
  "platform": "bilibili"
}
```

### 第三步：开始使用

像普通 skill 一样使用，例如：

```
帮我总结一下 https://www.bilibili.com/video/BV1k44mzWEvq
```
