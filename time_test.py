import re
import subprocess
import time
from typing import Dict, Optional


def is_device_connected() -> bool:
    """
    检查是否有设备连接
    :return: 如果有设备连接返回True,否则返回False
    """
    output = subprocess.check_output(['adb', 'devices']).decode('utf-8')
    devices = re.findall(r'(\w+)\s+device\b', output)
    return len(devices) == 1


def push_aapt() -> None:
    """
    将aapt-arm-pie推送到设备的/data/local/tmp目录下
    """
    aapt_path = 'aapt-arm-pie'  # 假设aapt-arm-pie与该脚本在同一目录下
    remote_path = '/data/local/tmp/aapt-arm-pie'
    subprocess.run(['adb', 'push', aapt_path, remote_path], creationflags=subprocess.CREATE_NO_WINDOW)
    subprocess.run(['adb', 'shell', 'chmod', '+x', remote_path], creationflags=subprocess.CREATE_NO_WINDOW)


def get_apk_path(package_name: str) -> Optional[str]:
    """
    获取指定包名的APK文件路径
    :param package_name: 应用包名
    :return: APK文件路径,如果未找到返回None
    """
    output = subprocess.check_output(['adb', 'shell', 'pm', 'path', package_name]).decode('utf-8').split('\r')[0]
    match = re.search(r'package:(.+)', output)
    if match:
        return match.group(1)
    else:
        return None


def get_launch_activity(apk_path: str) -> Optional[str]:
    """
    获取应用的启动Activity
    :param apk_path: APK文件路径
    :return: 启动Activity,如果未找到返回None
    """
    remote_aapt = '/data/local/tmp/aapt-arm-pie'
    process = subprocess.Popen(['adb', 'shell', remote_aapt, 'd', 'badging', apk_path],
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    output, _ = process.communicate()
    output = output.decode('utf-8')
    match = re.search(r'launchable-activity: name=\'(.+?)\'', output)
    if match:
        return match.group(1)
    else:
        return None


def test_launch_time(package_name: str, launch_activity: str, stop_before_launch: bool = False,
                     stop_after_launch: bool = False) -> Optional[Dict[str, str]]:
    """
    测试应用启动时间
    :param package_name: 应用包名
    :param launch_activity: 启动Activity
    :param stop_before_launch: 是否在启动前结束应用
    :param stop_after_launch: 是否在启动后结束应用
    :return: 包含启动时间信息的字典,如果启动失败返回None
    """
    if stop_before_launch:
        subprocess.run(['adb', 'shell', 'am', 'force-stop', package_name])

    start_time = time.time()
    process = subprocess.Popen(['adb', 'shell', 'am', 'start', '-W', '-n', f'{package_name}/{launch_activity}'],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, _ = process.communicate()
    output = output.decode('utf-8')

    cpu_usage_threshold = 10
    while True:
        top_output = subprocess.check_output(['adb', 'shell', 'top', '-n', '1', '-b']).decode('utf-8')
        match = re.search(
            r'\d+(?:\.\d+)?%s*\d+[\s|]+[A-Za-z]+\s+\d+\s+\d+[\s|]+\d+[\s|]+\d+[\s|]+[A-Za-z]+\s+[A-Za-z]+\s+[A-Za-z]+\s+[A-Za-z]+\s+[^\n]*' + re.escape(
                package_name), top_output)
        if match:
            cpu_usage = float(match.group().split('%')[0])
            if cpu_usage < cpu_usage_threshold:
                break
        else:
            # 如果找不到应用的CPU占用信息,则假定应用已经启动完成
            break
        time.sleep(0.1)

    end_time = time.time()
    launch_time = end_time - start_time

    if stop_after_launch:
        subprocess.run(['adb', 'shell', 'am', 'force-stop', package_name])

    result = {}
    for line in output.split('\n'):
        if line.startswith('LaunchState:'):
            result['LaunchState'] = line.split(':')[1].strip()
        elif line.startswith('TotalTime:'):
            result['TotalTime'] = line.split(':')[1].strip()
        elif line.startswith('WaitTime:'):
            result['WaitTime'] = line.split(':')[1].strip()
    result['CompleteLaunchTime'] = f'{launch_time:.2f}'

    if 'TotalTime' not in result:
        return None

    return result


def get_launch_info(package_name: str, stop_before_launch: bool = False, stop_after_launch: bool = False) -> Optional[
    Dict[str, str]]:
    """
    获取应用启动信息
    :param package_name: 应用包名
    :param stop_before_launch: 是否在启动前结束应用
    :param stop_after_launch: 是否在启动后结束应用
    :return: 包含启动时间信息的字典,如果获取失败返回None
    """
    if not is_device_connected():
        return None

    push_aapt()
    apk_path = get_apk_path(package_name)
    if apk_path is None:
        print('未找到应用的APK文件路径')
        return None

    launch_activity = get_launch_activity(apk_path)
    if launch_activity is None:
        print('未找到应用的启动Activity')
        return None

    launch_info = test_launch_time(package_name, launch_activity, stop_before_launch, stop_after_launch)
    return launch_info
