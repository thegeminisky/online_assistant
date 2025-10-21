
from services.dingtalk_notify import dingtalk_notify
from services.rain_report import rain_report
from auth_service.secrets_manager import SecretsManager
import threading
import time


def run_service(service_instance, method_name, *args):
    """安全运行服务方法。

    此函数封装服务方法的执行，提供错误处理和性能监控。

    Args:
        service_instance: 服务类的实例。
        method_name: 要调用的方法名称。
        *args: 传递给方法的参数。

    Returns:
        bool: 如果执行成功返回True，否则返回False。
    """
    method = getattr(service_instance, method_name)
    try:
        start_time = time.time()
        result = method(*args)
        elapsed = time.time() - start_time
        print(f"服务执行成功 | 方法: {method_name} | 耗时: {elapsed:.4f}s | 结果: {result}")
        return True
    except Exception as e:
        print(f"服务执行失败: {str(e)}")
        return False


if __name__ == "__main__":
    """主程序入口。

    初始化密钥管理器，创建服务实例，并并行执行多个服务任务。
    """
    # 预加载密钥并显示（调试用）
    SecretsManager.load_secrets()
    print("= 加载的密钥 =")
    print(SecretsManager.list_secrets())
    print("=")

    # 创建服务实例
    dingtalk_notify = dingtalk_notify()
    rain_report = rain_report()

    # 服务任务列表
    tasks = [
        (dingtalk_notify, "push_notification_with_args", ["测试消息"]),
        (rain_report, "rain_or_not", ['占位'])
    ]

    # 启动服务线程
    threads = []
    for i, (instance, method, args) in enumerate(tasks):
        t = threading.Thread(
            target=run_service,
            args=(instance, method, *args),
            name=f"ServiceThread-{i + 1}"
        )
        t.start()
        threads.append(t)
        time.sleep(0.1)  # 错开启动时间

    # 等待所有服务完成
    for t in threads:
        t.join()

    print("所有服务执行完毕")

