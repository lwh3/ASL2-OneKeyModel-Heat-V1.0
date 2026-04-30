# 部署指南 - LF精炼炉加热模型监控系统

本文档提供详细的部署指导，支持两种UI选项：Vue3 WebUI和WPF Desktop应用。

## 目录

- [系统架构](#系统架构)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [详细部署步骤](#详细部署步骤)
- [UI选择指南](#ui选择指南)
- [配置说明](#配置说明)
- [生产部署](#生产部署)
- [故障排除](#故障排除)

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户界面层                              │
├──────────────────────┬──────────────────────────────────┤
│   Vue3 WebUI        │      WPF Desktop App             │
│   (跨平台浏览器)      │      (Windows原生应用)            │
└──────────────────────┴──────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              Flask Backend (Python)                      │
│  - RESTful API                                          │
│  - WebSocket实时通信                                     │
│  - Swagger API文档                                       │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              守护进程 (Daemon)                            │
│  - 轮询任务队列                                           │
│  - 算法计算                                               │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              数据库                                       │
│  PostgreSQL / MySQL / Oracle / SQLite                   │
└─────────────────────────────────────────────────────────┘
```

## 环境要求

### 后端服务
- **Python**: 3.8+ (必需)
- **数据库**: PostgreSQL / MySQL / Oracle / SQLite (选择一种)
- **操作系统**: Linux, Windows, macOS

### Vue3 WebUI
- **Node.js**: 16+ (必需)
- **npm/yarn/pnpm**: 最新版本
- **浏览器**: Chrome 87+, Firefox 78+, Safari 14+, Edge 88+

### WPF Desktop App
- **.NET**: 10 (必需)
- **操作系统**: Windows 10 (1809+) 或 Windows 11
- **开发**: Visual Studio 2022 或 Rider (可选)

## 快速开始

### 使用统一部署脚本

#### Linux/macOS

```bash
# 赋予执行权限
chmod +x deploy.sh

# 运行部署脚本
./deploy.sh
```

#### Windows

```cmd
# 直接运行部署脚本
deploy.bat
```

### 手动部署

#### 1. 部署后端

```bash
cd Backend

# 安装依赖
pip install -r requirements.txt

# 配置数据库 (编辑 config.yaml)
vi config.yaml

# 启动服务
python web_app.py
```

后端服务将运行在 `http://localhost:5000`

#### 2. 部署Vue3 WebUI

```bash
cd Frontend-Vue3

# 安装依赖
npm install

# 开发模式
npm run dev  # 访问 http://localhost:3000

# 生产构建
npm run build  # 输出到 dist/ 目录
```

#### 3. 构建WPF Desktop App

```bash
cd Frontend-WPF/HeatModelMonitor

# 还原依赖
dotnet restore

# 开发运行
dotnet run

# 生产构建
dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true
```

## 详细部署步骤

### 步骤1: 准备环境

#### 安装Python 3.8+

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**Windows:**
从 https://www.python.org/downloads/ 下载并安装

**macOS:**
```bash
brew install python3
```

#### 安装Node.js (用于Vue3)

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

**Windows/macOS:**
从 https://nodejs.org/ 下载并安装

#### 安装.NET 10 (用于WPF)

**Windows:**
从 https://dotnet.microsoft.com/download 下载并安装

### 步骤2: 配置数据库

#### 选项A: 使用SQLite (最简单，适合测试)

编辑 `Backend/config.yaml`:
```yaml
database:
  type: "sqlite"
  sqlite_path: "./heat_model.db"
  create_tables: true
```

无需额外配置，系统会自动创建数据库文件。

#### 选项B: 使用PostgreSQL (推荐生产环境)

1. **安装PostgreSQL**
   ```bash
   # Linux
   sudo apt install postgresql postgresql-contrib

   # macOS
   brew install postgresql
   ```

2. **创建数据库**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE heat_model;
   CREATE USER heat_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE heat_model TO heat_user;
   \q
   ```

3. **执行建表SQL**
   ```bash
   psql -U heat_user -d heat_model -f SQL/create_tables.sql
   ```

4. **配置连接**
   编辑 `Backend/config.yaml`:
   ```yaml
   database:
     type: "postgresql"
     host: "localhost"
     port: 5432
     database: "heat_model"
     username: "heat_user"
     password: "your_password"
   ```

#### 选项C: 使用MySQL

1. **安装MySQL**
   ```bash
   sudo apt install mysql-server
   ```

2. **创建数据库**
   ```bash
   mysql -u root -p
   CREATE DATABASE heat_model;
   CREATE USER 'heat_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON heat_model.* TO 'heat_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

3. **执行建表SQL**
   ```bash
   mysql -u heat_user -p heat_model < SQL/create_tables.sql
   ```

4. **配置连接**
   编辑 `Backend/config.yaml`:
   ```yaml
   database:
     type: "mysql"
     host: "localhost"
     port: 3306
     database: "heat_model"
     username: "heat_user"
     password: "your_password"
   ```

### 步骤3: 部署后端服务

```bash
cd Backend

# 安装Python依赖
pip install -r requirements.txt

# 测试运行
python web_app.py
```

验证后端服务:
- API: http://localhost:5000/api/status
- Swagger文档: http://localhost:5000/api/docs

### 步骤4: 选择并部署UI

#### 选项A: Vue3 WebUI (推荐跨平台使用)

**开发环境部署:**
```bash
cd Frontend-Vue3

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问: http://localhost:3000

**生产环境部署:**

1. **构建静态文件**
   ```bash
   npm run build
   ```

2. **部署方式1: 使用Nginx**
   ```bash
   # 复制构建文件到Nginx目录
   sudo cp -r dist/* /var/www/html/lf-heating/

   # 配置Nginx
   sudo vi /etc/nginx/sites-available/lf-heating
   ```

   Nginx配置示例:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       root /var/www/html/lf-heating;
       index index.html;

       location / {
           try_files $uri $uri/ /index.html;
       }

       location /api {
           proxy_pass http://localhost:5000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

3. **部署方式2: 使用Flask集成**
   ```bash
   # 复制构建文件到Flask静态目录
   cp -r dist/* ../Backend/web_ui/static/vue3/
   ```

4. **部署方式3: 使用Docker**
   ```dockerfile
   # Dockerfile
   FROM node:18-alpine as build
   WORKDIR /app
   COPY package*.json ./
   RUN npm install
   COPY . .
   RUN npm run build

   FROM nginx:alpine
   COPY --from=build /app/dist /usr/share/nginx/html
   EXPOSE 80
   CMD ["nginx", "-g", "daemon off;"]
   ```

   构建和运行:
   ```bash
   docker build -t lf-heating-vue3 .
   docker run -d -p 80:80 lf-heating-vue3
   ```

#### 选项B: WPF Desktop App (推荐Windows生产环境)

**开发环境:**
```bash
cd Frontend-WPF/HeatModelMonitor

# 使用Visual Studio打开 HeatModelMonitor.sln
# 或使用命令行运行
dotnet run
```

**生产部署:**

1. **构建发布版本**
   ```bash
   dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true
   ```

   输出位置: `bin/Release/net10.0-windows/win-x64/publish/HeatModelMonitor.exe`

2. **配置API端点**
   编辑 `appsettings.json`:
   ```json
   {
     "ApiSettings": {
       "BaseUrl": "http://your-api-server:5000/api",
       "Timeout": 30
     }
   }
   ```

3. **分发应用**
   - 方式1: 直接分发 `publish` 文件夹
   - 方式2: 创建MSI安装程序 (使用WiX Toolset)
   - 方式3: 创建Setup向导 (使用Inno Setup)

## UI选择指南

### 何时使用Vue3 WebUI?

**优势:**
- ✅ 跨平台访问 (Windows/Linux/macOS/移动设备)
- ✅ 无需安装，浏览器即可访问
- ✅ 易于更新和维护
- ✅ 多用户同时访问
- ✅ 适合远程监控

**适用场景:**
- 需要远程访问监控系统
- 多个用户需要同时查看数据
- 移动设备访问需求
- IT环境允许Web应用

### 何时使用WPF Desktop App?

**优势:**
- ✅ 原生Windows性能
- ✅ 离线缓存功能
- ✅ 更丰富的桌面集成 (系统托盘、文件系统等)
- ✅ 适合高安全要求环境 (无需Web端口)
- ✅ 企业级桌面应用体验

**适用场景:**
- Windows生产环境
- 需要离线工作能力
- 高安全要求 (限制Web访问)
- 需要桌面集成功能
- 企业内部使用

### 混合部署

可以同时部署两种UI，让用户根据需求选择:
- 办公室用户使用Vue3 WebUI远程访问
- 现场操作员使用WPF Desktop App本地操作

## 配置说明

### 后端配置 (Backend/config.yaml)

```yaml
# 数据库配置
database:
  type: "postgresql"  # postgresql, mysql, oracle, sqlite
  host: "localhost"
  port: 5432
  database: "heat_model"
  username: "heat_user"
  password: "your_password"

# Web UI配置
web_ui:
  enabled: true
  host: "0.0.0.0"  # 0.0.0.0 允许外部访问
  port: 5000
  debug: false

# 守护进程配置
daemon:
  polling_interval: 2  # 轮询间隔(秒)
  max_retries: 3
  retry_delay: 5

# 日志配置
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file_path: "logs/heat_model.log"
```

### Vue3前端配置

创建 `.env.production`:
```env
VITE_API_BASE_URL=http://your-server:5000/api
```

### WPF应用配置

编辑 `appsettings.json`:
```json
{
  "ApiSettings": {
    "BaseUrl": "http://your-server:5000/api",
    "Timeout": 30
  },
  "AppSettings": {
    "RefreshInterval": 10,
    "LogLines": 100
  }
}
```

## 生产部署

### 使用Systemd (Linux)

创建服务文件 `/etc/systemd/system/lf-heating.service`:

```ini
[Unit]
Description=LF Heating Model Backend Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/lf-heating/Backend
ExecStart=/usr/bin/python3 /opt/lf-heating/Backend/web_app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable lf-heating
sudo systemctl start lf-heating
sudo systemctl status lf-heating
```

### 使用Docker Compose

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./Backend
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - DB_TYPE=postgresql
      - DB_HOST=db
      - DB_PORT=5432
      - DB_NAME=heat_model
      - DB_USER=heat_user
      - DB_PASS=your_password
    depends_on:
      - db
    restart: always

  vue3:
    build:
      context: ./Frontend-Vue3
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: always

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=heat_model
      - POSTGRES_USER=heat_user
      - POSTGRES_PASSWORD=your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./SQL/create_tables.sql:/docker-entrypoint-initdb.d/create_tables.sql
    restart: always

volumes:
  postgres_data:
```

启动:
```bash
docker-compose up -d
```

## 故障排除

### 后端无法启动

**问题**: 数据库连接失败
```
Error: could not connect to server
```

**解决**:
1. 检查数据库服务是否运行
2. 验证 `config.yaml` 中的数据库配置
3. 检查防火墙设置

**问题**: 端口被占用
```
Error: Address already in use: 5000
```

**解决**:
1. 更改 `config.yaml` 中的端口号
2. 或停止占用端口的程序

### Vue3前端无法连接后端

**问题**: API请求失败

**解决**:
1. 检查后端服务是否运行
2. 验证API地址配置
3. 检查CORS设置
4. 检查网络和防火墙

### WPF应用无法启动

**问题**: 缺少.NET Runtime

**解决**:
- 安装.NET 10 Runtime
- 或使用自包含部署模式

**问题**: 无法连接API

**解决**:
1. 检查 `appsettings.json` 中的API地址
2. 确保后端服务可访问
3. 检查防火墙设置

## 性能优化

### 后端优化
- 使用PostgreSQL代替SQLite (生产环境)
- 启用数据库连接池
- 配置适当的轮询间隔
- 使用Redis缓存 (可选)

### Vue3前端优化
- 启用gzip压缩
- 使用CDN加速静态资源
- 配置浏览器缓存
- 代码分割和懒加载

### WPF应用优化
- 使用虚拟化列表
- 异步加载数据
- 实现数据缓存
- 优化UI渲染

## 监控和日志

### 日志位置
- 后端: `Backend/logs/heat_model.log`
- Vue3: 浏览器控制台
- WPF: Windows事件查看器

### 监控端点
- 健康检查: `GET /api/status`
- API文档: `GET /api/docs`

## 更新和维护

### 后端更新
```bash
cd Backend
git pull
pip install -r requirements.txt --upgrade
sudo systemctl restart lf-heating
```

### Vue3前端更新
```bash
cd Frontend-Vue3
git pull
npm install
npm run build
# 部署新的构建文件
```

### WPF应用更新
```bash
cd Frontend-WPF/HeatModelMonitor
git pull
dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true
# 分发新的可执行文件
```

## 支持和帮助

- **文档**: 查看项目README.md
- **Issues**: https://github.com/lwh3/ASL2-OneKeyModel-Heat-V1.0/issues
- **Wiki**: 查看项目Wiki获取更多信息
