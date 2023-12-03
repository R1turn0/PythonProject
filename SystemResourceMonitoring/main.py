# -*- coding: UTF-8 -*-
# !/usr/bin/python

import psutil
import datetime

# import msvcrt
import os
import time


def catch_sys_info():
    global sys_log, now_time
    # 获取系统信息
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cpu_per = psutil.cpu_percent(interval=0.5)  # 获取cpu刷新率，刷新时间0.5s
    mermory_info = psutil.virtual_memory()  # 获取内存使用情况（包括总、可用、使用率...）
    disk_info = psutil.disk_usage("/")  # 获取根目录磁盘使用情况
    net_info = psutil.net_io_counters()  # 获取网络状态

    sys_log = "当前时间：%s \n" % (now_time)
    sys_log += "|---------------|---------------|---------------|----------------|\n"
    sys_log += "|     CPU       |      内存      |       硬盘     |      网络      |\n"
    sys_log += "|---------------|---------------|---------------|----------------|\n"
    sys_log += "|    使用率：%d   |   使用率：%d    |    使用率：%d  |   收：%dMB     |\n" \
               % (cpu_per, mermory_info.percent, disk_info.percent, net_info.bytes_recv / 1024 ** 2)
    sys_log += "|---------------|---------------|---------------|----------------|\n"
    sys_log += "|    核心数：%d   |   总量：%.2f  G |   总量:%.2fG  |   发：%dMB     |\n" \
               % (psutil.cpu_count(logical=False), mermory_info.total / 1024 ** 3, disk_info.total / 1024 ** 3,
                  net_info.bytes_sent / 1024 ** 2)
    sys_log += "|---------------|---------------|---------------|----------------|\n"


def save_sys_info():
    log_txt = open("./log_test.txt", "a")
    log_txt.write(sys_log + "\n\n")
    log_txt.close()


"""
关于"__name__"
1) 在本文件调用（不管在那个函数、那个位置），__name__ = "__main__"
2) 当本文件被import时，文件名.__name__ = "文件名"
"""


def main():
    time.sleep(1)
    try:
        # 程序入口
        i = 0
        while True:
            i += 1
            os.system("clear")
            print("监控脚本正在运行，\"ctrl+C\"停止运行脚本！")
            catch_sys_info()
            print(sys_log)
            if i == 2:  # 2为测试次数，每24小时保存一次日志，每次刷新为5s，刷新43200次为24小时
                save_sys_info()
                print("%s 日志已保存!" % now_time)
                i = 0
            time.sleep(5)
    except KeyboardInterrupt:
        os.system("clear")
        print("监控脚本已正常退出!")


if __name__ == "__main__":
    main()
