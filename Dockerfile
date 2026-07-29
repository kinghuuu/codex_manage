# 1. 使用基础的Python镜像
# 注：slim 版本去除了很多不必要的编译工具和文档，体积通常能减少一半以上，非常适合生产环境。
FROM python:3.11.9-slim

# 2. 设置环境变量
# PYTHONDONTWRITEBYTECODE=1: 防止 Python 在容器中生成 .pyc 字节码文件，节省空间
# PYTHONUNBUFFERED=1: 确保 Python 输出直接打印到终端，而不是被缓存（这对查看 docker logs 至关重要）
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. 设置工作目录
# 设置容器内的工作目录为 /my-codex-manage，后续指令（如 COPY、RUN）的操作路径默认基于此目录
# 有了 WORKDIR /my-codex-manage 后，Docker 知道你要在这个目录下干活，就可以直接写相对路径：
# 例如：COPY ./requirements.txt ./requirements.txt
WORKDIR /my-codex-manage

# 4. 设置时区为上海 (Asia/Shanghai)
# 这一步很重要，否则容器内的日志时间会比北京时间慢 8 小时
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

# 5. 复制依赖文件
# 将 requirements.txt 单独复制并安装，利用 Docker 的层缓存机制
COPY ./requirements.txt /my-codex-manage/requirements.txt

# 6. 安装依赖
# --no-cache-dir：不缓存安装包（减少镜像体积）
# --upgrade：升级已安装的包到最新版本
# -r /my-codex-manage/requirements.txt：从指定的 requirements.txt 文件中读取依赖列表并安装
RUN pip install --no-cache-dir --upgrade -r /my-codex-manage/requirements.txt

# 7.复制应用代码
# 将宿主机当前目录下的 app 文件夹，递归复制到容器的 /my-codex-manage/app 路径（即把本地代码拷贝到容器中）
COPY ./app /my-codex-manage/app

# 8.启动命令
# 容器启动时执行的命令（用 JSON 数组格式，避免 shell 解析问题）
# uvicorn：ASGI 服务器
# app.main:app：指定 ASGI 应用的入口（app/main.py 文件中的 app 实例）；
# --host 0.0.0.0：监听所有网络接口（允许外部访问）；
# --port 8011：服务监听端口为 8011。
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8011"]

