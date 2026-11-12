# 喵家档案 · Lesson15 猫咪档案

本作业以现有喵家档案网站为基础，保留原有页面结构、文案、布局、配色、图标和图片，只把猫咪资料的读取和保存接到 FastAPI 与 SQLite。原有前端项目在 `miaojia-archive-styles`；此交付保留其前端展示代码，并加入后端持久化。

为了和你现有运行中的网站避开端口冲突，下面使用前端 `5174`、后端 `8001`。

## 已完成

- 从原有首页进入猫咪档案库，并保留原有视觉设计。
- 新建猫咪档案，填写姓名、照片、品种、生日、性别、性格和备注。
- 查看多只猫的档案列表与单只猫详情；保留原站已有的编辑和删除操作。
- 猫咪档案和照片保存到本地 SQLite，刷新或重新启动服务后仍可读取。
- 保存和读取失败会显示页面提示；保存失败时表单内容保留，用户可重试。
- 兼容现有 `backend/data/cats.sqlite3` 的表结构，并保留其中已有的“小橘”和“奶盖”记录。

## 环境要求

- Node.js 20 或更新版本（包含 npm）
- Python 3.10 或更新版本

## 启动后端

在第一个终端中，从项目根目录运行：

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

首次安装后端依赖时，在项目根目录运行：

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

后端地址：<http://127.0.0.1:8001>

- 健康检查：<http://127.0.0.1:8001/api/health>
- API 文档：<http://127.0.0.1:8001/docs>
- 数据库文件：`backend/data/cats.sqlite3`

## 启动前端

打开第二个终端，从项目根目录运行：

```bash
cd frontend
npm install
VITE_API_BASE_URL=http://127.0.0.1:8001 npm run dev -- --port 5174
```

打开：<http://localhost:5174>

## API 接口

- `GET /api/health`：健康检查。
- `GET /api/message`：首页连接状态。
- `GET /api/cats`：读取猫咪列表。
- `POST /api/cats`：新增猫咪档案。
- `GET /api/cats/{id}`：读取单只猫咪档案。
- `PUT /api/cats/{id}`：更新猫咪档案。
- `DELETE /api/cats/{id}`：删除猫咪档案。

## 验证

前端构建：`cd frontend && npm run build`

后端测试：

```bash
cd backend
source .venv/bin/activate
python -m unittest discover -s tests -v
```

## 当前范围

SQLite 数据只保存在运行项目的本机。暂不包含登录权限、健康记录模块和生产环境部署。
