-- =====================================================
-- LF精炼炉加热模型工艺包 - 数据库建表脚本
-- 支持: PostgreSQL (推荐), MySQL, Oracle, SQLite
-- =====================================================

-- 1. 输入缓冲表 (Input_Buffer)
CREATE TABLE IF NOT EXISTS Input_Buffer (
    Task_ID VARCHAR(50) PRIMARY KEY,
    Steel_Grade VARCHAR(50) NOT NULL,              -- 钢种
    Heat_Stage VARCHAR(50) NOT NULL,               -- 加热阶段 (初加热/精炼/保温等)
    Current_Temp DECIMAL(10, 2),                   -- 当前温度 (℃)
    Target_Temp DECIMAL(10, 2) NOT NULL,           -- 目标温度 (℃)
    Process_Params TEXT,                           -- 工艺参数 (JSON格式)
    Realtime_Data TEXT,                            -- 实时采集数据 (JSON格式)
    Data_Ready SMALLINT DEFAULT 0,                 -- 数据就绪标志 (0=未就绪, 1=就绪)
    Start_Flag SMALLINT DEFAULT 0,                 -- 启动标志 (0=未启动, 1=主程序置位启动)
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 输出缓冲表 (Output_Buffer)
CREATE TABLE IF NOT EXISTS Output_Buffer (
    Task_ID VARCHAR(50) PRIMARY KEY,
    Heat_Level INT,                                 -- 加热档位 (1-10档)
    Heat_Duration DECIMAL(10, 2),                   -- 加热时长 (分钟)
    Predicted_Temp DECIMAL(10, 2),                  -- 预测达到温度 (℃)
    Algorithm_Used VARCHAR(50),                     -- 使用的算法 (Algorithm1/Algorithm2)
    Result_Data TEXT,                               -- 详细结果数据 (JSON格式)
    Finish_Flag SMALLINT DEFAULT 0,                 -- 完成标志 (0=未完成, 1=模型置位完成)
    Error_Code INT DEFAULT 0,                       -- 错误代码 (0=成功)
    Error_Message TEXT,                             -- 错误信息
    Process_Time DECIMAL(10, 4),                    -- 处理耗时 (秒)
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Task_ID) REFERENCES Input_Buffer(Task_ID)
);

-- 3. 加热历史表 (Heat_History)
CREATE TABLE IF NOT EXISTS Heat_History (
    ID SERIAL PRIMARY KEY,                          -- PostgreSQL自增主键 (MySQL用AUTO_INCREMENT, Oracle用SEQUENCE)
    Task_ID VARCHAR(50),
    Steel_Grade VARCHAR(50),
    Heat_Stage VARCHAR(50),
    Start_Temp DECIMAL(10, 2),
    End_Temp DECIMAL(10, 2),
    Heat_Level INT,
    Heat_Duration DECIMAL(10, 2),
    Actual_Duration DECIMAL(10, 2),                 -- 实际加热时长
    Success SMALLINT DEFAULT 1,                     -- 是否成功 (0=失败, 1=成功)
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Task_ID) REFERENCES Input_Buffer(Task_ID)
);

-- 4. 加热配置表 (Heat_Config)
CREATE TABLE IF NOT EXISTS Heat_Config (
    ID SERIAL PRIMARY KEY,
    Config_Key VARCHAR(100) UNIQUE NOT NULL,        -- 配置项键
    Config_Value TEXT,                              -- 配置项值 (支持JSON)
    Description TEXT,                               -- 配置说明
    Config_Type VARCHAR(50) DEFAULT 'STRING',       -- 配置类型 (STRING/INT/FLOAT/JSON)
    Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入默认配置
INSERT INTO Heat_Config (Config_Key, Config_Value, Description, Config_Type) VALUES
('DEFAULT_ALGORITHM', 'Algorithm1', '默认算法选择 (Algorithm1=历史数据预测, Algorithm2=公式计算)', 'STRING'),
('POLLING_INTERVAL', '2', '轮询间隔时间 (秒)', 'INT'),
('MAX_HEAT_LEVEL', '10', '最大加热档位', 'INT'),
('MIN_HEAT_LEVEL', '1', '最小加热档位', 'INT'),
('FORMULA_PARAMS', '{"base_coefficient": 1.2, "temp_factor": 0.015}', '公式计算参数 (Algorithm2专用)', 'JSON')
ON CONFLICT (Config_Key) DO NOTHING;

-- 索引优化
CREATE INDEX IF NOT EXISTS idx_input_buffer_start_flag ON Input_Buffer(Start_Flag, Data_Ready);
CREATE INDEX IF NOT EXISTS idx_output_buffer_finish_flag ON Output_Buffer(Finish_Flag);
CREATE INDEX IF NOT EXISTS idx_heat_history_steel_grade ON Heat_History(Steel_Grade, Heat_Stage);
CREATE INDEX IF NOT EXISTS idx_heat_history_timestamp ON Heat_History(Timestamp);

-- 注意事项:
-- 1. PostgreSQL: 使用 SERIAL 自增, CURRENT_TIMESTAMP
-- 2. MySQL: 将 SERIAL 改为 INT AUTO_INCREMENT, SMALLINT 改为 TINYINT
-- 3. Oracle: 使用 NUMBER + SEQUENCE + TRIGGER, CURRENT_TIMESTAMP 改为 SYSTIMESTAMP
-- 4. SQLite: 使用 INTEGER PRIMARY KEY AUTOINCREMENT, TIMESTAMP 用 TEXT 存储
