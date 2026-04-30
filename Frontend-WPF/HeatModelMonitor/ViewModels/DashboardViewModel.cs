using Prism.Mvvm;
using Prism.Commands;
using System;
using System.Collections.ObjectModel;
using System.Windows.Input;
using System.Windows.Threading;
using HeatModelMonitor.Services;
using HeatModelMonitor.Models;

namespace HeatModelMonitor.ViewModels
{
    public class DashboardViewModel : BindableBase
    {
        private readonly IApiService _apiService;
        private readonly DispatcherTimer _refreshTimer;

        private int _totalTasks;
        private int _pendingTasks;
        private int _completedTasks;
        private int _errorTasks;

        public DashboardViewModel(IApiService apiService)
        {
            _apiService = apiService;

            RecentTasks = new ObservableCollection<TaskItem>();

            RefreshCommand = new DelegateCommand(async () => await LoadDataAsync());

            // 自动刷新
            _refreshTimer = new DispatcherTimer
            {
                Interval = TimeSpan.FromSeconds(10)
            };
            _refreshTimer.Tick += async (s, e) => await LoadDataAsync();
            _refreshTimer.Start();

            // 初始加载
            LoadDataAsync().ConfigureAwait(false);
        }

        public ObservableCollection<TaskItem> RecentTasks { get; }

        public int TotalTasks
        {
            get => _totalTasks;
            set => SetProperty(ref _totalTasks, value);
        }

        public int PendingTasks
        {
            get => _pendingTasks;
            set => SetProperty(ref _pendingTasks, value);
        }

        public int CompletedTasks
        {
            get => _completedTasks;
            set => SetProperty(ref _completedTasks, value);
        }

        public int ErrorTasks
        {
            get => _errorTasks;
            set => SetProperty(ref _errorTasks, value);
        }

        public ICommand RefreshCommand { get; }

        private async System.Threading.Tasks.Task LoadDataAsync()
        {
            try
            {
                var status = await _apiService.GetStatusAsync();
                if (status?.Statistics != null)
                {
                    TotalTasks = status.Statistics.TotalTasks;
                    PendingTasks = status.Statistics.PendingTasks;
                    CompletedTasks = status.Statistics.CompletedTasks;
                    ErrorTasks = status.Statistics.ErrorTasks;
                }

                var tasks = await _apiService.GetTasksAsync(limit: 10);
                RecentTasks.Clear();
                foreach (var task in tasks)
                {
                    RecentTasks.Add(task);
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error loading data: {ex.Message}");
            }
        }
    }
}
