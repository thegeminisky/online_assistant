# 服务自动化系统 - 集成工具箱

这是一个集成钉钉通知、邮箱监控和天气预报服务的自动化系统，使用Python实现。

## 目录结构

```text
D:.
│  .gitignore         # Git忽略配置文件
│  LICENSE            # 项目许可证
│  main_temp.py       # 主程序入口
│
├─auth_service       # 认证服务模块
│  │  auth_decorator.py # 服务鉴权装饰器
│  │  secrets_manager.py # 密钥管理器
│  │  __init__.py     # 模块初始化
│
├─function_plugin    # 功能插件模块
│  │  dingtalk_notify.py # 钉钉通知功能
│  │  email_monitor.py   # 邮箱监控功能
│  │  rain_report.py      # 天气预报功能
│  │  __init__.py        # 模块初始化
└─ignore_file
        ed25519-private.pem
        key.txt
```

## 功能模块说明

### 1. 认证服务 (`auth_service`)

#### `auth_decorator.py`
提供两个鉴权装饰器：
- `require_secret`: 自动注入所需服务密钥
- `require_secret_with_context`: 提供更详细的错误上下文

#### `secrets_manager.py`
密钥管理核心：
- 从指定文件加载和管理密钥
- 支持服务名.密钥名的命名空间结构
- 提供`get_secret`方法获取相关密钥

### 2. 功能插件 (`function_plugin`)

#### `dingtalk_notify.py` - 钉钉通知功能
- 发送自定义机器人群消息
- 支持@指定用户/手机号码
- 使用HMAC-SHA256签名机制保障安全
- 提供命令行参数和函数调用两种方式

#### `email_monitor.py` - 邮箱监控功能
- 连接IMAP邮件服务器并登录认证
- 扫描并处理未读邮件
- 解析邮件主题、发件人和正文内容
- 支持附件保存功能
- 可设置文件夹和搜索条件

#### `rain_report.py` - 天气预报功能
- 获取和风天气API的24小时预报
- 使用EdDSA算法生成JWT令牌认证
- 检测多个位置在不同时段的降雨情况
- 自动生成降雨提醒
- 含时区处理功能（UTC转北京时间）

### 3. 主程序 (`main_temp.py`)
- 加载并管理所有服务实例
- 多线程并行执行服务
- 提供错误处理和日志记录
- 支持单个服务或批量执行模式

## 安装与使用指南

### 环境要求
- Python 3.7+
- 依赖库：
  ```bash
  pip install requests pyjwt pytz chardet
  ```

### 配置步骤
1. **准备密钥文件**
   - 创建路径：`ignore_file/key.txt`
   - 添加服务密钥（格式如下）：
     ```
     # 钉钉通知配置
     dingtalk_notify.access_token = your_dingtalk_token
     dingtalk_notify.secret = your_dingtalk_secret
   
     # 邮箱监控配置
     email_monitor.username = <邮箱账号>
     email_monitor.password = <IMAP密钥>
     email_monitor.url = <IMAP服务器>
   
     # 天气预报配置
     rain_report.kid = your_kid_value
     rain_report.sub = your_sub_value
     rain_report.api_host = api.qweather.com
     # 天气监测点坐标经纬度，经度在前纬度在后，英文逗号分隔，十进制格式，北纬东经为正，南纬西经为负，坐标间以“/”分割
     rain_report.location_list = 105.44,28.89/106.45,29.90
     ```
   - 将依照和风天气JWT身份认证生成的ed25519-private.pem文件放到ignore_file目录下
   - 在项目根目录下新建并在'ignore_file\\key.txt'中填写项目所需密钥
   - 钉钉机器人access_token获取
   - https://open.dingtalk.com/document/orgapp/obtain-the-webhook-address-of-a-custom-robot
   - 钉钉机器人secret获取
   - https://open.dingtalk.com/document/robots/customize-robot-security-settings
   - 和风天气api_host
   - https://dev.qweather.com/docs/configuration/api-host/
   - 和风天气kid和sub参见和风天气JWT认证部分
   - https://dev.qweather.com/docs/configuration/authentication/

2. **执行主程序**
   ```bash
   python main_temp.py
   ```

### 功能示意图
```
 +-------------------+
 |  Secrets Manager  |
 | (密钥集中管理)     |
 +--------+----------+
          |
          | 提供认证凭证
          |
 +--------v---------+     +------------------+
 |  钉钉通知服务      +-----> 钉钉消息推送API   |
 | (dingtalk_notify)|     +------------------+
 +------------------+
          |
          | 降雨通知
          |
 +--------v---------+     +-------------------+
 |  天气预报服务      +-----> 和风天气API        |
 | (rain_report)    |     +-------------------+
 +------------------+
          |
          | 监控提醒
          |
 +--------v---------+     +--------------------+
 |  邮箱监控服务      +-----> IMAP邮件服务器      |
 | (email_monitor)  |     +--------------------+
 +------------------+
```

## 命令行使用示例

### 单独运行钉钉通知
```python
from function_plugin import dingtalk_notify

# 创建钉钉通知实例
dn = dingtalk_notify()

# 推送通知
dn.push_notification_with_args(
    msg="测试消息",
    at_mobiles="13800138000,13900139000",
    at_userids="user123,user456",
    is_at_all=False
)
```

### 单独运行邮箱监控
```python
from function_plugin import email_monitor

# 创建邮箱监控实例
em = email_monitor()
em.email_service('参数占位')
```

### 单独运行天气预报
```python
from function_plugin import rain_report

# 创建天气预报实例
rr = rain_report()
rr.rain_or_not('参数占位')
```

## 安全建议
1. **保护密钥文件**
   - 确保密钥文件存储在安全位置
   - `ignore_file`目录名已经指定在.gitignore中
   - 生产环境建议使用安全的密钥存储服务

2. **权限控制**
   - 使用最小权限原则设置服务账户
   - 定期轮换API令牌和密码

3. **日志安全**
   - 避免在日志中记录敏感信息
   - 保护日志文件的访问权限

## 许可证
本项目采用 **GPL-3.0 许可证** - 详细信息请参阅LICENSE文件。


## 贡献指南
欢迎通过Issues提交问题反馈，或通过Pull Request贡献代码：
1. Fork项目仓库

---

如有任何使用问题，请创建Issue或联系项目维护者。