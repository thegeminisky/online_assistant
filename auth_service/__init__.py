"""
auth_service 包

该包提供应用程序的密钥管理和服务鉴权功能。

主要包含：
- SecretsManager: 密钥管理类，用于加载和访问密钥
- 鉴权装饰器: 用于服务函数的密钥注入和权限验证
- 辅助函数: 提供密钥相关的实用功能

使用示例:
>>> from auth_service import SecretsManager, require_secrets
>>>
>>> # 加载密钥
>>> SecretsManager.load_secrets()
>>>
>>> # 使用装饰器
>>> @require_secrets("my_service", "api_key", "api_secret")
>>> def my_function(api_key, api_secret):
>>>     # 业务逻辑
>>>     pass
"""

# 导入包的核心功能
from .secrets_manager import SecretsManager
from .auth_decorator import (
    require_secret,
    require_secret_with_context
)

# 定义包的公共API
__all__ = [
    'SecretsManager',
    'require_secret',
    'require_secret_with_context'
]

# 包初始化代码
def _initialize():
    """包的初始化函数，在第一次导入时执行"""
    # 可以在这里添加初始化逻辑，例如：
    # - 设置默认配置
    # - 验证环境变量
    # - 预加载常用资源
    pass

# 执行初始化
_initialize()

# 包版本信息
__version__ = "1.0.0"
__author__ = "Your Name <your.email@example.com>"
__license__ = "MIT"