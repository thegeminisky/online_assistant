"""
services 包

该包提供三个主要功能模块：
- dingtalk_notify: 钉钉机器人通知模块
- email_monitor: 邮件监控与解析模块
- rain_report: 天气预报与自动推送模块
"""

from .dingtalk_notify import dingtalk_notify

from .rain_report import rain_report

__all__ = [
    "dingtalk_notify",
    "rain_report",
]
