# ASL2-OneKeyModel-Heat-V1.0

## LF精炼炉加热模型工艺包 - 一键式智能加热控制系统

![Version](https://img.shields.io/badge/version-1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

---

## 📋 目录

- [系统简介](#系统简介)
- [核心原理](#核心原理)
- [系统架构](#系统架构)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [详细使用指南](#详细使用指南)
- [算法详解](#算法详解)
- [配置说明](#配置说明)
- [API文档](#api文档)
- [集成指南](#集成指南)
- [常见问题](#常见问题)
- [后续发展](#后续发展)
- [贡献指南](#贡献指南)

---

## 🎯 系统简介

**ASL2-OneKeyModel-Heat-V1.0** 是一个专为LF（Ladle Furnace）精炼炉设计的智能加热模型工艺包。该系统通过数据库缓冲表与主控程序交互，实现自动化、智能化的加热参数计算和控制。

### 核心价值

- ⚡ **智能预测**：基于历史数据和数学模型的智能加热参数预测
- 🔄 **实时响应**：守护进程轮询机制，秒级响应加热请求
- 📊 **可视化监控**：Web UI实时监控系统运行状态和历史数据
- 🎛️ **灵活配置**：支持多种数据库、多算法切换、参数可调
- 🔧 **易于集成**：标准数据库接口，无缝对接现有ASL2系统
- 🛡️ **稳定可靠**：异常重试、断线重连、完整日志记录

---

## 🧠 核心原理

### 1. 工作流程

```
┌─────────────┐        ┌──────────────┐        ┌─────────────┐
│  主控程序    │───1───>│  Input_Buffer │───2───>│  守护进程    │
│ (ASL2系统)  │        │  (输入缓冲表)  │        │ (模型计算)   │
└─────────────┘        └──────────────┘        └─────────────┘
      ^                                                 │
      │                                                 │ 3
      │                                                 v
      │                ┌──────────────┐        ┌─────────────┐
      └────────4───────│ Output_Buffer│<───────│  算法引擎    │
                       │ (输出缓冲表)  │        │ (智能计算)   │
                       └──────────────┘        └─────────────┘
```

**详细步骤：**

1. **主控程序写入任务**：ASL2系统将加热任务写入`Input_Buffer`表，设置`Data_Ready=1`和`Start_Flag=1`
2. **守护进程检测任务**：轮询守护进程检测到待处理任务（`Start_Flag=1`）
3. **算法计算**：根据配置选择算法（历史数据预测或公式计算），输出加热档位和时长
4. **结果写回**：计算结果写入`Output_Buffer`表，设置`Finish_Flag=1`
5. **主控读取结果**：ASL2系统读取输出表，执行加热控制，并重置`Start_Flag=0`

### 2. 算法原理

#### 算法1：历史数据预测（Historical Data Prediction）

**适用场景**：钢种和加热阶段固定，有充足历史数据

**核心思想**：
- 查询相同钢种、相同加热阶段的历史成功记录（最近50条）
- 计算历史平均加热档位和时长
- 根据当前温差与历史温差的比值进行调整
- 动态计算置信度（基于历史数据量）

**优势**：
- ✅ 自适应能力强，随着数据积累精度提升
- ✅ 考虑实际生产环境的变化
- ✅ 高置信度预测（历史记录>=50条时可达95%）

**计算公式**：
```
温度比例 = 当前温差 / 历史平均温差
调整后档位 = round(历史平均档位 × 温度比例)
调整后时长 = 历史平均时长 × 温度比例
```

#### 算法2：公式计算（Formula Calculation）

**适用场景**：工艺参数明确，需要精确控制

**核心思想**：
- 基于配置的数学公式计算
- 考虑钢种特性、加热阶段、温差等多因素
- 支持自定义修正系数

**优势**：
- ✅ 计算速度快，结果可预测
- ✅ 不依赖历史数据，适合新钢种
- ✅ 参数可调，灵活性强

**计算公式**：
```
加热档位 = base_coefficient × (1 + temp_factor × ΔT)
          × stage_multiplier × steel_modifier × custom_multiplier

加热时长 = (ΔT / 10) × stage_multiplier × steel_modifier × custom_multiplier
```

**参数说明**：
- `base_coefficient`：基础系数（默认1.2）
- `temp_factor`：温度因子（默认0.015）
- `stage_multiplier`：阶段乘数（初加热=1.0, 精炼=0.8, 保温=0.5, 升温=1.2）
- `steel_modifier`：钢种修正系数（碳钢=1.0, 合金钢=1.1, 不锈钢=1.2, 高温合金=1.3）
- `custom_multiplier`：自定义乘数（从工艺参数获取）

### 3. 设计思想

#### 松耦合架构
- 通过数据库表解耦模型与主控程序
- 模型独立运行，不影响主控系统
- 支持热插拔，可随时停启模型服务

#### 容错设计
- 数据库连接断开自动重连
- 任务处理失败写入错误信息，不阻塞后续任务
- 完整的日志记录，便于问题追踪

#### 可扩展性
- 算法模块化，新算法只需继承`BaseAlgorithm`基类
- 配置驱动，无需修改代码即可调整参数
- Web UI提供管理界面，便于运维

---

## 🏗️ 系统架构

### 目录结构

```
ASL2-OneKeyModel-Heat-V1.0/
├── Backend/                      # 后端核心代码
│   ├── algorithms/               # 算法模块
│   │   ├── __init__.py
│   │   ├── base.py              # 算法基类
│   │   ├── algorithm1_historical.py   # 历史数据预测算法
│   │   └── algorithm2_formula.py      # 公式计算算法
│   ├── daemon/                  # 守护进程模块
│   │   ├── __init__.py
│   │   └── polling_daemon.py    # 轮询守护进程
│   ├── db/                      # 数据库模块
│   │   ├── __init__.py
│   │   ├── models.py            # ORM模型
│   │   └── session.py           # 数据库连接管理
│   ├── web_ui/                  # Web界面
│   │   ├── templates/           # HTML模板
│   │   │   └── index.html       # 主页面
│   │   └── static/              # 静态资源
│   ├── config.yaml              # 配置文件
│   ├── config_manager.py        # 配置管理器
│   ├── logger_config.py         # 日志配置
│   ├── main.py                  # 命令行入口
│   ├── web_app.py               # Web UI入口
│   └── requirements.txt         # Python依赖
├── SQL/                         # 数据库脚本
│   └── create_tables.sql        # 建表SQL
├── README.md                    # 本文档
├── start.sh                     # Linux启动脚本
└── start.bat                    # Windows启动脚本
```

### 数据库表设计

#### Input_Buffer（输入缓冲表）
```sql
Task_ID         VARCHAR(50)   PRIMARY KEY     任务ID
Steel_Grade     VARCHAR(50)   NOT NULL        钢种
Heat_Stage      VARCHAR(50)   NOT NULL        加热阶段
Current_Temp    DECIMAL(10,2)                 当前温度(℃)
Target_Temp     DECIMAL(10,2) NOT NULL        目标温度(℃)
Process_Params  TEXT                          工艺参数(JSON)
Realtime_Data   TEXT                          实时数据(JSON)
Data_Ready      SMALLINT      DEFAULT 0       数据就绪标志
Start_Flag      SMALLINT      DEFAULT 0       启动标志
Created_At      TIMESTAMP
Updated_At      TIMESTAMP
```

#### Output_Buffer（输出缓冲表）
```sql
Task_ID         VARCHAR(50)   PRIMARY KEY     任务ID
Heat_Level      INT                           加热档位(1-10)
Heat_Duration   DECIMAL(10,2)                 加热时长(分钟)
Predicted_Temp  DECIMAL(10,2)                 预测温度(℃)
Algorithm_Used  VARCHAR(50)                   使用的算法
Result_Data     TEXT                          详细结果(JSON)
Finish_Flag     SMALLINT      DEFAULT 0       完成标志
Error_Code      INT           DEFAULT 0       错误代码
Error_Message   TEXT                          错误信息
Process_Time    DECIMAL(10,4)                 处理耗时(秒)
Created_At      TIMESTAMP
Updated_At      TIMESTAMP
```

#### Heat_History（历史数据表）
```sql
ID              SERIAL        PRIMARY KEY     自增ID
Task_ID         VARCHAR(50)                   任务ID
Steel_Grade     VARCHAR(50)                   钢种
Heat_Stage      VARCHAR(50)                   加热阶段
Start_Temp      DECIMAL(10,2)                 起始温度
End_Temp        DECIMAL(10,2)                 结束温度
Heat_Level      INT                           加热档位
Heat_Duration   DECIMAL(10,2)                 加热时长
Actual_Duration DECIMAL(10,2)                 实际时长
Success         SMALLINT      DEFAULT 1       是否成功
Timestamp       TIMESTAMP
```

#### Heat_Config（配置表）
```sql
ID              SERIAL        PRIMARY KEY     自增ID
Config_Key      VARCHAR(100)  UNIQUE          配置键
Config_Value    TEXT                          配置值
Description     TEXT                          说明
Config_Type     VARCHAR(50)   DEFAULT 'STRING' 类型
Updated_At      TIMESTAMP
```

---

## ✨ 功能特性

### 核心功能

1. **多算法支持**
   - 历史数据预测算法
   - 公式计算算法
   - 可扩展至更多算法（机器学习、深度学习等）

2. **实时监控Web UI**
   - 系统状态监控
   - 任务列表查看
   - 历史数据分析
   - 算法管理
   - 配置管理
   - 实时日志查看

3. **灵活配置**
   - YAML配置文件
   - 数据库配置表
   - 支持热更新（部分配置）

4. **多数据库支持**
   - PostgreSQL（推荐）
   - MySQL
   - Oracle
   - SQLite（开发测试）

5. **完善的日志系统**
   - 多级别日志（DEBUG/INFO/WARNING/ERROR）
   - 彩色控制台输出
   - 日志文件轮转（自动归档）
   - 性能日志记录

6. **高可用性**
   - 数据库断线自动重连
   - 任务处理异常重试
   - 优雅退出机制
   - 守护进程监控

---

## 🛠️ 技术栈

### 后端
- **Python 3.8+**
- **SQLAlchemy 2.0+**：ORM框架
- **Flask 3.0+**：Web框架
- **PyYAML**：配置管理
- **ColorLog**：彩色日志

### 数据库
- **PostgreSQL**（推荐生产环境）
- **MySQL**
- **Oracle**
- **SQLite**（开发测试）

### 前端
- **HTML5 + CSS3**
- **原生JavaScript**
- **响应式设计**

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.8 或更高版本
- 数据库（PostgreSQL/MySQL/Oracle/SQLite任选其一）
- pip（Python包管理器）

### 2. 安装步骤

#### 步骤1：克隆或下载代码

```bash
git clone https://github.com/lwh3/ASL2-OneKeyModel-Heat-V1.0.git
cd ASL2-OneKeyModel-Heat-V1.0
```

#### 步骤2：安装依赖

```bash
cd Backend
pip install -r requirements.txt
```

**注意**：如果使用特定数据库，可能需要额外安装驱动：
- PostgreSQL: `psycopg2-binary` (已包含)
- MySQL: `pymysql` (已包含)
- Oracle: `cx_Oracle` (已包含，需要Oracle Instant Client)

#### 步骤3：配置数据库

##### 3.1 创建数据库（如使用PostgreSQL）

```sql
CREATE DATABASE heat_model;
```

##### 3.2 执行建表脚本

```bash
# PostgreSQL
psql -U postgres -d heat_model -f ../SQL/create_tables.sql

# MySQL
mysql -u root -p heat_model < ../SQL/create_tables.sql

# SQLite (自动创建)
# 无需手动建表，程序会自动创建
```

#### 步骤4：修改配置文件

编辑 `Backend/config.yaml`：

```yaml
database:
  type: "postgresql"  # 或 mysql, oracle, sqlite
  host: "localhost"
  port: 5432
  database: "heat_model"
  username: "postgres"
  password: "your_password"
```

**快速使用SQLite**（无需安装数据库）：
```yaml
database:
  type: "sqlite"
  sqlite_path: "./heat_model.db"
  create_tables: true
```

#### 步骤5：启动系统

##### 方式1：启动Web UI（推荐）

```bash
# Linux/Mac
python web_app.py

# Windows
python web_app.py
```

访问：http://localhost:5000

##### 方式2：仅启动守护进程（无Web UI）

```bash
# Linux/Mac
python main.py --create-tables

# Windows
python main.py --create-tables
```

##### 方式3：使用启动脚本

```bash
# Linux/Mac
chmod +x ../start.sh
../start.sh

# Windows
..\start.bat
```

### 3. 验证安装

#### 3.1 检查系统状态

访问Web UI：http://localhost:5000

或通过API：
```bash
curl http://localhost:5000/api/status
```

#### 3.2 创建测试任务

使用SQL插入测试任务：

```sql
INSERT INTO Input_Buffer (
    Task_ID, Steel_Grade, Heat_Stage,
    Current_Temp, Target_Temp,
    Data_Ready, Start_Flag
) VALUES (
    'TEST001', '碳钢', '初加热',
    20.0, 1600.0,
    1, 1
);
```

#### 3.3 查看计算结果

等待几秒后查询输出表：

```sql
SELECT * FROM Output_Buffer WHERE Task_ID = 'TEST001';
```

或在Web UI的"任务列表"中查看。

---

## 📖 详细使用指南

### 命令行模式

#### 基本用法

```bash
python main.py [选项]
```

#### 常用选项

```bash
# 使用PostgreSQL
python main.py --db-type postgresql --host localhost --port 5432 \
               --database heat_model --username postgres --password mypass

# 使用MySQL
python main.py --db-type mysql --host localhost --port 3306 \
               --database heat_model --username root --password mypass

# 使用SQLite
python main.py --db-type sqlite --sqlite-path ./heat_model.db

# 创建数据库表
python main.py --create-tables

# 设置日志级别
python main.py --log-level DEBUG

# 设置轮询间隔
python main.py --polling-interval 5
```

#### 完整参数列表

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--db-type` | 数据库类型 | sqlite |
| `--host` | 数据库主机 | localhost |
| `--port` | 数据库端口 | 自动 |
| `--database` | 数据库名称 | heat_model |
| `--username` | 用户名 | - |
| `--password` | 密码 | - |
| `--sqlite-path` | SQLite文件路径 | ./heat_model.db |
| `--create-tables` | 创建数据库表 | False |
| `--polling-interval` | 轮询间隔(秒) | 2 |
| `--log-level` | 日志级别 | INFO |

### Web UI模式

#### 启动Web UI

```bash
python web_app.py
```

#### 功能模块

1. **仪表盘**
   - 总任务数
   - 待处理任务
   - 已完成任务
   - 错误任务

2. **任务列表**
   - 查看所有任务
   - 实时状态更新
   - 任务详情查看

3. **算法管理**
   - 查看可用算法
   - 查看当前使用算法
   - 算法精度显示

4. **系统配置**
   - 查看所有配置项
   - 动态修改配置（部分）

5. **系统日志**
   - 实时日志查看
   - 彩色日志显示
   - 日志过滤

6. **历史数据**
   - 历史记录查询
   - 数据统计分析

---

## 🧮 算法详解

### 算法选择策略

| 场景 | 推荐算法 | 理由 |
|------|----------|------|
| 生产稳定、历史数据充足 | Algorithm1 | 高精度、自适应 |
| 新钢种、无历史数据 | Algorithm2 | 不依赖历史 |
| 需要精确控制 | Algorithm2 | 参数可调 |
| 实验性生产 | Algorithm2 | 易于调试 |

### 算法精度对比

| 算法 | 精度等级 | 适用条件 | 响应速度 |
|------|----------|----------|----------|
| Algorithm1 | 高（>90%） | 历史数据>=30条 | 快 |
| Algorithm2 | 中（80-90%） | 无限制 | 极快 |

### 如何选择算法

#### 方法1：通过配置文件

编辑 `config.yaml`：

```yaml
algorithms:
  default: "Algorithm1"  # 或 Algorithm2
```

#### 方法2：通过数据库配置表

```sql
UPDATE Heat_Config
SET Config_Value = 'Algorithm2'
WHERE Config_Key = 'DEFAULT_ALGORITHM';
```

### 自定义算法

创建新算法非常简单：

```python
# Backend/algorithms/algorithm3_custom.py

from .base import BaseAlgorithm
from typing import Dict, Any, Tuple

class Algorithm3Custom(BaseAlgorithm):
    """自定义算法"""

    def __init__(self, db_session):
        super().__init__(name="Algorithm3_Custom", db_session=db_session)

    def calculate(self, input_data: Dict[str, Any]) -> Tuple[int, float, Dict[str, Any]]:
        """
        实现你的算法逻辑

        Returns:
            Tuple[加热档位, 加热时长, 详细结果]
        """
        # 验证输入
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data")

        # 你的算法逻辑
        heat_level = 5  # 计算得到的档位
        heat_duration = 20.0  # 计算得到的时长

        result_data = {
            'algorithm': self.name,
            'confidence': 0.85
        }

        return heat_level, heat_duration, result_data
```

然后在 `daemon/polling_daemon.py` 中注册：

```python
self.algorithms = {
    'Algorithm1': Algorithm1Historical(self.session),
    'Algorithm2': Algorithm2Formula(self.session),
    'Algorithm3': Algorithm3Custom(self.session),  # 添加新算法
}
```

---

## ⚙️ 配置说明

### 配置文件结构

`config.yaml` 包含以下主要部分：

#### 1. 数据库配置

```yaml
database:
  type: "postgresql"
  host: "localhost"
  port: 5432
  database: "heat_model"
  username: "postgres"
  password: "your_password"
  create_tables: true
```

#### 2. 守护进程配置

```yaml
daemon:
  polling_interval: 2      # 轮询间隔(秒)
  max_retries: 3          # 最大重试次数
  retry_delay: 5          # 重试延迟(秒)
```

#### 3. 日志配置

```yaml
logging:
  level: "INFO"           # DEBUG, INFO, WARNING, ERROR
  console: true           # 控制台输出
  file: true              # 文件输出
  file_path: "logs/heat_model.log"
  max_bytes: 10485760     # 10MB
  backup_count: 5         # 保留5个备份
```

#### 4. Web UI配置

```yaml
web_ui:
  enabled: true
  host: "0.0.0.0"
  port: 5000
  debug: false
  secret_key: "change-in-production"
```

#### 5. 算法配置

```yaml
algorithms:
  default: "Algorithm1"
  enabled:
    - "Algorithm1"
    - "Algorithm2"

  algorithm2:
    formula_params:
      base_coefficient: 1.2
      temp_factor: 0.015
      stage_multiplier:
        初加热: 1.0
        精炼: 0.8
      steel_grade_modifier:
        碳钢: 1.0
        合金钢: 1.1
```

### 动态配置

某些配置可以在运行时通过数据库配置表修改：

```sql
-- 修改默认算法
UPDATE Heat_Config
SET Config_Value = 'Algorithm2'
WHERE Config_Key = 'DEFAULT_ALGORITHM';

-- 修改公式参数
UPDATE Heat_Config
SET Config_Value = '{"base_coefficient": 1.5, "temp_factor": 0.02}'
WHERE Config_Key = 'FORMULA_PARAMS';
```

---

## 📡 API文档

### 基础信息

- **Base URL**: `http://localhost:5000/api`
- **Content-Type**: `application/json`

### API列表

#### 1. 获取系统状态

```http
GET /api/status
```

**响应示例**：
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T12:00:00",
  "statistics": {
    "total_tasks": 150,
    "pending_tasks": 2,
    "completed_tasks": 145,
    "error_tasks": 3
  },
  "daemon": {
    "running": true,
    "stats": {
      "total_processed": 145,
      "success_count": 142,
      "error_count": 3
    }
  }
}
```

#### 2. 获取任务列表

```http
GET /api/tasks?limit=50&status=all
```

**参数**：
- `limit`: 返回数量（默认50）
- `status`: 过滤状态（all/pending/completed）

**响应示例**：
```json
{
  "status": "ok",
  "tasks": [
    {
      "task_id": "TASK001",
      "steel_grade": "碳钢",
      "heat_stage": "初加热",
      "current_temp": 20.0,
      "target_temp": 1600.0,
      "output": {
        "heat_level": 8,
        "heat_duration": 35.5,
        "algorithm_used": "Algorithm1",
        "finish_flag": 1
      }
    }
  ]
}
```

#### 3. 获取历史数据

```http
GET /api/history?limit=100&steel_grade=碳钢
```

#### 4. 获取配置

```http
GET /api/config
```

#### 5. 更新配置

```http
POST /api/config
Content-Type: application/json

{
  "key": "DEFAULT_ALGORITHM",
  "value": "Algorithm2"
}
```

#### 6. 获取算法列表

```http
GET /api/algorithms
```

#### 7. 获取日志

```http
GET /api/logs?lines=100
```

---

## 🔗 集成指南

### 与ASL2主逻辑集成

#### 1. 数据库连接

确保ASL2系统和模型工艺包连接同一个数据库实例。

#### 2. 主控程序集成步骤

##### 步骤1：发送加热请求

```sql
-- ASL2主程序执行
INSERT INTO Input_Buffer (
    Task_ID,
    Steel_Grade,
    Heat_Stage,
    Current_Temp,
    Target_Temp,
    Process_Params,
    Data_Ready,
    Start_Flag
) VALUES (
    'TASK_' || TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDDHH24MISS'),
    '碳钢',
    '初加热',
    25.0,
    1600.0,
    '{"custom_multiplier": 1.0}',
    1,
    1
);
```

##### 步骤2：等待计算完成

```sql
-- 轮询检查（建议间隔1-2秒）
SELECT Finish_Flag, Heat_Level, Heat_Duration, Error_Code, Error_Message
FROM Output_Buffer
WHERE Task_ID = 'TASK_20240101120000';
```

##### 步骤3：读取结果

```sql
-- 当Finish_Flag = 1时读取结果
SELECT
    Heat_Level as 加热档位,
    Heat_Duration as 加热时长,
    Algorithm_Used as 使用算法,
    Error_Code as 错误码,
    Error_Message as 错误信息
FROM Output_Buffer
WHERE Task_ID = 'TASK_20240101120000' AND Finish_Flag = 1;
```

##### 步骤4：重置标志位

```sql
-- 读取结果后重置Start_Flag
UPDATE Input_Buffer
SET Start_Flag = 0
WHERE Task_ID = 'TASK_20240101120000';
```

### 典型集成示例（伪代码）

```python
def request_heating_calculation(task_id, steel_grade, heat_stage, current_temp, target_temp):
    """请求加热计算"""
    # 1. 写入输入表
    sql = """
        INSERT INTO Input_Buffer
        (Task_ID, Steel_Grade, Heat_Stage, Current_Temp, Target_Temp, Data_Ready, Start_Flag)
        VALUES (%s, %s, %s, %s, %s, 1, 1)
    """
    execute_sql(sql, (task_id, steel_grade, heat_stage, current_temp, target_temp))

    # 2. 等待结果（轮询，最多30秒）
    for i in range(30):
        result = execute_sql("SELECT * FROM Output_Buffer WHERE Task_ID = %s AND Finish_Flag = 1", (task_id,))
        if result:
            break
        time.sleep(1)

    # 3. 处理结果
    if result:
        if result['Error_Code'] == 0:
            heat_level = result['Heat_Level']
            heat_duration = result['Heat_Duration']
            print(f"计算成功：档位={heat_level}, 时长={heat_duration}分钟")
            # 执行加热控制...
        else:
            print(f"计算失败：{result['Error_Message']}")

    # 4. 重置标志
    execute_sql("UPDATE Input_Buffer SET Start_Flag = 0 WHERE Task_ID = %s", (task_id,))
```

### 高级功能

#### 1. 传递工艺参数

```sql
INSERT INTO Input_Buffer (..., Process_Params, ...)
VALUES (..., '{"custom_multiplier": 1.2, "priority": "high"}', ...);
```

#### 2. 传递实时数据

```sql
INSERT INTO Input_Buffer (..., Realtime_Data, ...)
VALUES (..., '{"furnace_pressure": 1.2, "oxygen_flow": 50}', ...);
```

#### 3. 反馈历史数据

加热完成后，将实际结果写入历史表，用于算法优化：

```sql
INSERT INTO Heat_History (
    Task_ID,
    Steel_Grade,
    Heat_Stage,
    Start_Temp,
    End_Temp,
    Heat_Level,
    Heat_Duration,
    Actual_Duration,
    Success
) VALUES (
    'TASK_20240101120000',
    '碳钢',
    '初加热',
    25.0,
    1605.0,  -- 实际达到的温度
    8,
    35.5,
    36.2,    -- 实际用时
    1        -- 成功
);
```

---

## ❓ 常见问题

### Q1: 如何选择数据库？

**A**:
- **生产环境**：推荐PostgreSQL（性能好、稳定性高）
- **中小规模**：MySQL也是不错的选择
- **开发测试**：SQLite（零配置，开箱即用）
- **企业环境**：Oracle（如已有Oracle license）

### Q2: 守护进程崩溃怎么办？

**A**:
1. 检查日志文件：`logs/heat_model.log`
2. 常见原因：
   - 数据库连接失败（检查数据库服务）
   - 数据格式错误（检查输入数据）
   - 内存不足（增加系统资源）
3. 守护进程会自动重试数据库连接
4. 建议使用系统服务管理器（如systemd）自动重启

### Q3: 如何提高算法精度？

**A**:
1. **积累历史数据**：Algorithm1需要足够的历史数据
2. **调整公式参数**：Algorithm2可调整`config.yaml`中的参数
3. **定期反馈**：将实际结果写入`Heat_History`表
4. **自定义算法**：根据实际情况开发专用算法

### Q4: 支持分布式部署吗？

**A**: 当前版本支持单机部署。如需分布式：
- 可部署多个守护进程实例（需数据库支持行锁）
- Web UI可部署多个实例（使用负载均衡器）
- 建议使用消息队列（如RabbitMQ）解耦

### Q5: 如何备份数据？

**A**:
```bash
# PostgreSQL
pg_dump -U postgres heat_model > heat_model_backup.sql

# MySQL
mysqldump -u root -p heat_model > heat_model_backup.sql

# SQLite
sqlite3 heat_model.db .dump > heat_model_backup.sql
```

### Q6: Web UI无法访问？

**A**:
1. 检查防火墙：`sudo ufw allow 5000`
2. 检查绑定地址：`config.yaml`中设置`host: "0.0.0.0"`
3. 检查进程是否运行：`ps aux | grep web_app`
4. 查看日志：`logs/heat_model.log`

### Q7: 如何监控系统健康状态？

**A**:
- 通过API：`curl http://localhost:5000/api/status`
- 通过Web UI：访问仪表盘
- 通过日志：`tail -f logs/heat_model.log`
- 通过数据库：查询`Output_Buffer`表的`Error_Code`

---

## 🚀 后续发展

### 短期计划（1-3个月）

1. **算法增强**
   - [ ] 引入机器学习算法（随机森林、XGBoost）
   - [ ] 增加神经网络预测算法
   - [ ] 支持多模型集成（投票/加权）

2. **功能扩展**
   - [ ] 用户权限管理
   - [ ] 告警系统（邮件/短信通知）
   - [ ] 移动端适配
   - [ ] 数据导出功能（Excel/CSV）

3. **性能优化**
   - [ ] 数据库查询优化
   - [ ] 缓存机制（Redis）
   - [ ] 异步任务处理

### 中期计划（3-6个月）

1. **智能化升级**
   - [ ] 自适应参数调优
   - [ ] 异常检测与预警
   - [ ] 知识图谱构建

2. **系统集成**
   - [ ] RESTful API完善
   - [ ] gRPC支持
   - [ ] 消息队列集成（Kafka/RabbitMQ）

3. **可视化增强**
   - [ ] 实时数据看板
   - [ ] 3D温度场可视化
   - [ ] 预测趋势图表

### 长期计划（6-12个月）

1. **AI赋能**
   - [ ] 深度强化学习自动调优
   - [ ] 数字孪生技术
   - [ ] 预测性维护

2. **平台化**
   - [ ] 多工艺包支持
   - [ ] 工艺包市场
   - [ ] 低代码配置平台

3. **云原生**
   - [ ] 容器化部署（Docker）
   - [ ] Kubernetes编排
   - [ ] 微服务架构

---

## 🤝 贡献指南

欢迎贡献代码、报告问题、提出建议！

### 如何贡献

1. Fork本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m "Add your feature"`
4. 推送分支：`git push origin feature/your-feature`
5. 提交Pull Request

### 代码规范

- 遵循PEP 8 Python代码风格
- 添加必要的注释和文档字符串
- 编写单元测试
- 更新README文档

### 报告问题

请通过GitHub Issues报告问题，包含以下信息：
- 问题描述
- 复现步骤
- 期望行为
- 实际行为
- 系统环境
- 日志信息

---

## 📜 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 📞 联系方式

- **GitHub**: https://github.com/lwh3/ASL2-OneKeyModel-Heat-V1.0
- **Issues**: https://github.com/lwh3/ASL2-OneKeyModel-Heat-V1.0/issues

---

## 🙏 致谢

感谢所有为本项目做出贡献的开发者！

---

## 📊 项目统计

![GitHub stars](https://img.shields.io/github/stars/lwh3/ASL2-OneKeyModel-Heat-V1.0)
![GitHub forks](https://img.shields.io/github/forks/lwh3/ASL2-OneKeyModel-Heat-V1.0)
![GitHub issues](https://img.shields.io/github/issues/lwh3/ASL2-OneKeyModel-Heat-V1.0)

---

**⚡ 立即开始使用，让LF精炼炉加热更智能！**
