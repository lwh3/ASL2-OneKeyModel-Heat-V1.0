using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using RestSharp;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Microsoft.Extensions.Configuration;
using HeatModelMonitor.Models;

namespace HeatModelMonitor.Services
{
    public class ApiService : IApiService
    {
        private readonly RestClient _client;
        private readonly string _baseUrl;

        public ApiService(IConfiguration configuration)
        {
            _baseUrl = configuration["ApiSettings:BaseUrl"] ?? "http://localhost:5000/api";
            var options = new RestClientOptions(_baseUrl)
            {
                MaxTimeout = (int)TimeSpan.FromSeconds(
                    int.Parse(configuration["ApiSettings:Timeout"] ?? "30")
                ).TotalMilliseconds
            };
            _client = new RestClient(options);
        }

        public async Task<SystemStatus> GetStatusAsync()
        {
            var request = new RestRequest("/status", Method.Get);
            var response = await _client.ExecuteAsync(request);

            if (!response.IsSuccessful)
                throw new Exception($"API Error: {response.ErrorMessage}");

            var result = JsonConvert.DeserializeObject<JObject>(response.Content);
            return JsonConvert.DeserializeObject<SystemStatus>(response.Content);
        }

        public async Task<List<TaskItem>> GetTasksAsync(string status = "all", int limit = 50)
        {
            var request = new RestRequest("/tasks", Method.Get);
            request.AddParameter("status", status);
            request.AddParameter("limit", limit);

            var response = await _client.ExecuteAsync(request);

            if (!response.IsSuccessful)
                throw new Exception($"API Error: {response.ErrorMessage}");

            var result = JsonConvert.DeserializeObject<JObject>(response.Content);
            return result["tasks"]?.ToObject<List<TaskItem>>() ?? new List<TaskItem>();
        }

        public async Task<List<HistoryRecord>> GetHistoryAsync(string steelGrade = null, int limit = 100)
        {
            var request = new RestRequest("/history", Method.Get);
            if (!string.IsNullOrEmpty(steelGrade))
                request.AddParameter("steel_grade", steelGrade);
            request.AddParameter("limit", limit);

            var response = await _client.ExecuteAsync(request);

            if (!response.IsSuccessful)
                throw new Exception($"API Error: {response.ErrorMessage}");

            var result = JsonConvert.DeserializeObject<JObject>(response.Content);
            return result["history"]?.ToObject<List<HistoryRecord>>() ?? new List<HistoryRecord>();
        }

        public async Task<List<ConfigItem>> GetConfigAsync()
        {
            var request = new RestRequest("/config", Method.Get);
            var response = await _client.ExecuteAsync(request);

            if (!response.IsSuccessful)
                throw new Exception($"API Error: {response.ErrorMessage}");

            var result = JsonConvert.DeserializeObject<JObject>(response.Content);
            return result["configs"]?.ToObject<List<ConfigItem>>() ?? new List<ConfigItem>();
        }

        public async Task<bool> UpdateConfigAsync(string key, string value)
        {
            var request = new RestRequest("/config", Method.Post);
            request.AddJsonBody(new { key, value });

            var response = await _client.ExecuteAsync(request);
            return response.IsSuccessful;
        }

        public async Task<AlgorithmInfo> GetAlgorithmsAsync()
        {
            var request = new RestRequest("/algorithms", Method.Get);
            var response = await _client.ExecuteAsync(request);

            if (!response.IsSuccessful)
                throw new Exception($"API Error: {response.ErrorMessage}");

            var result = JsonConvert.DeserializeObject<JObject>(response.Content);
            return result["algorithms"]?.ToObject<AlgorithmInfo>() ?? new AlgorithmInfo();
        }

        public async Task<List<string>> GetLogsAsync(int lines = 100)
        {
            var request = new RestRequest("/logs", Method.Get);
            request.AddParameter("lines", lines);

            var response = await _client.ExecuteAsync(request);

            if (!response.IsSuccessful)
                throw new Exception($"API Error: {response.ErrorMessage}");

            var result = JsonConvert.DeserializeObject<JObject>(response.Content);
            return result["logs"]?.ToObject<List<string>>() ?? new List<string>();
        }
    }
}
