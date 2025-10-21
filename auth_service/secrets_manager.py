
'''
项目结构：
project/
├── ignore_file/
│   └── key.tet          # 密钥文件
├── auth_service/
│   ├── __init__.py
│   ├── secrets_manager.py  # 密钥管理核心
│   └── .py   # 鉴权装饰器
├── services/
│   ├── __init__.py
│   ├── service_a.py        # 服务A
│   └── service_b.py        # 服务B
└── main.py                 # 主程序

6. 密钥文件示例 (ignore_file/key.tet)

服务A的API密钥

service_a.api_key = a1b2c3d4e5f6g7h8i9j0

服务B的访问令牌

service_b.access_token = token_1234567890abcdef

服务B的加密密钥

service_b.encryption_key = enc_key_0987654321

全局管理员令牌

admin_token = admin_secure_token_xyz

数据库密码

db.password = P@ssw0rd!123
'''

import chardet
import os
import re
from collections import defaultdict
from functools import lru_cache

class SecretsManager:
    """管理应用程序密钥的加载和访问。

    该类负责从指定文件中加载密钥，并提供安全的访问接口。
    密钥文件格式应为每行一个密钥，格式为"密钥名 = 密钥值"。

    属性:
        _secrets: 存储所有加载的密钥，格式为字典的字典。
        DEFAULT_FILE_PATH: 默认密钥文件路径。
    """

    _secrets = None
    DEFAULT_FILE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'ignore_file',
        'key.txt'
    )



    @classmethod
    @lru_cache(maxsize=1)
    def load_secrets(cls, file_path=None):
        """加载并缓存密钥文件。

        该方法会解析密钥文件，并将结果存储在类变量中。使用LRU缓存确保
        文件只被读取一次，后续调用直接返回缓存结果。

        Args:
            file_path: 可选，指定密钥文件路径。如果未提供，则使用默认路径。

        Returns:
            dict: 包含所有密钥的嵌套字典，格式为 {服务名: {密钥名: 密钥值}}

        Raises:
            FileNotFoundError: 如果指定的密钥文件不存在。
            ValueError: 如果密钥文件中有格式错误的行。
            RuntimeError: 如果加载过程中发生其他错误。
        """
        file_path = file_path or cls.DEFAULT_FILE_PATH

        if cls._secrets is None:
            cls._secrets = defaultdict(dict)
            try:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"密钥文件不存在: {file_path}")

                # 自动检测文件编码
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                    encoding_result = chardet.detect(raw_data)
                    file_encoding = encoding_result['encoding'] or 'utf-8'

                    # 如果检测到的编码置信度较低，尝试使用utf-8和gbk
                    if encoding_result['confidence'] < 0.7:
                        try:
                            content = raw_data.decode('utf-8')
                        except UnicodeDecodeError:
                            try:
                                content = raw_data.decode('gbk')
                            except UnicodeDecodeError:
                                content = raw_data.decode(file_encoding, errors='replace')
                    else:
                        content = raw_data.decode(file_encoding)

                # 按行处理文件内容
                for line_num, line in enumerate(content.splitlines(), 1):
                    line = line.strip()
                    # 跳过空行和注释
                    if not line or line.startswith('#'):
                        continue

                    # 解析 "密钥名 = 密钥值" 格式
                    match = re.match(r'^([\w\.\-]+)\s*=\s*(.+)$', line)
                    if not match:
                        raise ValueError(
                            f"第 {line_num} 行格式错误: '{line}'。"
                            "应为 '密钥名 = 密钥值' 格式"
                        )

                    key_name = match.group(1)
                    key_value = match.group(2).strip()

                    # 处理带命名空间的密钥 (service.key)
                    if '.' in key_name:
                        service, key = key_name.split('.', 1)
                        cls._secrets[service][key] = key_value
                    else:
                        # 全局密钥
                        cls._secrets['global'][key_name] = key_value

                print(f"成功加载密钥文件: {file_path} (编码: {file_encoding})")
                print(f"发现 {len(cls._secrets)} 个服务密钥组")

            except Exception as e:
                cls._secrets = None
                raise RuntimeError(f"加载密钥失败: {str(e)}")

        return cls._secrets

    @classmethod
    def get_secret(cls, service_name, key_name):
        """获取特定服务的密钥。

        首先尝试获取服务特定的密钥，如果未找到则尝试获取全局密钥。

        Args:
            service_name: 服务名称，对应密钥文件中的服务前缀。
            key_name: 密钥名称。

        Returns:
            str: 请求的密钥值。

        Raises:
            KeyError: 如果指定的服务或密钥不存在。
        """
        secrets = cls.load_secrets()

        # 首先尝试服务特定密钥
        if service_name in secrets and key_name in secrets[service_name]:
            return secrets[service_name][key_name]

        # 尝试全局密钥
        if 'global' in secrets and key_name in secrets['global']:
            return secrets['global'][key_name]

        # 密钥未找到
        available_services = ", ".join(secrets.keys())
        available_keys = ", ".join(
            list(secrets.get(service_name, {}).keys()) +
            list(secrets.get('global', {}).keys())
        )

        raise KeyError(
            f"服务 '{service_name}' 的密钥 '{key_name}' 未找到。\n"
            f"可用服务: {available_services}\n"
            f"可用密钥: {available_keys}"
        )

    @classmethod
    def list_secrets(cls):
        """列出所有加载的密钥（用于调试）。

        返回格式化的字符串，显示所有服务、密钥及其部分值。

        Returns:
            str: 格式化字符串，包含所有密钥信息。
        """
        secrets = cls.load_secrets()
        result = []
        for service, keys in secrets.items():
            for key, value in keys.items():
                result.append(f"{service}.{key} = {value[:3]}...")
        return "\n".join(result)


