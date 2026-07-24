# codex_manage

## 项目结构

```text
codex_manage/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 入口
│   ├── commons/                   # 公共配置、常量、基础能力
│   ├── utils/                     # 工具方法
│   └── modules/                   # 业务模块
│       ├── config/                # 基础管理类功能
│       │   ├── __init__.py
│       │   ├── models/            # 数据模型
│       │   ├── schemas/           # 数据结构
│       │   ├── services/          # 业务服务
│       │   └── views/             # 路由
│       │       ├── user.py        # 用户相关
│       │       ├── auth.py        # 登录、注册、鉴权相关
│       │       ├── role.py        # 角色管理
│       │       └── department.py  # 部门管理
│       ├── news/                  # 新闻业务模块
│       │   ├── __init__.py
│       │   ├── models/            # 数据模型
│       │   ├── schemas/           # 数据结构
│       │   ├── services/          # 业务服务
│       │   └── views/             # 路由
│       │       ├── article.py     # 文章/新闻内容
│       │       ├── category.py    # 分类管理
│       │       └── comment.py     # 评论相关
│       └── ...                    # 其他一级业务模块
├── README.md
└── venv/                          # 本地虚拟环境
```

## 说明

- `modules` 功能模块，例如 `config`、`news`
- `config` 主要放通用管理能力，例如用户、鉴权、角色、部门等
- `news` 主要放新闻相关业务，并可继续拆分出多个子功能
- 每个业务模块统一采用 `models / schemas / services / views` 四层结构
- `models`：数据库模型
- `schemas`：请求 / 响应数据结构
- `services`：核心业务逻辑
- `views`：接口路由
