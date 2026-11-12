# Lesson16 作业记录：测试、代码审查与代码提交

## 仓库

- 原仓库：<https://github.com/leiaqi1206/miaojia-archive-lesson15>
- 本次代码提交：`e7459b4b78043e3b6a6827b2f9222fb1a9ffdcb5`
- 本次提交链接：<https://github.com/leiaqi1206/miaojia-archive-lesson15/commit/e7459b4b78043e3b6a6827b2f9222fb1a9ffdcb5>（推送成功后可在 GitHub 查看）

## 第一部分：自测与检查

### 实际使用的检查提示词

> 请检查当前项目，重点验证新建猫咪档案和姓名校验：正常操作时，提交前后带空格的姓名应得到 HTTP 201、保存去掉首尾空格后的名字，并且重新建立客户端后仍可读取；遇到只包含空格的姓名时应拒绝保存，返回 HTTP 422，猫咪列表保持为空。请运行已有后端测试、前端类型检查和构建，使用独立测试数据库，保留项目原有资料，报告结果和未验证项。

### 填空答案

- 我实际检查了新建猫咪档案，重点关注空白姓名拒绝保存及资料持久化，因为这关系到档案数据是否有效、刷新后是否仍能读取。
- 我原本预期带首尾空格的正常姓名会被整理后保存，纯空格姓名会被拒绝且不会进入数据库。实际结果是：浏览器中纯空格姓名显示“请填写猫咪名字。”且没有提交；有效姓名成功显示在详情页，刷新后仍可读取。补充后的 API 测试确认纯空格姓名返回 HTTP 422，且列表为空。证据包括本会话展示的详情页截图，以及 `backend/tests/test_api.py` 中 `test_create_list_and_get_cat`、`test_records_survive_a_new_client`、`test_blank_name_is_rejected` 的执行输出：7 项通过。
- 本轮新增或调整了 `backend/tests/test_api.py` 中的断言，作用是确认被拒绝的姓名没有写入数据库。后端 7 项测试、前端 `vue-tsc` 类型检查和 Vite 构建均通过；浏览器手动验证使用独立临时数据库。未人工逐项操作编辑、删除和照片上传等其他页面流程。

### 检查结果

- 后端命令：`cd backend && ./.venv/bin/python -m unittest discover -s tests -v` — 7 项通过。
- 前端命令：`cd frontend && npm run build` — `vue-tsc -b` 与 Vite production build 通过。
- `git diff --check` 通过。
- 测试使用临时 SQLite 数据库；项目原数据库仍保留“小橘”和“奶盖”两条记录。

## 第二部分：代码审查与修复

### 实际使用的审查提示词

> 请审查当前项目的前后端代码，结合测试结果列出有依据的问题、触发条件、影响和依据，区分确认的问题与未验证风险。重点检查空白姓名被拒绝后是否确实没有写入记录。

### 选择的问题与处理

- 我选择处理空白姓名测试覆盖不足的问题。在提交只包含空格的姓名时，API 应拒绝请求；原测试只检查 HTTP 422，没有确认数据库仍为空。若只检查状态码，就无法证明无效资料没有被保存，因此补上数据库列表为空的断言。
- 一处关键改动位于 `backend/tests/test_api.py`：在原有 HTTP 422 断言后，新增 `GET /api/cats` 结果为空的断言。这样可以同时验证拒绝响应和没有产生副作用。
- 修改前的结果是测试只验证 HTTP 422；修改后同一测试还验证记录未保存。通过完整后端测试套件确认效果，并重新检查创建、读取、更新、删除和持久化相关测试，结果均通过。

### 实际使用的处理提示词

> 我选择补足空白姓名测试，因为原测试只确认接口返回 HTTP 422，没有确认数据库未新增记录。我希望空白姓名请求被拒绝且记录列表保持为空。请核实判断，补充测试并回归验证，说明文件改动及作用。

## 第三部分：整理并提交代码

### 改动概述

- 前端保留原有网站布局并连接 FastAPI，支持猫咪档案的列表、详情、新建、编辑、删除和错误提示。
- 后端提供 FastAPI 接口并使用 SQLite 保存档案，兼容并保留已有资料。
- README 补充启动命令、地址和接口说明。
- 后端测试补足空白姓名请求不会写入数据库的检查。

### 实际使用的提交提示词

> 本次主要改动是保留现有喵家档案网站外观，将猫咪档案前端接入 FastAPI 与 SQLite，补充 API 测试并更新启动文档。提交说明采用 `feat: connect cat archive UI to FastAPI and SQLite`。请核对差异、确认测试和构建结果有效，保留其他改动，将本次修改提交并推送到原仓库 <https://github.com/leiaqi1206/miaojia-archive-lesson15>，给出提交号和提交链接。

### 填空答案

- 本次提交包含前后端档案功能、SQLite 持久化、测试和启动说明，涉及 `frontend/`、`backend/` 和 `README.md`；README 的命令改为从项目根目录使用相对路径，更新的文档是 `README.md` 与本作业记录 `LESSON16_REPORT.md`。
- 我采用的提交说明是 `feat: connect cat archive UI to FastAPI and SQLite`；提交号是 `e7459b4b78043e3b6a6827b2f9222fb1a9ffdcb5`，GitHub 提交链接是 <https://github.com/leiaqi1206/miaojia-archive-lesson15/commit/e7459b4b78043e3b6a6827b2f9222fb1a9ffdcb5>。
- 本地已核对提交差异和说明。GitHub 页面尚未核对；推送未完成，因为此电脑没有可用的 GitHub 命令行凭据，需先连接 GitHub 后再推送并核对。

## 演示证据

后端测试执行输出显示 7 项测试通过；前端执行 `npm run build` 后显示 `vue-tsc -b` 和 Vite production build 成功。浏览器验证截图显示“Lesson16检查猫”保存后的详情页，重新加载后仍显示该记录。所有测试使用临时数据库；项目数据库中的“小橘”和“奶盖”记录保持不变。GitHub 推送与页面核对尚待完成。
