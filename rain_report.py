
import jwt
import requests
from dingtalk_notify import push_notification_with_args as dingtalk_push
from datetime import datetime, timezone, time
import pytz

def read_config(filename):
    config = {}
    with open(filename, 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config


def generate_jwt_token(file_path):
    # 使用with语句自动管理文件资源
    with open(file_path, 'r', encoding='utf-8') as file:
        private_key = file.read()  # 读取私钥明文到字符串变量

    payload = {
        'iat': int(datetime.now(timezone.utc).timestamp()) - 30,
        'exp': int(datetime.now(timezone.utc).timestamp()) + 900,
        'sub': configlist['hefeng_sub']
    }
    headers = {
        'kid': configlist['hefeng_kid']
    }

    # Generate JWT
    encoded_jwt = jwt.encode(payload, private_key, algorithm='EdDSA', headers=headers)
    return encoded_jwt


def grid_weather_24h(location):
    # 调用和风天气API请求天气
    url = f"https://{configlist['hefen_api_host']}/v7/grid-weather/24h"
    # 定义查询地点
    params = {"location": location}
    headers = {
        "Authorization": f"Bearer {hefeng_jwt_token}",
        "Accept-Encoding": "gzip, deflate, br"  # 对应 --compressed 参数
    }

    response = requests.get(
        url,
        params=params,
        headers=headers
    )

    # 检查响应状态
    if response.status_code == 200:
        print(f"位置 {location} 的天气请求成功！")
    else:
        print(f"位置 {location} 的天气请求失败，状态码: {response.status_code}")
        print("错误信息:", response.text)
    return response.json()


def extract_weather_data_json(json_respond):
    """
    从JSON数据中提取天气数据

    Args:
        json_respond (str): JSON数据

    Returns:
        dict: 以"xx时"为键，包含temp、icon和text的字典
    """

    # 提取hourly数据
    hourly_data = json_respond.get('hourly', [])

    # 创建结果字典
    result_dict = {}

    # 处理每小时的数据
    for item in hourly_data:
        # 获取时间
        fx_time = item.get('fxTime', '')
        # 获取温度、图标和天气描述
        temp = item.get('temp', '')
        icon = item.get('icon', '')
        text = item.get('text', '')

        # 将UTC时间转换为北京时间并格式化为"xx时"
        try:
            # 解析时间字符串
            time_part = fx_time.split('+')[0]
            dt = datetime.fromisoformat(time_part)

            # 转换为北京时间 (UTC+8)
            utc_tz = pytz.utc
            beijing_tz = pytz.timezone('Asia/Shanghai')
            utc_dt = utc_tz.localize(dt)
            beijing_dt = utc_dt.astimezone(beijing_tz)

            # 格式化为"xx时"
            time_key = f"{beijing_dt.hour}时"

            # 存储数据
            result_dict[time_key] = {
                'temp': temp,
                'icon': icon,
                'text': text
            }
        except Exception as e:
            print(f"时间转换错误: {e}")
            continue
    return result_dict


def check_rain_for_locations(location_list):
    """
    检查多个坐标点的降雨情况

    Args:
        location_list: 坐标点列表，值遵从和风天气接口规范，如 ["105.44,28.89", "105.441,28.887"]

    Returns:
        tuple: (上午有雨, 下午有雨) 的布尔值
    """
    morning_rain_anywhere = False
    afternoon_rain_anywhere = False

    for location in location_list:
        try:
            # 获取天气数据
            weather_condition = grid_weather_24h(location)
            weather_dict = extract_weather_data_json(weather_condition)

            # 检查当前坐标点的降雨情况
            morning_rain, afternoon_rain = check_single_location_rain(weather_dict)

            # 更新总体降雨状态（只要有一个地方有雨就为True）
            if morning_rain:
                morning_rain_anywhere = True
                print(f"位置 {location} 上午有雨")

            if afternoon_rain:
                afternoon_rain_anywhere = True
                print(f"位置 {location} 下午有雨")

        except Exception as e:
            print(f"处理位置 {location} 时出错: {e}")
            continue

    return morning_rain_anywhere, afternoon_rain_anywhere


def check_single_location_rain(weather_data):
    """
    检查单个坐标点的降雨情况

    Args:
        weather_data: 天气数据字典

    Returns:
        tuple: (上午有雨, 下午有雨) 的布尔值
    """
    # 检查上午(8点到13点)是否有雨
    morning_hours = ['8时', '9时', '10时', '11时', '12时', '13时']
    morning_rain = False

    for hour in morning_hours:
        if hour in weather_data and 'text' in weather_data[hour]:
            if '雨' in weather_data[hour]['text']:
                morning_rain = True
                break

    # 检查下午(14点到18点)是否有雨
    afternoon_hours = ['14时', '15时', '16时', '17时', '18时']
    afternoon_rain = False

    for hour in afternoon_hours:
        if hour in weather_data and 'text' in weather_data[hour]:
            if '雨' in weather_data[hour]['text']:
                afternoon_rain = True
                break

    return morning_rain, afternoon_rain

if __name__ == '__main__':
    # 读取配置数据
    configlist = read_config('ignore_file\\key.txt')
    hefeng_jwt_token = generate_jwt_token("ignore_file\\ed25519-private.pem")

    # 定义需要监测的坐标列表
    location_list = configlist['location_list'].split('/')

    # 检查所有坐标点的降雨情况
    morning_rain, afternoon_rain = check_rain_for_locations(location_list)

    # 设置北京时区
    beijing_tz = pytz.timezone('Asia/Shanghai')

    # 获取当前北京时间的日期和时间
    now_beijing = datetime.now(beijing_tz)
    current_time = now_beijing.time()

    # 定义时间范围
    start_time_morning = time(6, 0, 0)
    end_time_morning = time(9, 0, 0)
    start_time_afternoon = time(12, 0, 0)
    end_time_afternoon = time(15, 0, 0)

    # 检查时间并完成推送
    if start_time_morning <= current_time < end_time_morning and morning_rain:
        dingtalk_push(msg='上午可能有雨')
    elif start_time_afternoon <= current_time < end_time_afternoon and afternoon_rain:
        dingtalk_push(msg='下午可能有雨')
