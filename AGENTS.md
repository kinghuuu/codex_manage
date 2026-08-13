# AGENTS.md

## 项目简介
`codex_manage` 是基于 FastAPI 的异步后端项目。代码注释统一使用中文，新增代码时请保持该规范。

## 技术栈
- 框架：FastAPI + uvicorn（端口 8011）
- ORM/数据库：SQLAlchemy 2.x（异步）+ asyncpg，PostgreSQL 15
- 缓存：Redis（异步客户端 `redis.asyncio`）
- 认证：PyJWT / python-jose，passlib（bcrypt）

## 目录结构
- `app/main.py` — FastAPI 入口；注册路由、中间件，启动时检查 Redis/Postgres
- `app/modules/` — 业务模块，每个模块包含 `models/`、`schemas/`、`services/`、`views/`
  - `config/` — 用户与认证（登录/注册/Token）
  - `news/` — 新闻、历史记录、收藏
  - `tools/` — 天气等工具
- `app/utils/` — `database.py`、`cache_conf.py`、`jwt.py`、`security.py`、`middleware.py`、`response.py`、`exception.py`、`logger.py`
- `app/cache/` — Redis 缓存封装（缓存键如 `news:categories`、`news:list:*`、`news:detail:*`）
- `test/` — pytest 风格脚本

## 运行方式
- Docker：`docker compose up --build`（后端 8011 端口，Postgres 宿主机端口 15400，Redis 6379）
- 本地开发：激活 `venv` 后执行 `uvicorn app.main:app --reload --port 8011`
- 配置来自 `.env`（`DB_*`、`REDIS_*`、`SMTP_*`）；`docker-compose.yml` 会把 DB/REDIS 主机覆盖为容器名

## 开发规范

### 1. 敏感配置禁止硬编码
- 数据库密码、API Key、JWT 密钥等敏感配置必须通过 `os.getenv()` 读取，值统一放在 `.env`（已被 `.gitignore` 忽略，严禁提交）。
- 参考 `app/utils/database.py`：先调用 `load_dotenv()`，再逐个 `os.getenv("DB_HOST")` 读取。
- 严禁在代码中写死密钥。反例：`app/utils/jwt.py` 中硬编码的 `SECRET_KEY`，应改为 `SECRET_KEY = os.getenv("JWT_SECRET_KEY")`，真实密钥只存在于 `.env`。
- 新增密钥/凭据配置项时，在 `.env.example`（如存在）补充键名占位，不填真实值。

### 2. 公共逻辑统一封装在 app/utils/
- 密码加密/校验 → `app/utils/security.py`（`PasswordUtils.hash_password` / `check_password`）
- JWT 生成/校验、OAuth2 依赖 → `app/utils/jwt.py`（`create_user_token` / `get_user_token`）
- 统一响应、异常处理、日志、缓存等同样封装在 `app/utils/` 或 `app/cache/`。
- 分层职责：`views/` 只负责参数解析并调用 `services/`；`services/` 负责业务编排；加密、鉴权等公共能力一律复用 `app/utils/`，禁止在路由或服务里重复实现。

### 3. FastAPI 路由依赖注入写法
- 数据库会话统一用 `db: AsyncSession = Depends(get_db)`（`get_db` 来自 `app/utils/database.py`），禁止自行创建 session。
- Token 鉴权推荐 `Annotated` 写法：`token: Annotated[str, Depends(oauth2_scheme)]`，或直接依赖 `get_current_active_user`。
- 整组路由需要鉴权时，在 `APIRouter(..., dependencies=[Depends(...)])` 上统一声明（参考 `app/modules/tools/views/weather.py`）；仅个别接口需要时，在函数参数上声明。
- 路由函数保持精简：入参校验交给 Pydantic schema 和 `Query`，业务逻辑放在 services。

### 4. Git 提交与分支规范
- 提交信息使用 Conventional Commits：`<type>(<scope>): <subject>`
  - `type` 取值：`feat` / `fix` / `docs` / `refactor` / `perf` / `test` / `chore` / `style` / `build` / `ci`
  - `scope` 可选，建议用模块名，如 `auth`、`news`、`utils`
  - `subject` 用中文或英文均可；英文用祈使句、首字母小写
  - 示例：`feat(auth): 新增用户注册接口`、`fix(news): 修复列表缓存未失效`、`refactor(utils): 抽取密码加密到 security.py`
- 分支命名：`<type>/<kebab-case 描述>`，如 `feat/auth-login`、`fix/news-cache-expire`、`refactor/utils-password`、`docs/readme-update`
- 功能开发基于新分支，不直接向 `main`/`master` 推送未经 review 的改动。

## 其他约定
- 改动保持最小化，风格与现有代码保持一致
- 不得提交 `.env`、`venv/`、`postgres-data/`、`redis-data/`
- 代码注释一律使用中文
