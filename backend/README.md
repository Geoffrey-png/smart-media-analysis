# 后端说明

## 技术栈

- Python 3.10+
- FastAPI
- SQLAlchemy
- SQLite
- Jieba

## 启动

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/init_db.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档：

```text
http://localhost:8000/docs
```

演示账号：

```text
tech_user / demo
finance_user / demo
sports_user / demo
ent_user / demo
life_user / demo
```

主要接口：

- `POST /api/auth/login`：登录
- `GET /api/meta/options`：分类、标签、内容类型
- `GET /api/dashboard/summary`：首页统计
- `GET /api/recommendations/user/{user_id}`：个性化推荐
- `POST /api/uploads`：文件上传
- `GET /api/contents/audit/pending`：待审核内容
- `POST /api/contents/{id}/audit`：内容审核
- `GET /api/recommendations/analytics/summary`：推荐效果分析
