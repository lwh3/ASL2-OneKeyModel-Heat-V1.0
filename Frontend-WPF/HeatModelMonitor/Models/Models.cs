using System;
using System.Collections.Generic;

namespace HeatModelMonitor.Models
{
    public class SystemStatus
    {
        public string Status { get; set; }
        public DateTime Timestamp { get; set; }
        public Statistics Statistics { get; set; }
        public DaemonStatus Daemon { get; set; }
    }

    public class Statistics
    {
        public int TotalTasks { get; set; }
        public int PendingTasks { get; set; }
        public int CompletedTasks { get; set; }
        public int ErrorTasks { get; set; }
    }

    public class DaemonStatus
    {
        public bool Running { get; set; }
        public Dictionary<string, int> Stats { get; set; }
    }

    public class TaskItem
    {
        public string TaskId { get; set; }
        public string SteelGrade { get; set; }
        public string HeatStage { get; set; }
        public double? CurrentTemp { get; set; }
        public double TargetTemp { get; set; }
        public int DataReady { get; set; }
        public int StartFlag { get; set; }
        public DateTime? CreatedAt { get; set; }
        public TaskOutput Output { get; set; }
    }

    public class TaskOutput
    {
        public int HeatLevel { get; set; }
        public double? HeatDuration { get; set; }
        public string AlgorithmUsed { get; set; }
        public int FinishFlag { get; set; }
        public int ErrorCode { get; set; }
        public string ErrorMessage { get; set; }
        public double? ProcessTime { get; set; }
    }

    public class HistoryRecord
    {
        public int Id { get; set; }
        public string TaskId { get; set; }
        public string SteelGrade { get; set; }
        public string HeatStage { get; set; }
        public double? StartTemp { get; set; }
        public double? EndTemp { get; set; }
        public int HeatLevel { get; set; }
        public double? HeatDuration { get; set; }
        public int Success { get; set; }
        public DateTime? Timestamp { get; set; }
    }

    public class ConfigItem
    {
        public int Id { get; set; }
        public string Key { get; set; }
        public string Value { get; set; }
        public string Description { get; set; }
        public string Type { get; set; }
    }

    public class AlgorithmInfo
    {
        public string Default { get; set; }
        public List<string> Enabled { get; set; }
    }
}
