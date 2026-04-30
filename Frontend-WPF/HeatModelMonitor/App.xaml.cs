using Prism.Ioc;
using Prism.Unity;
using System.Windows;
using HeatModelMonitor.Views;
using HeatModelMonitor.ViewModels;
using HeatModelMonitor.Services;
using Microsoft.Extensions.Configuration;
using System.IO;

namespace HeatModelMonitor
{
    public partial class App : PrismApplication
    {
        private IConfiguration _configuration;

        protected override Window CreateShell()
        {
            return Container.Resolve<MainWindow>();
        }

        protected override void RegisterTypes(IContainerRegistry containerRegistry)
        {
            // 加载配置
            var builder = new ConfigurationBuilder()
                .SetBasePath(Directory.GetCurrentDirectory())
                .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);
            _configuration = builder.Build();
            containerRegistry.RegisterInstance(_configuration);

            // 注册服务
            containerRegistry.RegisterSingleton<IApiService, ApiService>();

            // 注册ViewModels
            containerRegistry.Register<MainWindowViewModel>();
            containerRegistry.Register<DashboardViewModel>();
            containerRegistry.Register<TasksViewModel>();
            containerRegistry.Register<HistoryViewModel>();
            containerRegistry.Register<AlgorithmsViewModel>();
            containerRegistry.Register<ConfigViewModel>();
            containerRegistry.Register<LogsViewModel>();

            // 注册Views for navigation
            containerRegistry.RegisterForNavigation<DashboardView>();
            containerRegistry.RegisterForNavigation<TasksView>();
            containerRegistry.RegisterForNavigation<HistoryView>();
            containerRegistry.RegisterForNavigation<AlgorithmsView>();
            containerRegistry.RegisterForNavigation<ConfigView>();
            containerRegistry.RegisterForNavigation<LogsView>();
        }

        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);
        }
    }
}
