using System.Collections.Generic;
using System.Threading.Tasks;
using HeatModelMonitor.Models;

namespace HeatModelMonitor.Services
{
    public interface IApiService
    {
        Task<SystemStatus> GetStatusAsync();
        Task<List<TaskItem>> GetTasksAsync(string status = "all", int limit = 50);
        Task<List<HistoryRecord>> GetHistoryAsync(string steelGrade = null, int limit = 100);
        Task<List<ConfigItem>> GetConfigAsync();
        Task<bool> UpdateConfigAsync(string key, string value);
        Task<AlgorithmInfo> GetAlgorithmsAsync();
        Task<List<string>> GetLogsAsync(int lines = 100);
    }
}
