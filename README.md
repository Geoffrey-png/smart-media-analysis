# 智能传媒内容分析与推荐系统

一个基于 **Python FastAPI + Vue 3** 的智能传媒内容分析与推荐系统。系统支持新闻内容采集、内容分析、用户行为记录、用户画像更新、个性化推荐、内容审核和真实管理员后台。

## 1. 技术栈

### 后端

- Python
- FastAPI
- SQLAlchemy
- SQLite
- JWT 登录认证
- jieba / scikit-learn 作为演示级文本分析与推荐算法基础

### 前端

- Vue 3
- Vite
- Element Plus
- ECharts
- Pinia
- Vue Router

## 2. 项目目录

```text
智能传媒内容分析与推荐系统/
├─ backend/                 后端 FastAPI 项目
│  ├─ app/                  后端业务代码
│  ├─ data/                 SQLite 数据库目录
│  ├─ uploads/              上传文件目录
│  ├─ scripts/init_db.py    初始化演示数据脚本
│  ├─ requirements.txt      Python 依赖
│  └─ .venv/                Python 虚拟环境，放在项目内
├─ frontend/                前端 Vue 项目
│  ├─ src/                  前端源码
│  ├─ node_modules/         前端依赖，放在项目内
│  └─ package.json
├─ scripts/                 启动和初始化脚本
│  ├─ setup_local.ps1       一键安装依赖并初始化数据
│  ├─ start_backend.ps1     启动后端
│  └─ start_frontend.ps1    启动前端
├─ .cache/                  pip / npm 缓存，放在项目内
├─ AI_CODING_开发提示词.md
└─ README.md
```

## 3. 本地依赖位置

本项目按要求把运行环境和缓存都放在项目目录内：

```text
backend/.venv/                  Python 虚拟环境
backend/data/smart_media.db     SQLite 数据库
backend/uploads/                上传文件
frontend/node_modules/          前端依赖
.cache/pip/                     pip 下载缓存
.cache/npm/                     npm 下载缓存
```

## 4. 运行环境要求

建议环境：

- Windows 10/11
- Python 3.10+
- Node.js 18+
- npm
- PowerShell

## 5. 首次初始化 ← 答辩前必做

进入项目根目录，执行**一键初始化**：

```powershell
cd E:\code\2026实训\智能传媒内容分析与推荐系统
powershell -ExecutionPolicy Bypass -File .\scripts\setup_local.ps1
```

该脚本会做这些事：

1. 创建 `backend/.venv/` 虚拟环境。
2. 安装 Python 后端依赖。
3. 初始化 SQLite 演示数据库（30 条内容、5 个用户、120 条行为数据）。
4. 安装前端 npm 依赖到 `frontend/node_modules/`。
5. 使用项目内 `.cache/` 作为 pip / npm 缓存目录。

### 5.1 自动播种保护

后端启动时会自动检测数据库是否为空：
- **空库首次启动** → 自动播种演示数据，无需额外操作。
- **已有数据** → 跳过播种，不会覆盖你的业务数据。

> 注意：`setup_local.ps1` 中的 `backend/scripts/init_db.py` 默认会**重置**演示数据库。
> 如果已经产生了自己的数据，不要重复执行初始化脚本。

## 6. 启动项目

需要打开两个 PowerShell 终端。

### 6.1 启动后端

```powershell
cd E:\code\2026实训\智能传媒内容分析与推荐系统
powershell -ExecutionPolicy Bypass -File .\scripts\start_backend.ps1
```

后端默认地址：

```text
http://localhost:8000
```

API 文档：

```text
http://localhost:8000/docs
```

### 6.2 启动前端

```powershell
cd E:\code\2026实训\智能传媒内容分析与推荐系统
powershell -ExecutionPolicy Bypass -File .\scripts\start_frontend.ps1
```

前端默认地址：

```text
http://localhost:5173
```

管理员后台地址：

```text
http://localhost:5173/admin
```

## 7. 手动运行方式

如果不使用脚本，也可以手动运行。

### 7.1 后端

```powershell
cd E:\code\2026实训\智能传媒内容分析与推荐系统\backend
.\.venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7.2 前端

```powershell
cd E:\code\2026实训\智能传媒内容分析与推荐系统\frontend
npm run dev
```

### 7.3 前端构建检查

```powershell
cd E:\code\2026实训\智能传媒内容分析与推荐系统\frontend
npm run build
```

## 8. 演示账号

| 用户名 | 密码 | 角色 | 说明 |
|---|---|---|---|
| `tech_user` | `demo` | 管理员 `admin` | 拥有完整后台权限 |
| `finance_user` | `demo` | 编辑 `editor` | 可采集新闻、编辑内容、分析内容 |
| `ent_user` | `demo` | 审核员 `auditor` | 可审核内容、查看部分日志和统计 |
| `sports_user` | `demo` | 观察者 `viewer` | 浏览内容、点赞、查看自己的推荐 |
| `life_user` | `demo` | 观察者 `viewer` | 浏览内容、点赞、查看自己的推荐 |

## 9. 主要功能

### 9.1 登录认证与角色权限

- JWT 登录认证。
- 后端接口做真实权限校验。
- 前端根据角色动态显示菜单。
- 支持四类角色：
  - `admin`：管理员
  - `editor`：编辑
  - `auditor`：审核员
  - `viewer`：普通用户 / 观察者

### 9.2 真正的管理员后台

访问地址：

```text
http://localhost:5173/admin
```

管理员后台支持：

- 系统指标总览。
- 用户数量统计。
- 账号正常 / 禁用状态统计。
- 内容总数统计。
- 待审核内容统计。
- 用户行为日志统计。
- 操作审计日志统计。
- 角色分布统计。
- 内容状态分布统计。
- 新闻来源分布统计。
- 后台操作日志查询。

### 9.3 用户管理

管理员可以：

- 查看用户列表。
- 搜索用户。
- 按角色筛选。
- 按账号状态筛选。
- 新增用户。
- 修改用户资料。
- 修改用户角色。
- 禁用 / 启用账号。
- 删除用户。
- 查看用户画像。

账号被禁用后：

- 不能重新登录。
- 已有 Token 访问接口也会被后端拦截。

### 9.4 新闻采集

系统支持从 RSS 新闻源采集内容，包括：

- 内置新闻源。
- 自定义 RSS 地址。
- 新闻标题、摘要、来源、发布时间、原文链接入库。
- 采集后的新闻进入内容资产库。
- 采集操作会写入操作审计日志。

### 9.5 内容管理

支持：

- 内容列表。
- 内容详情。
- 新增内容。
- 编辑内容。
- 删除内容。
- 内容状态管理。
- 来源链接查看。
- 封面图 / 上传文件关联。

### 9.6 智能内容分析

支持对内容做演示级分析：

- 自动摘要。
- 关键词提取。
- 分类识别。
- 情感判断。
- 敏感词识别。
- 热度分计算。
- 质量分计算。
- 相似内容推荐。

### 9.7 内容审核

审核员和管理员可以：

- 查看待审核内容。
- 通过内容。
- 拒绝内容。
- 下架内容。
- 填写审核意见。
- 查看敏感词命中情况。

### 9.8 用户行为记录

系统会记录用户行为：

- 浏览 `view`
- 点赞 `like`
- 收藏 `favorite`
- 评论 `comment`
- 分享 `share`
- 不喜欢 `dislike`

用户浏览和点赞内容后，会影响：

- 内容浏览数 / 点赞数。
- 用户活跃度。
- 用户兴趣标签。
- 用户画像向量。
- 后续推荐结果。

### 9.9 用户画像

系统根据用户行为动态生成画像：

- 兴趣标签权重。
- 负向兴趣标签。
- 分类偏好分布。
- 行为类型统计。
- 最近行为内容。
- 活跃分。

### 9.10 个性化推荐

推荐逻辑综合考虑：

- 用户画像兴趣标签。
- 用户负反馈。
- 内容分类。
- 内容标签。
- 内容热度。
- 内容质量分。
- 发布时间新鲜度。
- 用户已看内容去重。

支持：

- 用户个性化推荐。
- 混合推荐。
- 热门推荐。
- 推荐点击记录。
- 推荐效果分析。

### 9.11 数据看板与统计

系统提供：

- 总览看板。
- 内容统计。
- 用户行为统计。
- 推荐效果统计。
- CTR / 曝光 / 点击分析。
- 热门内容排行。

### 9.12 文件上传

支持编辑上传内容相关文件，文件默认存储在：

```text
backend/uploads/
```

## 10. 常用接口

```text
POST /api/auth/login                         登录
GET  /api/auth/me                            当前用户

GET  /api/admin/summary                      管理员后台概览
GET  /api/admin/logs                         操作审计日志
GET  /api/admin/roles                        角色选项

GET  /api/users                              用户列表，管理员
POST /api/users                              新增用户，管理员
PUT  /api/users/{id}                         修改用户，管理员
DELETE /api/users/{id}                       删除用户，管理员
GET  /api/users/{id}/profile                 用户画像

GET  /api/contents                           内容列表
POST /api/contents                           新增内容，管理员 / 编辑
PUT  /api/contents/{id}                      编辑内容，管理员 / 编辑
DELETE /api/contents/{id}                    删除内容，管理员
POST /api/contents/{id}/analyze              内容分析，管理员 / 编辑
GET  /api/contents/audit/pending             待审核内容
POST /api/contents/{id}/audit                内容审核

GET  /api/news/sources                       新闻源列表
POST /api/news/import                        新闻采集，管理员 / 编辑

POST /api/behaviors                          写入用户行为
GET  /api/behaviors                          行为日志，管理员 / 编辑 / 审核员

GET  /api/recommendations/user/{user_id}     用户推荐
GET  /api/recommendations/mixed/{user_id}    混合推荐
GET  /api/recommendations/analytics/summary  推荐效果分析

POST /api/uploads                            文件上传，管理员 / 编辑
```

## 11. 常见问题

### 11.1 访问不了前端

先确认前端服务是否启动：

```text
http://localhost:5173
```

如果端口被占用，关闭旧的 Vite 进程后重新运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_frontend.ps1
```

### 11.2 管理员后台看不到

请确认使用管理员账号登录：

```text
tech_user / demo
```

如果之前登录过普通用户，先退出登录，再重新登录管理员账号。

### 11.3 后端访问不了

先确认后端服务是否启动：

```text
http://localhost:8000/docs
```

重新启动后端：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_backend.ps1
```

### 11.4 数据库在哪里

SQLite 数据库文件：

```text
backend/data/smart_media.db
```

### 11.5 如何重新初始化演示数据

**完全重置**（清空数据库 + 重新播种）：
```powershell
cd E:\code\2026实训\智能传媒内容分析与推荐系统\backend
.\.venv\Scripts\python scripts\init_db.py
```

**安全模式**（仅在数据库为空时播种，不覆盖已有数据）：
```powershell
.\.venv\Scripts\python scripts\init_db.py --safe
```

注意：不带 `--safe` 的默认模式会清空并重建演示数据。

## 12. 开发说明

- 后端入口：`backend/app/main.py`
- 后端路由：`backend/app/api/`
- 后端模型：`backend/app/models/`
- 后端服务：`backend/app/services/`
- 推荐算法：`backend/app/algorithms/recommender.py`
- 内容分析：`backend/app/algorithms/content_analyzer.py`
- 前端入口：`frontend/src/main.js`
- 前端页面：`frontend/src/views/`
- 前端接口封装：`frontend/src/api/`
- 前端路由：`frontend/src/router/index.js`
