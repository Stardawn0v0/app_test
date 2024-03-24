import time
from typing import List
from time_test import get_launch_info


def input_package_names() -> List[str]:
    """
    从用户输入中获取包名列表。
    用户可以连续输入包名，每输入一个包名后按回车键确认。
    当用户不输入任何内容直接按回车键时，结束输入。
    :return: 包含用户输入的所有包名的列表。
    """
    package_names = []
    print("请输入应用包名，输入完成后直接回车结束：")
    while True:
        package_name = input().strip()
        if not package_name:
            break
        package_names.append(package_name)
    return package_names


def main():
    package_names = input_package_names()
    total_complete_launch_time = 0.0

    for package_name in package_names:
        print(f"\n正在测试应用 {package_name} 的启动时间...")
        launch_info = get_launch_info(package_name)
        if launch_info is not None:
            print(f'启动类型: {launch_info["LaunchState"]}')
            print(f'应用拉起用时: {launch_info["TotalTime"]} ms')
            print(f'应用加载用时: {launch_info["WaitTime"]} ms')
            print(f'完全启动时间: {launch_info["CompleteLaunchTime"]} 秒')
            total_complete_launch_time += float(launch_info["CompleteLaunchTime"])
        else:
            print('应用启动失败')
        time.sleep(1)  # 每个应用测试完毕后等待1秒

    print(f"\n所有应用总完全启动时间: {total_complete_launch_time:.2f} 秒")


if __name__ == "__main__":
    main()
