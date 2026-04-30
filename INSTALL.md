# 快速安装指南

## 一分钟快速启动 (SQLite版本 - 开箱即用)

### 1. 下载代码
```bash
git clone https://github.com/lwh3/ASL2-OneKeyModel-Heat-V1.0.git
cd ASL2-OneKeyModel-Heat-V1.0
```

### 2. 安装依赖
```bash
cd Backend
pip install -r requirements.txt
```

### 3. 启动系统
```bash
python web_app.py
```

### 4. 访问系统
打开浏览器访问: http://localhost:5000

## 完成！

系统已启动，SQLite数据库会自动创建。

---

## 生产环境部署 (PostgreSQL版本)

### 1. 安装PostgreSQL
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql postgresql-server

# macOS
brew install postgresql
```

### 2. 创建数据库
```bash
# 登录PostgreSQL
sudo -u postgres psql

# 创建数据库和用户
CREATE DATABASE heat_model;
CREATE USER heat_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE heat_model TO heat_user;
\q
```

### 3. 执行建表脚本
```bash
psql -U heat_user -d heat_model -f SQL/create_tables.sql
```

### 4. 修改配置文件
编辑 `Backend/config.yaml`:
```yaml
database:
  type: "postgresql"
  host: "localhost"
  port: 5432
  database: "heat_model"
  username: "heat_user"
  password: "your_secure_password"
  create_tables: false  # 已手动建表
```

### 5. 启动系统
```bash
cd Backend
python web_app.py
```

或使用启动脚本:
```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

---

## Docker部署 (可选)

### 创建Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY Backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Backend/ .
COPY SQL/ /app/SQL/

EXPOSE 5000

CMD ["python", "web_app.py"]
```

### 构建和运行
```bash
# 构建镜像
docker build -t heat-model:v1.0 .

# 运行容器
docker run -d -p 5000:5000 \
  -v $(pwd)/Backend/config.yaml:/app/config.yaml \
  -v $(pwd)/logs:/app/logs \
  --name heat-model \
  heat-model:v1.0
```

---

## 使用systemd管理服务 (Linux)

### 创建服务文件
```bash
sudo nano /etc/systemd/system/heat-model.service
```

内容:
```ini
[Unit]
Description=LF Heat Model Service
After=network.target postgresql.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/ASL2-OneKeyModel-Heat-V1.0/Backend
ExecStart=/usr/bin/python3 /path/to/ASL2-OneKeyModel-Heat-V1.0/Backend/web_app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 启动服务
```bash
sudo systemctl daemon-reload
sudo systemctl enable heat-model
sudo systemctl start heat-model
sudo systemctl status heat-model
```

---

## 常见问题

### Q: 端口5000已被占用
**A**: 修改 `config.yaml` 中的端口号:
```yaml
web_ui:
  port: 8080  # 改为其他端口
```

### Q: 依赖安装失败
**A**: 使用国内镜像源:
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: 数据库连接失败
**A**: 检查:
1. 数据库服务是否运行
2. 配置文件中的连接信息是否正确
3. 防火墙是否允许连接
4. 查看日志: `logs/heat_model.log`

---

## 下一步

- 阅读 [README.md](README.md) 了解详细功能
- 查看 [API文档](README.md#api文档) 进行集成
- 参考 [集成指南](README.md#集成指南) 接入ASL2系统

**祝您使用愉快！**
