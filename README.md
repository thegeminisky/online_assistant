# 通知归集助手

一个用于集中管理各类通知的Python工具，支持邮件监控、钉钉通知等多种通知方式。

## 功能特性

- 📧 **邮件监控** - 自动监控邮箱并处理新邮件
- 🔔 **钉钉通知** - 通过钉钉机器人发送通知消息
- 🌧️ **天气报告** - 生成降雨报告等天气信息
- 🔧 **模块化设计** - 易于扩展新的通知渠道

## 项目结构

```
online_assistant/
├── email_monitor.py      # 邮件监控模块
├── dingtalk_notify.py    # 钉钉通知模块
├── rain_report.py        # 天气报告模块
├── function_base.py      # 基础功能模块
├── .gitignore           # Git忽略配置
├── LICENSE              # GPL-3.0许可证
└── README.md            # 项目说明
```

## 安装依赖

```python
依赖列表未整理
# 其他依赖根据具体功能模块需要安装
```

## 快速开始

### 1. 设置鉴权与配置信息

在项目根目录下新建并在'ignore_file\\key.txt'中填写项目所需密钥
#### 钉钉机器人access_token获取
https://open.dingtalk.com/document/orgapp/obtain-the-webhook-address-of-a-custom-robot
#### 钉钉机器人secret获取
https://open.dingtalk.com/document/robots/customize-robot-security-settings
#### 和风天气api_host
https://dev.qweather.com/docs/configuration/api-host/
#### 和风天气kid和sub参见和风天气JWT认证部分
https://dev.qweather.com/docs/configuration/authentication/

```python
# 钉钉自定义机器人API
dingtalk_access_token = <xxxxxxxxxxxxxxxxxx>
dingtalk_secret = <SECxxxxxxxxxxxxxxxxxxxxxx>
# 和风天气API
hefen_api_host = <xxxx.xxxx.xxxx.xxxx>
hefeng_kid = <xxxxxxxxxx>
hefeng_sub = <xxxxxxxxxx>
# 天气监测点坐标经纬度，经度在前纬度在后，英文逗号分隔，十进制格式，北纬东经为正，南纬西经为负，坐标间以“/”分割
location_list = 116.40,39.90/121.47,31.23
# 邮箱IMAP信息
mail_password = <IMAP密钥>
mail_username = <邮箱账号>
mail_url = <IMAP服务器>
```

### 2. 将依照和风天气JWT身份认证生成的ed25519-private.pem文件放到ignore_file目录下
## 使用示例

### 发送钉钉通知

### 监控邮件并转发

## 许可证

本项目采用 GPL-3.0 开源许可证。详情请查看 LICENSE 文件。

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 联系方式

- 项目主页：https://github.com/thegeminisky/online_assistant
- 问题反馈：请通过GitHub Issues提交

---

*让通知管理变得更简单高效！*
