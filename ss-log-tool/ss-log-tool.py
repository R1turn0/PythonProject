import threading
import tkinter as tk
import xml.etree.ElementTree as ET
import os
import ctypes
import sys
import locale
import subprocess
from tkinter import messagebox
import platform
import datetime
import winreg
import glob
import shutil
import zipfile
import traceback
import py_control
import json
import logging
import requests
from bs4 import BeautifulSoup


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def elevate():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()


def get_locale_text():
    # Get system language
    # lang = locale.getdefaultlocale()[0]
    lang, _ = locale.getdefaultlocale()
    # lang, encoding = locale.getlocale()
    if lang.startswith('zh_CN'):
        return {
            "title": "ss日志工具",
            "current_mode": "当前模式：",
            "debug": "打开调试日志",
            "normal": "关闭调试日志",
            "debug_mode": "当前模式：调试日志模式",
            "normal_mode": "当前模式：正常日志模式",
            "service_status": "显示Sense Shield Service状态",
            "log_collect": "收集日志",
            "mode_changed": "模式已更改，更改模式后，需要重启SenseShield服务，现在正在重启。\n",
            "stop_success": "Sense Shield Service停止成功。\n",
            "stop_fail": "Sense Shield Service停止失败。\n",
            "start_success": "Sense Shield Service启动成功。\n",
            "start_fail": "Sense Shield Service启动失败。\n",
            "query_fail": "查询Sense Shield Service状态失败:\n",
            "service_config": "检查服务配置",
            "DENY_ALL_WITH_EXCEPTION": "白名单",
            "ALLOW_ALL_WITH_EXCEPTION": "黑名单",
            "cs_status_button": "查询用户工具CS状态",
            "cs_status_c": "客户端状态",
            "cs_status_cs": "服务端状态",
            "cs_status_local": "本地状态",
            "print_license_status": "查询服务器许可状态",
            "ping_ip_address": "Ping服务器",
            "ip_port_access": "访问服务器端口"
        }
    else:
        return {
            "title": "ss Debug Mode Modification Tool",
            "current_mode": "Current mode:",
            "debug": "Enable Debug Log",
            "normal": "Disable Debug Log",
            "debug_mode": "Current mode: Debug Log Mode",
            "normal_mode": "Current mode: Normal Log Mode",
            "service_status": "Show Sense Shield Service Status",
            "log_collect": "Log Collection",
            "mode_changed": "Mode changed, SenseShield service needs to be restarted \
            after changing mode, now restarting.\n",
            "stop_success": "Sense Shield Service stopped successfully.\n",
            "stop_fail": "Sense Shield Service failed to stop.\n",
            "start_success": "Sense Shield Service started successfully.\n",
            "start_fail": "Sense Shield Service failed to start.\n",
            "query_fail": "Failed to query Sense Shield Service status:\n",
            "service_config": "Check Server Configuration",
            "DENY_ALL_WITH_EXCEPTION": "White list",
            "ALLOW_ALL_WITH_EXCEPTION": "Black list",
            "cs_status_button": "Query CS Status",
            "cs_status_c": "Client Status",
            "cs_status_cs": "Server Status",
            "cs_status_local": "Local Status",
            "print_license_status": "License Context",
            "ping_ip_address": "Ping IP",
            "ip_port_access": "Access IP:Port"
        }


# 平台判断
if platform.uname().release == 'XP':
    XML_FILE = 'C:\\Documents and Settings\\All Users\\Application Data\\senseshield\\ss_service'
else:
    XML_FILE = 'C:/ProgramData/SenseShield/ss_service/ss_config.xml'
LOG_LEVEL_ELEM = 'LOG/LEVEL'
CS_TYPE_ELEM = 'GENERAL/TYPE'
locale_text = get_locale_text()

g_frame_button = None
g_log_output = None


class App:
    def __init__(self, master):
        global g_frame_button
        # master.attributes('-toolwindow', True)
        master.title(locale_text["title"])
        self.frame1 = tk.Frame(master)
        self.label = tk.Label(self.frame1, text=locale_text["current_mode"])
        self.label.pack()
        self.status_button = tk.Button(self.frame1, text=locale_text["service_status"],
                                       command=self.show_service_status)
        self.status_button.pack(side="left")
        self.debug_button = tk.Button(self.frame1, text=locale_text["debug"], command=self.set_debug)
        self.debug_button.pack(side="left")
        self.normal_button = tk.Button(self.frame1, text=locale_text["normal"], command=self.set_normal)
        self.normal_button.pack(side="left")
        self.frame1.pack()
        g_frame_button = self.frame1

        self.frame2 = tk.Frame(master)
        self.config_button = tk.Button(self.frame2, text=locale_text["service_config"],
                                       command=self.check_server_config)
        self.config_button.pack(side="left")
        self.cs_status_button = tk.Button(self.frame2, text=locale_text["cs_status_button"],
                                          command=self.show_cs_status)
        self.cs_status_button.pack(side="left")
        self.license_status_button = tk.Button(self.frame2, text=locale_text["print_license_status"],
                                               command=self.show_elite5_status)
        self.license_status_button.pack(side="left")
        self.frame2.pack()

        self.frame3 = tk.Frame(master)
        self.ping_ip_button = tk.Button(self.frame3, text=locale_text["ping_ip_address"],
                                        command=lambda: self.ping_ip_thread(self.ip_address_text.get()))
        self.ping_ip_button.pack(side="left")
        self.ping_ip_master = self.ping_ip_button.winfo_toplevel()
        self.access_service_port_button = tk.Button(self.frame3, text=locale_text["ip_port_access"],
                                                    command=lambda: self.access_service_port_thread(
                                                        self.ip_address_text.get()))
        self.access_service_port_button.pack(side="left")
        self.access_service_port_master = self.access_service_port_button.winfo_toplevel()
        self.ip_address_text = tk.Entry(self.frame3, width=20)
        self.ip_address_text.pack(side="left")
        self.frame3.pack()

        self.frame_text_output = tk.Frame(master)

        self.label_output = tk.Label(self.frame_text_output, text="日志")
        self.label_output.pack()
        self.log_output = tk.Text(self.frame_text_output, wrap=tk.WORD, height=10)
        self.log_output.pack(expand=True, fill=tk.BOTH)
        self.scrollbar = tk.Scrollbar(self.log_output)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_output.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.log_output.yview)
        self.frame_text_output.pack(side="bottom", expand=True, fill=tk.BOTH)

        global g_log_output
        g_log_output = self.log_output
        self.update_label()

    def update_label(self):
        if os.path.exists(XML_FILE) is not True:
            raise FileNotFoundError(XML_FILE)
        tree = ET.parse(XML_FILE)
        log_level = tree.find(LOG_LEVEL_ELEM).text

        if log_level == '0':
            self.label.config(text=locale_text["debug_mode"])
        else:
            self.label.config(text=locale_text["normal_mode"])

    def set_log_level(self, level):
        tree = ET.parse(XML_FILE)
        log_level_elem = tree.find(LOG_LEVEL_ELEM)
        log_level_elem.text = str(level)
        tree.write(XML_FILE)

        self.update_label()

    def set_debug(self):
        self.set_log_level(0)
        self.log_output.insert(tk.END, locale_text["mode_changed"])
        self.log_output.see(tk.END)

        self.restart_senseshield_service()

    def set_normal(self):
        self.set_log_level(3)
        self.log_output.insert(tk.END, locale_text["mode_changed"])
        self.log_output.see(tk.END)

        self.restart_senseshield_service()

    def restart_senseshield_service(self):
        return_code = os.system('sc stop "Sense Shield Service"')
        if return_code == 0:
            self.log_output.insert(tk.END, locale_text["stop_success"])
        else:
            self.log_output.insert(tk.END, locale_text["stop_fail"])
        self.log_output.see(tk.END)
        return_code = os.system('sc start "Sense Shield Service"')
        if return_code == 0:
            self.log_output.insert(tk.END, locale_text["start_success"])
        else:
            self.log_output.insert(tk.END, locale_text["start_fail"])
        self.log_output.see(tk.END)
        self.show_log_status()

    def show_service_status(self):
        try:
            output = subprocess.check_output('sc query "Sense Shield Service"', stderr=subprocess.STDOUT, shell=True)
            output = str(output)
            if "RUNNING" in output:
                ss_status = "RUNNING"
                self.log_output.insert(tk.END, 'Sense Shield Service状态:\n{}\n'.format(ss_status))
            elif "STOPPED" in output:
                ss_status = "STOPPED"
                self.log_output.insert(tk.END, 'Sense Shield Service状态:\n{}\n'.format(ss_status))
            else:
                self.log_output.insert(tk.END, 'Sense Shield Service状态查询失败:\n')

        except subprocess.CalledProcessError as e:
            self.log_output.insert(tk.END, '{}{}\n'.format(locale_text["query_fail"], e.output))

        self.log_output.see(tk.END)

    def show_log_status(self):
        try:
            tree = ET.parse(XML_FILE)
            log_level = tree.find(LOG_LEVEL_ELEM).text
            if log_level == '0':
                output = locale_text["debug_mode"]
            else:
                output = locale_text["normal_mode"]
            self.log_output.insert(tk.END, '{}\n'.format(output))
        except subprocess.CalledProcessError as e:
            self.log_output.insert(tk.END, '{}{}\n'.format(locale_text["query_fail"], e.output))

        self.log_output.see(tk.END)

    def check_server_config(self):
        try:
            tree = ET.parse(XML_FILE)
            xml_root = tree.getroot()

            for proxy_element in xml_root.iter('PROXY'):
                type_element = proxy_element.find('TYPE')
                if type_element is not None and type_element.text == 'NONE':
                    output = f"Proxy type is \"NONE\""
                    self.log_output.insert(tk.END, '{}\n'.format(output))
                elif type_element is not None:
                    output = f"Proxy type is \"{type_element.text}\""
                    self.log_output.insert(tk.END, '{}\n'.format(output))

            for server_element in xml_root.iter('SERVER'):
                allow_mode_element = server_element.find('ALLOW_MODE')
                if allow_mode_element is not None and allow_mode_element.text == 'ALLOW_ALL':
                    output = f"Allow mode is \"ALLOW_ALL\""
                    self.log_output.insert(tk.END, '{}\n'.format(output))
                elif allow_mode_element is not None:
                    output = f"Allow mode is \"{locale_text.get(allow_mode_element.text, allow_mode_element.text)}\""
                    # output = f"Allow mode is \"{allow_mode_element.text}\""
                    self.log_output.insert(tk.END, '{}\n'.format(output))
        except ET.ParseError as check_server_config_error:
            self.log_output.insert(tk.END, '{}\n'.format(check_server_config_error))

    def show_cs_status(self):
        try:
            tree = ET.parse(XML_FILE)
            CS_type = tree.find(CS_TYPE_ELEM).text
            if CS_type == 'C':
                output = locale_text["cs_status_c"]
            elif CS_type == 'CS':
                output = locale_text["cs_status_cs"]
            else:
                output = locale_text["cs_status_local"]
            self.log_output.insert(tk.END, '{}\n'.format(output))
        except subprocess.CalledProcessError as e:
            self.log_output.insert(tk.END, '{}{}\n'.format(locale_text["query_fail"], e.output))
        self.log_output.see(tk.END)

    def show_elite5_status(self):
        try:
            JSON = 2
            h_ipc = ctypes.c_void_p()
            license_id = ctypes.c_char_p()
            pchar_lock_array = ctypes.c_char_p(b"")
            pchar_license_array = ctypes.c_char_p(b"")
            slm_control = py_control.init_slm_control()

            ret = slm_control.slm_ctrl_client_open(ctypes.byref(h_ipc))
            ret = slm_control.slm_ctrl_get_local_description(h_ipc, JSON, ctypes.byref(pchar_lock_array))
            if ret != 0:
                logging.error('slm_ctrl_get_local_description error:0x%08X', ret)
                return ret
            else:
                logging.info('slm_ctrl_get_local_description ok')
                pjson_local_array = json.loads(pchar_lock_array.value)
                if not pjson_local_array:
                    logging.warning('pjson_python_data is NULL')
                    self.log_output.insert(tk.END, '{}\n'.format('没找到网络锁设备，请检查'))

                local_desc = pjson_local_array[0]
                local_desc_object = ctypes.c_char_p(json.dumps(local_desc).encode('utf-8'))

                ret = slm_control.slm_ctrl_read_brief_license_context(h_ipc, JSON, local_desc_object,
                                                                      ctypes.byref(pchar_license_array))
                if ret != 0:
                    logging.error('slm_ctrl_read_brief_license_context error:0x%08X', ret)
                    return ret
                else:
                    logging.info('slm_ctrl_read_brief_license_context ok')
                    pjson_license_array = json.loads(pchar_license_array.value)
                    if not pjson_license_array:
                        logging.warning('pjson_license_array is NULL')

                    # license_ids = [license_info.get('license_id', 'N/A') for license_info in pjson_license_array]
                    # output = f"License ID: {license_ids}"
                    # self.log_output.insert(tk.END, '{}\n'.format(output))

                    for license_info in pjson_license_array:
                        license_id = license_info.get('license_id', 'N/A')
                        if license_id == 0:
                            continue
                        license_enable = license_info.get('enable', 'N/A')
                        license_concurrent_type = license_info.get('concurrent_type', 'N/A')
                        license_concurrent = license_info.get('concurrent', 'N/A')

                        output_parts = [
                            f"License ID: {license_info.get('license_id', 'N/A')}",
                            f"Enable Status: {license_info.get('enable', 'N/A')}"
                        ]

                        if license_concurrent == 0:
                            output_parts += ["Concurrent Type: local"]
                        else:
                            output_parts += [
                                f"Concurrent Type: {license_info.get('concurrent_type', 'N/A')}",
                                f"Concurrent: {license_info.get('concurrent', 'N/A')}"
                            ]

                        output_str = '  '.join(['{:<{}}'.format(part, len(part) + 1) for part in output_parts])
                        self.log_output.insert(tk.END, '{}\n'.format(output_str))

            ret = slm_control.slm_ctrl_client_close(h_ipc)
        except subprocess.CalledProcessError as e:
            self.log_output.insert(tk.END, '{}{}\n'.format(locale_text["query_fail"], e.output))
        self.log_output.see(tk.END)

    # def ping_ip_thread(self, ip_address):
    #     ping_thread = threading.Thread(target=self.ping_ip, args=(ip_address,))
    #     ping_thread.start()

    def ping_ip_thread(self, ip_address):
        # Disable the button
        self.ping_ip_button.config(state=tk.DISABLED)
        # Start the ping thread
        ping_thread = threading.Thread(target=self.ping_ip, args=(ip_address,))
        ping_thread.start()
        # Monitor the thread and enable the button when it completes
        self.ping_ip_master.after(100, self.check_ping_thread, ping_thread)

    def check_ping_thread(self, ping_thread):
        if ping_thread.is_alive():
            # If the thread is still running, check again after 100 milliseconds
            self.ping_ip_master.after(100, self.check_ping_thread, ping_thread)
        else:
            # If the thread has completed, enable the button
            self.ping_ip_button.config(state=tk.NORMAL)

    def ping_ip(self, ip_address):
        try:
            if not ip_address:
                raise ValueError("IP address is empty")

            # 执行 ping 命令
            self.log_output.insert(tk.END, '请等待返回结果...')
            result = subprocess.run(["ping", "-n", "4", ip_address], text=True, check=True, capture_output=True)

            if result.returncode == 0:
                output = f"{ip_address} is reachable."
            else:
                output = f"{ip_address} is unreachable."

            # 使用主线程更新 GUI
            self.log_output.insert(tk.END, '{}\n'.format(output))
            self.log_output.see(tk.END)

        except subprocess.CalledProcessError as e:
            output = f"{ip_address} is unreachable."
            self.log_output.insert(tk.END, '{}\n'.format(output))
            self.log_output.insert(tk.END, '{}\n'.format(str(e)))
            self.log_output.see(tk.END)

        except ValueError as e:
            # 处理空 IP 地址的情况
            self.log_output.insert(tk.END, '{}\n'.format(str(e)))
            self.log_output.see(tk.END)

    def access_service_port_thread(self, ip_address):
        # Disable the button
        self.access_service_port_button.config(state=tk.DISABLED)
        # Start the ping thread
        ping_thread = threading.Thread(target=self.access_service_port, args=(ip_address,))
        ping_thread.start()
        # Monitor the thread and enable the button when it completes
        self.access_service_port_master.after(100, self.check_access_service_port_thread, ping_thread)

    def check_access_service_port_thread(self, ping_thread):
        if ping_thread.is_alive():
            # If the thread is still running, check again after 100 milliseconds
            self.access_service_port_master.after(100, self.check_access_service_port_thread, ping_thread)
        else:
            # If the thread has completed, enable the button
            self.access_service_port_button.config(state=tk.NORMAL)

    def access_service_port(self, ip_address):
        if not ip_address:
            tips_1 = "请输入服务端ip地址"
            self.log_output.insert(tk.END, '{}\n'.format(tips_1))
        else:
            url = "http://" + ip_address + ":10334"
            try:
                response = requests.get(url, verify=False)  # verify=False 忽略 SSL 证书验证，仅在信任环境下使用
                response.raise_for_status()  # 检查是否成功
                self.log_output.insert(tk.END, 'Success to access: {}\n'.format(url))
            except requests.exceptions.RequestException as e:
                # 处理异常，将异常信息记录到日志中
                self.log_output.insert(tk.END, 'Failed to access: {}: {}\n'.format(url, str(e)))


class LogCollector:
    def __init__(self, master):
        self.master = master

        self.frame1 = tk.Frame(master)
        # master.title("Senseshield Log Collector")
        # self.title_lable = tk.Label(self.frame1,text="日志打包")
        # self.title_lable.pack()
        self.log_path_label = tk.Label(self.frame1, text="日志路径")
        self.log_path_label.grid(row=0, column=0, sticky="w")
        # self.log_path_label.pack(side="left")
        self.log_path = tk.Entry(self.frame1, width=60)
        self.log_path.insert(0, self.get_log_path_from_registry())
        self.log_path.grid(row=0, column=1)
        # self.log_path.pack(side="left")

        self.archive_name_label = tk.Label(self.frame1, text="压缩包名称")
        self.archive_name_label.grid(row=1, column=0, sticky="w")
        self.archive_name = tk.Entry(self.frame1, width=60)
        default_archive_name = "{}_{}_ss_log".format(datetime.date.today(), platform.node())
        self.archive_name.insert(0, default_archive_name)
        self.archive_name.grid(row=1, column=1)

        self.output_path_label = tk.Label(self.frame1, text="打包输出路径")
        self.output_path_label.grid(row=2, column=0, sticky="w")
        self.output_path = tk.Entry(self.frame1, width=60)
        self.output_path.insert(0, os.getcwd())
        self.output_path.grid(row=2, column=1)

        self.target_days_label = tk.Label(self.frame1, text="目标日志天数")
        self.target_days_label.grid(row=3, column=0, sticky="w")
        self.target_days = tk.Entry(self.frame1, width=60)
        self.target_days.insert(0, "31")
        self.target_days.grid(row=3, column=1)

        self.target_size_label = tk.Label(self.frame1, text="日志大小（MB）")
        self.target_size_label.grid(row=4, column=0, sticky="w")
        self.target_size = tk.Entry(self.frame1, width=60)
        self.target_size.insert(0, "100")
        self.target_size.grid(row=4, column=1)

        self.collect_logs_button = tk.Button(g_frame_button, text=locale_text["log_collect"], command=self.collect_logs)
        self.collect_logs_button.pack()

        # self.log_output = tk.Text(self.frame1, wrap=tk.WORD, height=10)
        # self.log_output.grid(row=6, column=0, columnspan=2, sticky="nsew")
        # self.scrollbar = tk.Scrollbar(self.log_output)
        # self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # self.log_output.config(yscrollcommand=self.scrollbar.set)
        # self.scrollbar.config(command=self.log_output.yview)

        self.log_output = g_log_output

        self.frame1.columnconfigure(1, weight=1)
        self.frame1.rowconfigure(6, weight=1)

        self.frame1.pack()

    def get_log_path_from_registry(self):
        try:
            if platform.machine().endswith('64'):
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                     r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\senseshield")
            else:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                     r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\senseshield")
            value, _ = winreg.QueryValueEx(key, "UninstallString")
            winreg.CloseKey(key)
            install_path = value.replace("uninstall.exe", "")
            log_path = os.path.join(install_path, "log")
            return log_path
        except FileNotFoundError:
            return "无法从注册表获取安装路径"

    def collect_logs(self):
        if messagebox.askyesno("关闭SenseShield服务", "是否需要关闭SenseShield服务，获取更详细的日志？"):
            self.restart_senseshield_service()

        log_path = self.log_path.get()
        archive_name = self.archive_name.get()
        output_path = self.output_path.get()
        target_days = int(self.target_days.get())
        target_size = int(self.target_size.get())

        self.log_output.insert(tk.END, "收集日志中...\n")
        self.collect_logs_from_path(log_path, archive_name, output_path, target_days, target_size)
        self.log_output.insert(tk.END, "日志收集完成\n")
        self.log_output.see(tk.END)

    def restart_senseshield_service(self):
        return_code = os.system('sc stop "Sense Shield Service"')
        if return_code == 0:
            self.log_output.insert(tk.END, locale_text["stop_success"])
        else:
            self.log_output.insert(tk.END, locale_text["stop_fail"])
        self.log_output.see(tk.END)
        return_code = os.system('sc start "Sense Shield Service"')
        if return_code == 0:
            self.log_output.insert(tk.END, locale_text["start_success"])
        else:
            self.log_output.insert(tk.END, locale_text["start_fail"])
        self.log_output.see(tk.END)
        # self.show_log_status()

    def collect_logs_from_path(self, log_path, archive_name, output_path, target_days, target_size):
        output_dir = os.path.join(output_path, archive_name)
        os.makedirs(output_dir, exist_ok=True)
        # csv文件
        # todo：dump文件收集
        # 计算机信息收集
        target_date = datetime.datetime.now() - datetime.timedelta(days=target_days)
        csv_files = glob.glob(os.path.join(log_path, "*.csv"))

        total_size = 0
        log_files_by_type = {}
        for csv_file in csv_files:
            file_stat = os.stat(csv_file)
            file_date = datetime.datetime.fromtimestamp(file_stat.st_mtime)

            if file_date >= target_date:
                log_type = os.path.basename(csv_file).split("_")[0]
                if log_type not in log_files_by_type:
                    log_files_by_type[log_type] = []

                log_files_by_type[log_type].append((csv_file, file_stat.st_mtime, file_stat.st_size))
                total_size += file_stat.st_size

        # 如果日志大小超过目标日志大小，则限制每种日志类型的大小为4MB
        if total_size > target_size * 1024 * 1024:
            log_size_limit_per_type = target_size / 5 * 1024 * 1024
            for log_type in log_files_by_type:
                log_files_by_type[log_type].sort(key=lambda x: x[1], reverse=True)
                accumulated_size = 0
                for idx, (csv_file, mtime, size) in enumerate(log_files_by_type[log_type]):
                    accumulated_size += size
                    if accumulated_size > log_size_limit_per_type:
                        log_files_by_type[log_type] = log_files_by_type[log_type][:idx]
                        break

        for log_type in log_files_by_type:
            for csv_file, _, _ in log_files_by_type[log_type]:
                shutil.copy(csv_file, output_dir)

                self.log_output.insert(tk.END, "复制文件: {}\n".format(csv_file))
                self.log_output.see(tk.END)

        # 在这里实现根据条件过滤和压缩日志文件的功能
        output_dir = os.path.join(output_path, archive_name)
        os.makedirs(output_dir, exist_ok=True)
        # 在这里添加压缩日志文件的功能
        zip_filename = "{}.zip".format(archive_name)
        zip_path = os.path.join(output_path, zip_filename)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for log_type in log_files_by_type:
                for csv_file, _, _ in log_files_by_type[log_type]:
                    arcname = os.path.join(archive_name, os.path.basename(csv_file))
                    zipf.write(csv_file, arcname)

                    self.log_output.insert(tk.END, "添加到压缩文件: {}\n".format(csv_file))
                    self.log_output.see(tk.END)

        self.log_output.insert(tk.END, "日志文件已压缩为: {}\n".format(zip_path))
        self.log_output.see(tk.END)


if __name__ == "__main__":
    try:
        elevate()
        root = tk.Tk()
        app = App(root)
        log_collector = LogCollector(root)
        root.mainloop()
    except Exception as e:
        with open("ss-log-tool.log", mode="w", encoding="utf-8") as f:
            f.write(str(e.args))
            f.write(traceback.format_exc())
