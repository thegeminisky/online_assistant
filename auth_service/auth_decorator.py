
from .secrets_manager import SecretsManager


def require_secret(service_name, key_name):
    """服务鉴权装饰器 - 自动注入所需密钥。

    此装饰器会在函数执行前获取指定服务的密钥，并将其作为secret参数注入。

    Args:
        service_name: 服务名称。
        key_name: 密钥名称。

    Returns:
        function: 装饰后的函数。
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # 获取所需密钥
            secret = SecretsManager.get_secret(service_name, key_name)

            # 将密钥注入到函数参数中
            return func(*args, secret=secret, **kwargs)

        return wrapper

    return decorator


def require_secret_with_context(service_name, key_name):
    """服务鉴权装饰器 - 提供更多上下文信息。

    此装饰器会在函数执行前获取指定服务的密钥，并将其作为secret参数注入。
    如果密钥获取失败，会提供更详细的错误信息。

    Args:
        service_name: 服务名称。
        key_name: 密钥名称。

    Returns:
        function: 装饰后的函数。
    """

    def decorator(func):
        def wrapper(args, *kwargs):
            try:
                secret = SecretsManager.get_secret(service_name, key_name)
                return func(args, secret=secret, *kwargs)
            except KeyError as e:
                # 提供更详细的错误信息
                error_msg = (
                    f"服务 '{service_name}' 执行 '{func.__name__}' 失败: \n"
                    f"原因: {str(e)}"
                )
                raise PermissionError(error_msg) from e

        return wrapper

    return decorator
