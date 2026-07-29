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
│       │       └── auth.py        # 登录、注册、鉴权相关
│       ├── news/                  # 新闻业务模块
│       │   ├── __init__.py
│       │   ├── models/            # 数据模型
│       │   ├── schemas/           # 数据结构
│       │   ├── services/          # 业务服务
│       │   └── views/             # 路由
│       │       ├── news.py        # 新闻内容
│       │       ├── history.py     # 历史记录
│       │       └── favorite.py    # 收藏
│       └── ...                    # 其他一级业务模块
├── README.md
└── venv/                          # 本地虚拟环境
```


## 技术栈
- 后端框架: FastAPI
- 数据库: Postgres
- 数据库驱动: asyncpg
- ORM: SQLAlchemy (异步)
- 缓存系统: Redis
- 异步支持: Python asyncio


## 缓存策略
| 缓存类型 | 缓存键格式 | TTL | 
|----------|-----------|-------|
| 分类缓存 | `news:categories` | 7200s |
| 列表缓存 | `news:list:{category_id}:{page}:{page_size}` | 1800s |
| 详情缓存 | `news:detail:{news_id}` | 600s  | 新闻详情 |
| 相关新闻 | `news:related:{news_id}:{category_id}` | 1800  |


## 配置 Redis 客户端
    安装 Redis 客户端： pip install redis
    
    配置 Redis 客户端： 
        import redis.asyncio as redis
        redis.Redis(...)
        
        host: Redis 服务器地址
        port: 端口号 6379
        db: 数据库编号 (0~15)，默认为0
        decode_responses: 是否将返回的数据从字节流解码为字符串
    
    应用详见：config/cache_conf.py

    封装缓存操作：
        缓存操作就是围绕 Redis 做“存、取、删、判断、过期”等操作，让数据访问更快、数据库压力更小。
        Redis 存储数据：key - value
        方法：
            setex：设置缓存并指定过期时间（秒）
            get：获取缓存值。若缓存不存在，返回 None
            delete：删除指定的缓存键
            exists：检查缓存键是否存在，返回布尔值


## 全局异常处理器
全局异常处理器（Global Exception Handler）是注册在 FastAPI 应用级别的异常处理函数，
用于捕获业务层、数据库层以及系统层抛出的异常，并以统一的响应格式返回给前端。
步骤：
    （1）定义异常处理器(函数)
    （2）全局注册异常处理器(函数)
     详见： utils\exception.py、main.py





## Docker部署项目
只修改了代码，执行： 
```shell
docker compose up -d --build codex-manage-service
```

增加了其他容器，执行： 
```shell
docker compose up -d
```

修改了Dockerfile,需要全部重新构建，执行： 
```shell
docker compose up -d --build
```

相关概念：
1.Dockerfile：负责“造”（构建镜像）
1.docker-compose.yml：负责“用”（运行容器、映射端口、设置环境变量等）
1.执行docker compose up -d --build会创建镜像和容器，Docker Compose 项目分组名称自动命名为该项目名称。

```text
部署步骤：
1.确保项目结构：
    codex-manage/
    ├── Dockerfile          # 构建指令
    ├── docker-compose.yml  # 容器编排配置
    ├── requirements.txt    # Python 依赖
    └── app/                # 你的业务代码
        └── main.py         # 入口文件

2.将项目上传到服务器
3.进入项目目录(到codex-manage这一级)
4.一键构建并启动(首次启动时需要构建所有镜像：docker compose up -d --build)
5.验证部署是否成功
    查看运行状态：docker compose ps (STATUS 列显示为 Up)
    查看启动日志：docker compose logs -f (看到类似 Uvicorn running on http://0.0.0.0:8011 的日志，说明应用已经成功启动)

日常运维常用命令速查：
    停止并删除容器（不会删除镜像）：docker compose down
    仅重启容器（不重新构建镜像）：docker compose restart
```


## 安装依赖
```shell
pip install -r requirements.txt
```

## 导出当前 Python 环境中所有已安装包及其精确版本号
```shell
pip freeze > requirements.txt
```



