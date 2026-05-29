# 智能传媒内容分析与推荐系统 AI Coding 开发提示词

下面这段提示词可直接复制给 AI Coding 工具，用于生成和迭代开发本项目代码。

---

## 一、角色设定

你是一名资深全栈工程师、推荐系统工程师和架构师。请使用 **Python + Vue** 为我开发一个“智能传媒内容分析与推荐系统”。

你需要按照工程化标准完成项目，不要只写演示代码。代码要结构清晰、可运行、可扩展、便于后续二次开发。

---

## 二、项目名称

智能传媒内容分析与推荐系统

---

## 三、项目目标

构建一个面向新闻、图文、视频、融媒体内容平台的智能内容分析与推荐系统，实现以下能力：

1. 内容管理：支持内容新增、编辑、删除、查询、分类、标签管理。
2. 内容智能分析：对标题和正文进行关键词提取、自动摘要、分类、情感分析、热度评分。
3. 用户画像：根据用户浏览、点赞、收藏、评论等行为构建兴趣画像。
4. 个性化推荐：基于内容标签、用户兴趣、热门度和协同过滤思想进行内容推荐。
5. 数据统计：展示内容数量、用户行为、推荐点击率、热门内容等统计数据。
6. 后台管理：提供可视化管理后台，方便运营人员维护内容和查看推荐效果。

---

## 四、技术栈要求

### 后端

请使用 Python 实现，推荐技术栈如下：

- Python 3.10+
- FastAPI：后端 Web 框架
- SQLAlchemy：ORM
- Pydantic：数据校验
- SQLite：开发阶段数据库，代码结构要方便后续替换为 MySQL/PostgreSQL
- Jieba：中文分词和关键词提取
- scikit-learn：TF-IDF、相似度计算、基础推荐算法
- Uvicorn：服务启动
- python-jose / passlib：如实现登录认证，可用于 JWT 和密码加密

### 前端

请使用 Vue 实现，推荐技术栈如下：

- Vue 3
- Vite
- Vue Router
- Pinia
- Axios
- Element Plus
- ECharts

### 开发规范

- 前后端分离。
- 后端提供 RESTful API。
- 前端通过 Axios 调用后端接口。
- 代码要包含必要注释。
- 目录结构要清晰。
- API 返回格式统一。
- 错误处理要规范。
- 页面要具备基本美观度和可用性。

---

## 五、整体架构

系统采用前后端分离架构：

```text
智能传媒内容分析与推荐系统
├── backend/                # Python FastAPI 后端
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 配置、通用工具
│   │   ├── db/             # 数据库连接
│   │   ├── models/         # SQLAlchemy 模型
│   │   ├── schemas/        # Pydantic 数据模型
│   │   ├── services/       # 业务逻辑
│   │   ├── algorithms/     # 内容分析和推荐算法
│   │   └── main.py         # FastAPI 入口
│   ├── requirements.txt
│   └── README.md
│
├── frontend/               # Vue 前端
│   ├── src/
│   │   ├── api/            # Axios 接口封装
│   │   ├── assets/         # 静态资源
│   │   ├── components/     # 公共组件
│   │   ├── router/         # 路由
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── views/          # 页面
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── README.md
│
├── docs/                   # 项目文档
├── scripts/                # 初始化脚本、测试数据
└── README.md
```

---

## 六、核心业务模块

### 1. 内容管理模块

内容字段建议包括：

- id
- title：标题
- summary：摘要
- content：正文
- author：作者
- category：分类
- tags：标签，多个标签用数组或逗号分隔
- cover_url：封面图地址
- content_type：内容类型，例如 article、video、image
- publish_time：发布时间
- view_count：浏览量
- like_count：点赞量
- favorite_count：收藏量
- comment_count：评论量
- heat_score：热度分
- quality_score：质量分
- sentiment：情感倾向，positive、neutral、negative
- created_at
- updated_at

需要实现接口：

- `GET /api/contents`：分页查询内容
- `GET /api/contents/{id}`：查询内容详情
- `POST /api/contents`：新增内容
- `PUT /api/contents/{id}`：编辑内容
- `DELETE /api/contents/{id}`：删除内容
- `POST /api/contents/{id}/analyze`：对指定内容执行智能分析
- `GET /api/contents/hot`：获取热门内容

---

### 2. 内容智能分析模块

使用 Python 实现基础 NLP 分析能力。

#### 需要实现的能力

1. 中文分词  
   使用 jieba 对标题和正文进行分词。

2. 关键词提取  
   可使用 jieba.analyse.extract_tags 或 TF-IDF。

3. 自动摘要  
   初版可采用简单规则：
   - 取正文前 100-200 字；
   - 或根据关键词匹配句子权重，选择权重最高的 2-3 句。

4. 自动分类  
   可根据关键词规则实现初版分类，例如：
   - 科技：人工智能、算法、机器人、芯片、互联网、软件
   - 财经：股票、市场、企业、投资、经济、金融
   - 体育：比赛、球队、冠军、赛事、运动员
   - 娱乐：电影、音乐、明星、综艺
   - 社会：城市、民生、教育、医疗、交通

5. 情感分析  
   初版可使用正负面词典规则实现：
   - positive
   - neutral
   - negative

6. 内容质量评分  
   根据以下因素计算 0-100 分：
   - 标题长度是否合理
   - 正文长度是否充足
   - 是否有摘要
   - 是否有标签
   - 是否有封面图
   - 内容互动数据

7. 内容热度评分  
   可按以下公式：

   ```text
   heat_score = view_count * 0.4 + like_count * 2 + favorite_count * 3 + comment_count * 2.5
   ```

#### 后端建议文件

```text
backend/app/algorithms/content_analyzer.py
```

建议提供函数：

```python
def extract_keywords(title: str, content: str) -> list[str]:
    pass

def generate_summary(content: str, max_length: int = 160) -> str:
    pass

def classify_content(title: str, content: str, keywords: list[str]) -> str:
    pass

def analyze_sentiment(content: str) -> str:
    pass

def calculate_quality_score(content_obj) -> float:
    pass

def calculate_heat_score(view_count: int, like_count: int, favorite_count: int, comment_count: int) -> float:
    pass
```

---

### 3. 用户管理与用户画像模块

用户字段建议包括：

- id
- username
- nickname
- password_hash
- age
- gender
- city
- interests：用户兴趣标签
- created_at
- updated_at

用户行为字段建议包括：

- id
- user_id
- content_id
- action_type：view、like、favorite、comment、share、dislike
- duration：停留时长，单位秒
- created_at

需要实现接口：

- `GET /api/users`：用户列表
- `GET /api/users/{id}`：用户详情
- `POST /api/users`：新增用户
- `PUT /api/users/{id}`：编辑用户
- `DELETE /api/users/{id}`：删除用户
- `GET /api/users/{id}/profile`：获取用户画像
- `POST /api/behaviors`：记录用户行为
- `GET /api/behaviors`：查询行为日志

画像构建逻辑：

- 用户浏览某内容，给该内容标签增加较低权重。
- 用户点赞某内容，给该内容标签增加中等权重。
- 用户收藏某内容，给该内容标签增加较高权重。
- 用户评论或分享某内容，给该内容标签增加较高权重。
- 用户点“不感兴趣”，降低相关标签权重。

示例权重：

```text
view: 1
like: 3
favorite: 5
comment: 4
share: 4
dislike: -5
```

---

### 4. 推荐系统模块

推荐系统初版不要求复杂深度学习，但要有清晰的可扩展结构。

推荐策略包括：

1. 热门推荐  
   按 heat_score 排序推荐。

2. 标签匹配推荐  
   根据用户兴趣标签和内容标签进行匹配。

3. 内容相似推荐  
   根据当前内容的关键词、分类、标签，推荐相似内容。

4. 冷启动推荐  
   对新用户推荐热门内容、最新内容和人工精选内容。

5. 多样性调整  
   推荐列表不要全部来自同一个分类。

推荐接口：

- `GET /api/recommendations/hot`：热门推荐
- `GET /api/recommendations/user/{user_id}`：用户个性化推荐
- `GET /api/recommendations/content/{content_id}`：相似内容推荐
- `GET /api/recommendations/mixed`：综合推荐

推荐排序可按以下综合分：

```text
score = tag_match_score * 0.45
      + heat_score * 0.25
      + quality_score * 0.20
      + freshness_score * 0.10
```

注意：

- 对已经被用户浏览过的内容，可降低权重或过滤。
- 对用户点过“不感兴趣”的标签，要降低推荐分。
- 推荐结果要返回推荐原因，例如：
  - “因为你喜欢人工智能”
  - “近期热度较高”
  - “与你浏览过的内容相似”

后端建议文件：

```text
backend/app/algorithms/recommender.py
```

建议提供函数：

```python
def recommend_for_user(user_id: int, limit: int = 10) -> list[dict]:
    pass

def recommend_hot(limit: int = 10) -> list[dict]:
    pass

def recommend_similar_content(content_id: int, limit: int = 10) -> list[dict]:
    pass
```

---

## 七、前端页面要求

前端使用 Vue 3 + Element Plus 实现后台管理系统风格页面。

### 页面结构

建议包含以下页面：

1. 登录页，可先做简单模拟登录。
2. 首页仪表盘。
3. 内容管理页。
4. 内容新增/编辑页。
5. 内容详情页。
6. 内容智能分析页。
7. 用户管理页。
8. 用户画像页。
9. 行为日志页。
10. 推荐结果页。
11. 数据统计页。
12. 系统设置页。

### 首页仪表盘

展示：

- 内容总数
- 用户总数
- 今日浏览量
- 今日推荐点击量
- 热门分类分布
- 热门内容 Top 10
- 用户行为趋势图

使用 ECharts 绘制：

- 折线图：浏览量趋势
- 柱状图：分类内容数量
- 饼图：用户兴趣分布

### 内容管理页

功能：

- 表格展示内容列表
- 按标题搜索
- 按分类筛选
- 按内容类型筛选
- 新增内容
- 编辑内容
- 删除内容
- 一键智能分析
- 查看详情

表格字段：

- 标题
- 作者
- 分类
- 标签
- 浏览量
- 点赞量
- 热度分
- 情感倾向
- 发布时间
- 操作

### 内容详情页

展示：

- 标题
- 作者
- 分类
- 标签
- 摘要
- 正文
- 封面图
- 浏览量、点赞量、收藏量、评论量
- 热度分
- 质量分
- 情感倾向

### 用户画像页

展示：

- 用户基础信息
- 用户兴趣标签
- 兴趣权重排行
- 行为统计
- 最近浏览内容
- 推荐内容列表

### 推荐结果页

功能：

- 选择用户
- 查看该用户的推荐内容
- 展示推荐分数
- 展示推荐原因
- 支持刷新推荐

---

## 八、API 返回格式规范

所有接口建议统一返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

分页接口返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 10
  }
}
```

错误返回：

```json
{
  "code": 400,
  "message": "参数错误",
  "data": null
}
```

---

## 九、数据库表设计

至少需要设计以下表：

### contents

存储媒体内容。

字段：

- id
- title
- summary
- content
- author
- category
- tags
- cover_url
- content_type
- publish_time
- view_count
- like_count
- favorite_count
- comment_count
- heat_score
- quality_score
- sentiment
- created_at
- updated_at

### users

存储用户信息。

字段：

- id
- username
- nickname
- password_hash
- age
- gender
- city
- interests
- created_at
- updated_at

### user_behaviors

存储用户行为。

字段：

- id
- user_id
- content_id
- action_type
- duration
- created_at

### categories

存储内容分类。

字段：

- id
- name
- description
- created_at

### tags

存储标签。

字段：

- id
- name
- count
- created_at

---

## 十、开发步骤要求

请按以下顺序开发，不要一次性混乱生成代码：

### 第一步：初始化项目结构

创建：

```text
backend/
frontend/
docs/
scripts/
README.md
```

### 第二步：完成后端基础框架

包括：

- FastAPI 应用入口
- 数据库连接
- 统一响应结构
- CORS 配置
- 配置文件
- 基础路由

### 第三步：完成数据库模型和初始化数据

包括：

- 内容模型
- 用户模型
- 用户行为模型
- 分类模型
- 标签模型
- 初始化脚本
- 示例内容数据
- 示例用户数据

### 第四步：完成内容管理 API

包括：

- 增删改查
- 分页查询
- 分类筛选
- 关键词搜索
- 热门内容
- 内容分析接口

### 第五步：完成内容分析算法

包括：

- 关键词提取
- 摘要生成
- 自动分类
- 情感分析
- 质量评分
- 热度评分

### 第六步：完成用户和行为 API

包括：

- 用户管理
- 行为记录
- 用户画像计算

### 第七步：完成推荐算法和接口

包括：

- 热门推荐
- 个性化推荐
- 相似内容推荐
- 综合推荐
- 推荐原因返回

### 第八步：完成前端基础框架

包括：

- Vue 3 + Vite
- Element Plus
- Vue Router
- Pinia
- Axios 封装
- Layout 布局
- 左侧菜单
- 顶部导航

### 第九步：完成前端业务页面

包括：

- 首页仪表盘
- 内容管理
- 内容编辑
- 内容详情
- 用户管理
- 用户画像
- 推荐结果
- 数据统计

### 第十步：联调和优化

包括：

- 前后端接口联调
- 错误提示
- 加载状态
- 空状态
- 表单校验
- 页面样式优化
- README 运行说明

---

## 十一、界面风格要求

前端界面采用现代后台管理系统风格：

- 简洁
- 清晰
- 科技感
- 使用蓝色、白色、浅灰为主色
- 卡片式布局
- 表格操作清晰
- 图表直观

页面布局建议：

```text
顶部导航栏
左侧菜单栏
右侧内容区
```

左侧菜单：

- 首页
- 内容管理
- 用户管理
- 用户画像
- 推荐管理
- 数据统计
- 系统设置

---

## 十二、推荐重点实现逻辑

个性化推荐逻辑可以这样实现：

1. 查询用户历史行为。
2. 根据行为内容的标签计算用户兴趣权重。
3. 查询候选内容。
4. 排除用户已经浏览或明确不感兴趣的内容。
5. 计算内容标签与用户兴趣的匹配分。
6. 结合内容热度、质量分和发布时间计算综合分。
7. 按综合分排序。
8. 做分类多样性调整。
9. 返回推荐内容和推荐原因。

伪代码：

```python
def recommend_for_user(user_id, limit=10):
    user_profile = build_user_profile(user_id)
    candidates = get_candidate_contents()
    scored_items = []

    for item in candidates:
        tag_score = calculate_tag_match(user_profile, item.tags)
        heat_score = normalize(item.heat_score)
        quality_score = normalize(item.quality_score)
        freshness_score = calculate_freshness(item.publish_time)

        score = (
            tag_score * 0.45
            + heat_score * 0.25
            + quality_score * 0.20
            + freshness_score * 0.10
        )

        reason = generate_reason(user_profile, item)
        scored_items.append((item, score, reason))

    return sort_and_diversify(scored_items, limit)
```

---

## 十三、测试数据要求

请提供初始化测试数据，至少包括：

- 30 条内容
- 5 个用户
- 100 条用户行为
- 8 个分类
- 30 个标签

内容类型包括：

- 新闻文章
- 科技资讯
- 财经资讯
- 体育资讯
- 娱乐资讯
- 社会新闻
- 视频内容

用户兴趣类型要有差异，例如：

- 用户 A 偏科技
- 用户 B 偏财经
- 用户 C 偏体育
- 用户 D 偏娱乐
- 用户 E 偏社会民生

---

## 十四、运行方式要求

请最终提供完整 README，说明如何启动项目。

### 后端启动

示例：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Windows PowerShell 环境请补充：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动

示例：

```bash
cd frontend
npm install
npm run dev
```

前端默认地址：

```text
http://localhost:5173
```

后端默认地址：

```text
http://localhost:8000
```

API 文档地址：

```text
http://localhost:8000/docs
```

---

## 十五、验收标准

项目完成后应满足：

1. 后端服务可以正常启动。
2. 前端服务可以正常启动。
3. 前端页面可以访问后端 API。
4. 内容可以新增、编辑、删除、查询。
5. 内容可以执行智能分析。
6. 用户行为可以记录。
7. 用户画像可以生成。
8. 可以根据用户生成个性化推荐结果。
9. 首页仪表盘有统计数据和图表。
10. 项目 README 清楚说明启动和使用方式。

---

## 十六、代码质量要求

1. 不要把所有代码写在一个文件里。
2. 后端业务逻辑要放在 service 层。
3. 推荐算法和内容分析算法要单独放在 algorithms 目录。
4. 前端 API 请求要统一封装。
5. 前端页面组件要适当拆分。
6. 变量命名要清晰。
7. 异常处理要完善。
8. 表单要有校验。
9. 删除操作要有确认弹窗。
10. 重要逻辑要有注释。

---

## 十七、优先级说明

如果开发时间有限，请按以下优先级完成：

### P0 必须完成

- 后端 FastAPI 基础框架
- 数据库模型
- 内容管理 API
- 内容分析基础能力
- 推荐 API
- Vue 前端基础布局
- 内容管理页
- 推荐结果页

### P1 应该完成

- 用户画像
- 行为日志
- 首页仪表盘
- ECharts 图表
- 数据初始化脚本

### P2 可后续增强

- JWT 登录认证
- 视频智能分析
- 深度学习推荐模型
- Elasticsearch 搜索
- Redis 缓存
- Kafka/Flink 实时行为处理
- A/B 测试

---

## 十八、请 AI Coding 工具开始执行时的提示

请严格按照上述要求开发项目。  
先生成完整项目结构，再逐步实现后端、算法、前端和文档。  
每完成一个阶段，请确保代码可以运行，不要留下明显语法错误。  
如果某些高级功能暂时无法实现，请先提供可运行的基础版本，并在 README 中说明后续扩展方向。

