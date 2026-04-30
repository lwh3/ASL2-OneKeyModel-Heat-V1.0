# LF精炼炉加热模型监控系统 - WPF Desktop Application

基于 .NET 10 + WPF + Prism MVVM + Material Design 构建的Windows桌面监控应用。

## 技术栈

- **.NET 10** - 最新的.NET框架
- **WPF (Windows Presentation Foundation)** - Windows桌面UI框架
- **Prism 9** - MVVM框架和依赖注入
- **DryIoc** - 轻量级IoC容器
- **Material Design In XAML** - 现代化Material Design UI组件
- **LiveChartsCore** - 数据可视化图表库
- **RestSharp** - RESTful API客户端
- **Newtonsoft.Json** - JSON序列化/反序列化

## 功能特性

### 核心功能
- 📊 **实时仪表盘** - 展示系统运行状态和统计数据
- 📝 **任务管理** - 查看和管理加热任务列表
- 📈 **历史数据分析** - 查询和分析历史加热数据
- ⚙️ **算法配置** - 查看和管理计算算法
- 🔧 **系统配置** - 动态配置系统参数
- 📋 **日志查看** - 实时查看系统日志

### 技术特性
- 🎨 **Material Design UI** - 现代化的界面设计
- 🏗️ **MVVM架构** - 清晰的代码结构和职责分离
- 💉 **依赖注入** - Prism + DryIoc容器管理
- 🔄 **自动刷新** - 定时自动更新数据
- 🖥️ **原生性能** - Windows原生应用性能
- 📦 **单文件部署** - 可打包为单个可执行文件

## 环境要求

- Windows 10 或更高版本
- .NET 10 Runtime (或 SDK用于开发)
- Visual Studio 2022 或 Rider (用于开发)

## 快速开始

### 开发环境

1. **安装 .NET 10 SDK**

   从 https://dotnet.microsoft.com/download 下载并安装

2. **克隆代码**
   ```bash
   cd Frontend-WPF
   ```

3. **配置API端点**

   编辑 `HeatModelMonitor/appsettings.json`:
   ```json
   {
     "ApiSettings": {
       "BaseUrl": "http://localhost:5000/api",
       "Timeout": 30
     }
   }
   ```

4. **还原依赖**
   ```bash
   dotnet restore HeatModelMonitor/HeatModelMonitor.csproj
   ```

5. **运行应用**
   ```bash
   dotnet run --project HeatModelMonitor/HeatModelMonitor.csproj
   ```

   或在Visual Studio中打开解决方案并按F5运行。

### 生产部署

#### 方式1：发布自包含应用

```bash
cd HeatModelMonitor
dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true
```

生成的可执行文件位于: `bin/Release/net10.0-windows/win-x64/publish/HeatModelMonitor.exe`

将整个 `publish` 文件夹分发给用户，双击 `HeatModelMonitor.exe` 即可运行。

#### 方式2：框架依赖部署

```bash
dotnet publish -c Release -r win-x64 --self-contained false
```

用户需要预先安装.NET 10 Runtime。

#### 方式3：创建安装程序 (推荐生产环境)

使用 WiX Toolset 创建MSI安装程序：

1. 安装 WiX Toolset: https://wixtoolset.org/
2. 创建WiX安装项目
3. 构建安装程序

或使用 Inno Setup 创建安装向导。

## 项目结构

```
Frontend-WPF/
└── HeatModelMonitor/
    ├── Models/              # 数据模型
    │   └── Models.cs       # 所有数据模型定义
    ├── Services/            # 服务层
    │   ├── IApiService.cs  # API服务接口
    │   └── ApiService.cs   # API服务实现
    ├── ViewModels/          # 视图模型
    │   ├── MainWindowViewModel.cs
    │   ├── DashboardViewModel.cs
    │   ├── TasksViewModel.cs
    │   ├── HistoryViewModel.cs
    │   ├── AlgorithmsViewModel.cs
    │   ├── ConfigViewModel.cs
    │   └── LogsViewModel.cs
    ├── Views/               # 视图(XAML)
    │   ├── MainWindow.xaml
    │   ├── DashboardView.xaml
    │   ├── TasksView.xaml
    │   ├── HistoryView.xaml
    │   ├── AlgorithmsView.xaml
    │   ├── ConfigView.xaml
    │   └── LogsView.xaml
    ├── Converters/          # 值转换器
    ├── Behaviors/           # 行为
    ├── Properties/          # 程序集属性
    ├── App.xaml             # 应用程序定义
    ├── App.xaml.cs          # 应用程序启动逻辑
    ├── appsettings.json     # 配置文件
    └── HeatModelMonitor.csproj  # 项目文件
```

## MVVM架构说明

### 视图(View)
XAML文件定义UI结构和布局，使用Data Binding绑定到ViewModel。

### 视图模型(ViewModel)
处理UI逻辑和数据，继承自`BindableBase`实现属性通知。

### 模型(Model)
纯数据类，表示业务实体。

### 服务(Service)
封装API调用和业务逻辑，通过依赖注入提供给ViewModel。

### 依赖注入
在`App.xaml.cs`的`RegisterTypes`方法中注册服务和视图模型：

```csharp
protected override void RegisterTypes(IContainerRegistry containerRegistry)
{
    // 注册服务
    containerRegistry.RegisterSingleton<IApiService, ApiService>();

    // 注册ViewModels
    containerRegistry.Register<MainWindowViewModel>();
    containerRegistry.Register<DashboardViewModel>();

    // 注册Views用于导航
    containerRegistry.RegisterForNavigation<DashboardView>();
}
```

## 配置说明

### appsettings.json

```json
{
  "ApiSettings": {
    "BaseUrl": "http://localhost:5000/api",  // API基础URL
    "Timeout": 30                             // 请求超时时间(秒)
  },
  "AppSettings": {
    "RefreshInterval": 10,  // 自动刷新间隔(秒)
    "LogLines": 100         // 日志显示行数
  }
}
```

### 运行时配置
可以在程序运行时通过配置界面修改部分设置。

## 开发指南

### 添加新视图

1. **创建视图模型**
   ```csharp
   public class NewViewModel : BindableBase
   {
       public NewViewModel()
       {
           // 初始化
       }
   }
   ```

2. **创建视图(XAML)**
   ```xml
   <UserControl x:Class="HeatModelMonitor.Views.NewView"
                xmlns:prism="http://prismlibrary.com/"
                prism:ViewModelLocator.AutoWireViewModel="True">
       <!-- UI内容 -->
   </UserControl>
   ```

3. **注册视图**
   在`App.xaml.cs`中:
   ```csharp
   containerRegistry.Register<NewViewModel>();
   containerRegistry.RegisterForNavigation<NewView>();
   ```

4. **添加到菜单**
   在`MainWindowViewModel.cs`中添加菜单项:
   ```csharp
   MenuItems = new ObservableCollection<MenuItem>
   {
       new MenuItem { Title = "新视图", Icon = "NewIcon", NavigationPath = "NewView" }
   };
   ```

### 调用API

在ViewModel中注入`IApiService`:

```csharp
private readonly IApiService _apiService;

public MyViewModel(IApiService apiService)
{
    _apiService = apiService;
}

private async Task LoadDataAsync()
{
    try
    {
        var data = await _apiService.GetStatusAsync();
        // 处理数据
    }
    catch (Exception ex)
    {
        // 错误处理
    }
}
```

### 数据绑定

在XAML中绑定到ViewModel属性:

```xml
<TextBlock Text="{Binding MyProperty}"/>
<Button Content="点击" Command="{Binding MyCommand}"/>
```

在ViewModel中:

```csharp
private string _myProperty;
public string MyProperty
{
    get => _myProperty;
    set => SetProperty(ref _myProperty, value);
}

public ICommand MyCommand { get; }

public MyViewModel()
{
    MyCommand = new DelegateCommand(OnMyCommandExecute);
}

private void OnMyCommandExecute()
{
    // 命令逻辑
}
```

## 构建优化

### 减小发布体积

1. **启用裁剪**
   ```xml
   <PropertyGroup>
       <PublishTrimmed>true</PublishTrimmed>
   </PropertyGroup>
   ```

2. **压缩**
   ```xml
   <PropertyGroup>
       <EnableCompressionInSingleFile>true</EnableCompressionInSingleFile>
   </PropertyGroup>
   ```

### 性能优化

1. **使用异步操作** - 所有API调用使用async/await
2. **虚拟化列表** - 大数据列表使用VirtualizingStackPanel
3. **避免UI线程阻塞** - 耗时操作放到后台线程
4. **及时释放资源** - 实现IDisposable接口

## 常见问题

### Q: 无法连接到API服务器？
A: 检查`appsettings.json`中的`BaseUrl`配置，确保后端服务正在运行。

### Q: Material Design图标不显示？
A: 确保已正确安装MaterialDesignThemes.Wpf NuGet包。

### Q: 发布后无法运行？
A: 确保目标机器安装了.NET 10 Runtime，或使用自包含发布模式。

### Q: API调用超时？
A: 增加`appsettings.json`中的`Timeout`值，或检查网络连接。

### Q: 如何调试XAML绑定错误？
A: 在Visual Studio的输出窗口查看绑定错误信息，或使用Snoop工具。

## 系统要求

### 开发环境
- Windows 10/11
- Visual Studio 2022 (17.8+) 或 Rider 2023.3+
- .NET 10 SDK

### 运行环境
- Windows 10 (1809+) 或 Windows 11
- .NET 10 Runtime (自包含部署则不需要)
- 最小分辨率: 1280x720

## License

MIT
