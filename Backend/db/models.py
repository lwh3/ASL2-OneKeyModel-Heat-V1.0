"""
SQLAlchemy ORM Models for Heat Model Package
支持多数据库: PostgreSQL, MySQL, Oracle, SQLite
"""

from sqlalchemy import Column, String, Integer, Numeric, Text, SmallInteger, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class InputBuffer(Base):
    """输入缓冲表 - 接收主程序的加热任务"""
    __tablename__ = 'Input_Buffer'

    Task_ID = Column(String(50), primary_key=True)
    Steel_Grade = Column(String(50), nullable=False)          # 钢种
    Heat_Stage = Column(String(50), nullable=False)           # 加热阶段
    Current_Temp = Column(Numeric(10, 2))                     # 当前温度
    Target_Temp = Column(Numeric(10, 2), nullable=False)      # 目标温度
    Process_Params = Column(Text)                             # 工艺参数 (JSON)
    Realtime_Data = Column(Text)                              # 实时采集数据 (JSON)
    Data_Ready = Column(SmallInteger, default=0)              # 数据就绪标志
    Start_Flag = Column(SmallInteger, default=0)              # 启动标志
    Created_At = Column(TIMESTAMP, default=datetime.utcnow)
    Updated_At = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<InputBuffer(Task_ID={self.Task_ID}, Steel_Grade={self.Steel_Grade}, Heat_Stage={self.Heat_Stage})>"


class OutputBuffer(Base):
    """输出缓冲表 - 模型计算结果输出"""
    __tablename__ = 'Output_Buffer'

    Task_ID = Column(String(50), ForeignKey('Input_Buffer.Task_ID'), primary_key=True)
    Heat_Level = Column(Integer)                              # 加热档位
    Heat_Duration = Column(Numeric(10, 2))                    # 加热时长 (分钟)
    Predicted_Temp = Column(Numeric(10, 2))                   # 预测温度
    Algorithm_Used = Column(String(50))                       # 使用的算法
    Result_Data = Column(Text)                                # 详细结果 (JSON)
    Finish_Flag = Column(SmallInteger, default=0)             # 完成标志
    Error_Code = Column(Integer, default=0)                   # 错误代码
    Error_Message = Column(Text)                              # 错误信息
    Process_Time = Column(Numeric(10, 4))                     # 处理耗时 (秒)
    Created_At = Column(TIMESTAMP, default=datetime.utcnow)
    Updated_At = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<OutputBuffer(Task_ID={self.Task_ID}, Heat_Level={self.Heat_Level}, Finish_Flag={self.Finish_Flag})>"


class HeatHistory(Base):
    """加热历史表 - 存储历史加热数据用于算法训练"""
    __tablename__ = 'Heat_History'

    ID = Column(Integer, primary_key=True, autoincrement=True)
    Task_ID = Column(String(50), ForeignKey('Input_Buffer.Task_ID'))
    Steel_Grade = Column(String(50))
    Heat_Stage = Column(String(50))
    Start_Temp = Column(Numeric(10, 2))
    End_Temp = Column(Numeric(10, 2))
    Heat_Level = Column(Integer)
    Heat_Duration = Column(Numeric(10, 2))
    Actual_Duration = Column(Numeric(10, 2))                  # 实际加热时长
    Success = Column(SmallInteger, default=1)                 # 是否成功
    Timestamp = Column(TIMESTAMP, default=datetime.utcnow)

    def __repr__(self):
        return f"<HeatHistory(ID={self.ID}, Steel_Grade={self.Steel_Grade}, Heat_Level={self.Heat_Level})>"


class HeatConfig(Base):
    """加热配置表 - 系统配置参数"""
    __tablename__ = 'Heat_Config'

    ID = Column(Integer, primary_key=True, autoincrement=True)
    Config_Key = Column(String(100), unique=True, nullable=False)
    Config_Value = Column(Text)
    Description = Column(Text)
    Config_Type = Column(String(50), default='STRING')        # STRING/INT/FLOAT/JSON
    Updated_At = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<HeatConfig(Config_Key={self.Config_Key}, Config_Value={self.Config_Value})>"
