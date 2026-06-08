<div align="center">

# 🧠 智能传媒内容分析与推荐系统

**Smart Media Content Analysis & Recommendation System**

基于 FastAPI + Vue 3 的全栈智能传媒平台，集成新闻采集、内容分析、个性化推荐与管理后台

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vue 3](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[功能演示](#-功能一览) · [快速开始](#-快速开始) · [技术架构](#-技术架构) · [API 文档](#-api-一览)

</div>

---

## ✨ 功能一览

<table>
<tr>
<td width="50%">

### 🔐 认证与权限
- JWT Token 登录认证
- 四级角色权限控制（Admin / Editor / Auditor / Viewer）
- 账号禁用实时拦截
- 前端菜单动态渲染

</td>
<td width="50%">

### 📰 新闻采集
- 内置 RSS 新闻源
- 自定义 RSS 地址
- 采集内容自动入库
- 操作审计日志记录

</td>
</tr>
<tr>
<td width="50%">

### 📝 内容管理
- 内容 CRUD 全流程
- 封面图 / 文件关联
- 内容状态生命周期管理
- 来源链接追踪

</td>
<td width="50%">

### 🤖 智能内容分析
- 自动摘要生成
- 关键词提取（jieba）
- 分类识别 & 情感判断
- 敏感词检测 & 热度/质量评分
- 相似内容推荐（TF-IDF + 余弦相似度）

</td>
</tr>
<tr>
<td width="50%">

### ✅ 内容审核
- 待审核内容队列
- 通过 / 拒绝 / 下架
- 审核意见填写
- 敏感词命中展示

</td>
<td width="50%">

### 👤 用户画像
- 兴趣标签权重计算
- 负向兴趣标签
- 分类偏好分布
- 行为类型统计 & 活跃度评分

</td>
</tr>
<tr>
<td width="50%">

### 🎯 个性化推荐
- 基于用户画像的协同过滤
- 基于内容的相似度推荐
- 热度 + 新鲜度混合排序
- 已看内容去重 & CTR 分析

</td>
<td width="50%">

### 📊 数据看板
- 系统指标总览
- 内容 / 用户 / 行为统计
- 推荐效果分析（CTR / 曝光 / 点击）
- 热门内容排行
- ECharts 可视化图表

</td>
</tr>
</table>

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────┐
│                    Frontend                          │
│   Vue 3 · Vite · Element Plus · ECharts · Pinia     │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP / REST API
┌──────────────────────▼──────────────────────────────┐
│                    Backend                           │
│              FastAPI · SQLAlchemy · JWT              │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │  API Layer  │ │  Algorithms  │ │   Services   │  │
│  │  RESTful    │ │  Recommender │ │   Business   │  │
│  │  Router     │ │  Analyzer    │ │   Logic      │  │
│  └──────┬──────┘ └──────┬───────┘ └──────┬───────┘  │
│         └───────────────┼────────────────┘          │
│                    ┌────▼─────┐                      │
│                    │   Data   │                      │
│                    │  Layer   │                      │
│                    │ SQLite   │                      │
│                    └──────────┘                      │
└─────────────────────────────────────────────────────┘
```

### 技术栈详情

| 层级 | 技术 | 说明 |
|:---:|:---|:---|
| **前端框架** | Vue 3 + Vite 6 | Composition API + 响应式开发 |
| **UI 组件** | Element Plus | 企业级 Vue 3 组件库 |
| **状态管理** | Pinia | 轻量级状态管理 |
| **数据可视化** | ECharts 5 | 图表与数据看板 |
| **后端框架** | FastAPI 0.115 | 高性能异步 Python Web 框架 |
| **ORM** | SQLAlchemy 2.0 | 数据库操作与模型定义 |
| **数据库** | SQLite | 轻量级嵌入式数据库 |
| **认证** | python-jose + passlib | JWT + bcrypt 密码哈希 |
| **NLP** | jieba + scikit-learn | 中文分词、TF-IDF、余弦相似度 |

---

## 📁 项目结构

```
smart-media-analysis/
├── backend/                    # 🐍 FastAPI 后端
│   ├── app/
│   │   ├── algorithms/         # 推荐算法 & 内容分析
│   │   ├── api/                # RESTful API 路由
│   │   ├── core/               # 配置 & 通用响应
│   │   ├── db/                 # 数据库 & 种子数据
│   │   ├── models/             # SQLAlchemy 数据模型
│   │   ├── schemas/            # Pydantic 请求/响应模式
│   │   └── services/           # 业务逻辑层
│   ├── scripts/                # 数据库初始化脚本
│   └── requirements.txt
├── frontend/                   # 🖼️ Vue 3 前端
│   ├── src/
│   │   ├── api/                # API 请求封装
│   │   ├── components/         # 公共组件
│   │   ├── router/             # 路由配置
│   │   ├── stores/             # Pinia 状态
│   │   ├── styles/             # 全局样式
│   │   └── views/              # 页面视图
│   └── package.json
└── scripts/                    # 🚀 一键启动脚本
    ├── setup_local.ps1         # 初始化环境
    ├── start_backend.ps1       # 启动后端
    └── start_frontend.ps1      # 启动前端
```

---

## 🚀 快速开始

### 环境要求

| 依赖 | 版本 |
|:---:|:---:|
| Python | 3.10+ |
| Node.js | 18+ |
| npm | 9+ |
| OS | Windows 10/11 |

### 一键初始化

```powershell
git clone https://github.com/Geoffrey-png/smart-media-analysis.git
cd smart-media-analysis
powershell -ExecutionPolicy Bypass -File .\scripts\setup_local.ps1
```

脚本会自动完成：创建虚拟环境 → 安装后端依赖 → 播种演示数据 → 安装前端依赖

### 启动项目

打开两个终端分别运行：

```powershell
# 终端 1 — 启动后端
powershell -ExecutionPolicy Bypass -File .\scripts\start_backend.ps1

# 终端 2 — 启动前端
powershell -ExecutionPolicy Bypass -File .\scripts\start_frontend.ps1
```

| 服务 | 地址 |
|:---|:---|
| 🖥️ 前端页面 | http://localhost:5173 |
| 🔧 管理后台 | http://localhost:5173/admin |
| 📡 后端 API | http://localhost:8000 |
| 📖 API 文档 | http://localhost:8000/docs |

---

## 🔑 演示账号

| 用户名 | 密码 | 角色 | 权限说明 |
|:---:|:---:|:---:|:---|
| `tech_user` | `demo` | 🔴 Admin | 完整后台权限 |
| `finance_user` | `demo` | 🟡 Editor | 采集、编辑、分析 |
| `ent_user` | `demo` | 🟠 Auditor | 审核、日志查看 |
| `sports_user` | `demo` | 🟢 Viewer | 浏览、点赞、推荐 |
| `life_user` | `demo` | 🟢 Viewer | 浏览、点赞、推荐 |

---

## 📡 API 一览

<details>
<summary>🖱️ 点击展开完整 API 列表</summary>

```
认证
  POST   /api/auth/login              登录
  GET    /api/auth/me                 当前用户信息

管理后台
  GET    /api/admin/summary            系统概览
  GET    /api/admin/logs               操作审计日志
  GET    /api/admin/roles              角色选项

用户管理
  GET    /api/users                    用户列表
  POST   /api/users                    新增用户
  PUT    /api/users/{id}               修改用户
  DELETE /api/users/{id}               删除用户
  GET    /api/users/{id}/profile       用户画像

内容管理
  GET    /api/contents                 内容列表
  POST   /api/contents                 新增内容
  PUT    /api/contents/{id}            编辑内容
  DELETE /api/contents/{id}            删除内容
  POST   /api/contents/{id}/analyze    智能分析
  GET    /api/contents/audit/pending   待审核列表
  POST   /api/contents/{id}/audit      内容审核

新闻采集
  GET    /api/news/sources             新闻源列表
  POST   /api/news/import              采集新闻

行为记录
  POST   /api/behaviors               写入行为
  GET    /api/behaviors                行为日志

推荐引擎
  GET    /api/recommendations/user/{id}       个性化推荐
  GET    /api/recommendations/mixed/{id}      混合推荐
  GET    /api/recommendations/analytics/summary  推荐分析

文件上传
  POST   /api/uploads                  上传文件

数据看板
  GET    /api/dashboard/summary        看板总览
  GET    /api/dashboard/content-stats  内容统计
  GET    /api/dashboard/behavior-stats 行为统计
```

</details>

---

## 🧩 推荐算法

系统采用 **混合推荐策略**，融合多种信号源：

| 策略 | 方法 | 权重因子 |
|:---:|:---|:---|
| **协同过滤** | 基于用户画像兴趣标签匹配内容标签 | 兴趣权重、负反馈衰减 |
| **内容相似** | TF-IDF 向量化 + 余弦相似度 | 内容标签重叠度 |
| **热度排序** | 浏览量 / 点赞数 / 质量分加权 | 热度分、质量分 |
| **时间衰减** | 发布时间新鲜度因子 | 指数时间衰减 |

最终排序 = `画像匹配分 × α + 热度分 × β + 新鲜度 × γ`，并对已看内容去重。

---

## ❓ 常见问题

<details>
<summary>前端访问不了？</summary>

确认前端服务已启动：http://localhost:5173  
端口被占用时，关闭旧 Vite 进程后重新运行启动脚本。
</details>

<details>
<summary>管理员后台看不到？</summary>

需使用管理员账号 `tech_user / demo` 登录。如果之前登录过普通用户，先退出再重新登录。
</details>

<details>
<summary>如何重置演示数据？</summary>

```powershell
# 完全重置（清空 + 重新播种）
cd backend && .\.venv\Scripts\python scripts\init_db.py

# 安全模式（仅空库时播种，不覆盖已有数据）
.\.venv\Scripts\python scripts\init_db.py --safe
```
</details>

---

## 📄 License

本项目仅供学习与实训使用，基于 [MIT License](LICENSE) 开源。

<div align="center">

**Made with ❤️ by [Geoffrey-png](https://github.com/Geoffrey-png)**

</div>
