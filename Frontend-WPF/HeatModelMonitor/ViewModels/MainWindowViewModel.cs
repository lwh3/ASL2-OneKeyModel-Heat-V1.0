using Prism.Mvvm;
using Prism.Regions;
using Prism.Commands;
using System;
using System.Collections.ObjectModel;
using System.Windows.Input;
using System.Windows.Threading;
using System.Windows.Media;

namespace HeatModelMonitor.ViewModels
{
    public class MenuItem : BindableBase
    {
        public string Title { get; set; }
        public string Icon { get; set; }
        public string NavigationPath { get; set; }
    }

    public class MainWindowViewModel : BindableBase
    {
        private readonly IRegionManager _regionManager;
        private readonly DispatcherTimer _timer;

        private string _currentTitle = "仪表盘";
        private string _currentTime;
        private string _connectionStatus = "已连接";
        private Brush _connectionColor = Brushes.Green;
        private MenuItem _selectedMenuItem;

        public MainWindowViewModel(IRegionManager regionManager)
        {
            _regionManager = regionManager;

            // 初始化菜单项
            MenuItems = new ObservableCollection<MenuItem>
            {
                new MenuItem { Title = "仪表盘", Icon = "ViewDashboard", NavigationPath = "DashboardView" },
                new MenuItem { Title = "任务列表", Icon = "FormatListBulleted", NavigationPath = "TasksView" },
                new MenuItem { Title = "历史数据", Icon = "History", NavigationPath = "HistoryView" },
                new MenuItem { Title = "算法管理", Icon = "Cog", NavigationPath = "AlgorithmsView" },
                new MenuItem { Title = "系统配置", Icon = "Settings", NavigationPath = "ConfigView" },
                new MenuItem { Title = "系统日志", Icon = "FileDocument", NavigationPath = "LogsView" }
            };

            // 初始化定时器
            _timer = new DispatcherTimer
            {
                Interval = TimeSpan.FromSeconds(1)
            };
            _timer.Tick += Timer_Tick;
            _timer.Start();

            CurrentTime = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");

            // 默认导航到仪表盘
            _regionManager.RequestNavigate("ContentRegion", "DashboardView");
        }

        public ObservableCollection<MenuItem> MenuItems { get; }

        public string CurrentTitle
        {
            get => _currentTitle;
            set => SetProperty(ref _currentTitle, value);
        }

        public string CurrentTime
        {
            get => _currentTime;
            set => SetProperty(ref _currentTime, value);
        }

        public string ConnectionStatus
        {
            get => _connectionStatus;
            set => SetProperty(ref _connectionStatus, value);
        }

        public Brush ConnectionColor
        {
            get => _connectionColor;
            set => SetProperty(ref _connectionColor, value);
        }

        public MenuItem SelectedMenuItem
        {
            get => _selectedMenuItem;
            set
            {
                if (SetProperty(ref _selectedMenuItem, value) && value != null)
                {
                    CurrentTitle = value.Title;
                    _regionManager.RequestNavigate("ContentRegion", value.NavigationPath);
                }
            }
        }

        private void Timer_Tick(object sender, EventArgs e)
        {
            CurrentTime = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
        }
    }
}
