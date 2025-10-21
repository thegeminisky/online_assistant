from function_plugin import dingtalk_notify, email_monitor, rain_report
from auth_service import SecretsManager
import threading
import time
import traceback

def run_service(service_instance, method_name, *args):
    """安全运行服务方法。"""
    method = getattr(service_instance, method_name)
    try:
        start_time = time.time()
        result = method(*args)
        elapsed = time.time() - start_time
        print(f"服务执行成功 | 方法: {method_name} | 耗时: {elapsed:.4f}s | 结果: {result}")
        return True
    except Exception as e:
        print(f"服务执行失败: {str(e)}")
        print("完整堆栈跟踪:")
        traceback.print_exc()
        return False


def run_single_service(service_instance, method_name, *args):
    print(f"正在启动服务: {method_name}")
    run_service(service_instance, method_name, *args)
    print(f"服务 {method_name} 执行完毕")


def run_all_services():

    # 任务列表
    tasks = [
        (dingtalk_notify_service, "push_notification_with_args", ["测试消息"]),
        (email_monitor_service, "email_service", ['占位']),
        (rain_report_service, "rain_or_not", ['占位'])
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
        time.sleep(0.1)

    for t in threads:
        t.join()

    print("所有服务执行完毕")

if __name__ == "__main__":
    SecretsManager.load_secrets()
    print("============= 加载的密钥 =============")
    print(SecretsManager.list_secrets())
    print("====================================")

    # 创建服务实例
    dingtalk_notify_service = dingtalk_notify()
    rain_report_service = rain_report()
    email_monitor_service = email_monitor()

    # 启动服务
    run_all_services()
    #run_single_service(email_monitor_service, "email_service", '占位')



