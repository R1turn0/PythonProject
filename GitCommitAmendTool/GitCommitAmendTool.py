import os
import subprocess
import pyautogui

# 运行前需要修改这些参数！！！
day = 15
start_date = '2023 12 01'
file_path = r'D:\WorkSpace\Tac\ss-log-tool\dll'


def get_directory_path():
    # 使用 os.listdir() 获取指定目录中的文件列表
    file_list = os.listdir(file_path)

    # # 使用双引号括起文件名并输出
    # quoted_file_list = ['\n' + '"' + filename + '"' for filename in file_list]
    # # 将括起来的文件名列表输出为字符串
    # output_string = ', '.join(quoted_file_list)
    # print(output_string)

    return file_list


def run_git_amend_date_tool():
    # 启动外部命令
    process = subprocess.Popen("GitAmendDateTool.exe", stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

    # 输入 count 和 start_date
    input_data = f"{day}\n{start_date}\n"
    process.stdin.write(input_data)
    process.stdin.flush()

    # 等待命令执行完成并获取输出
    output, _ = process.communicate()

    # 检查命令是否成功执行
    if process.returncode == 0:
        # 将命令输出按换行符分割存储在数组中
        output_lines = output.splitlines()
        # output内获取的输出会将一些输入提示信息一起加入到程序内，所以应该删除数组第1个元素
        if output_lines is not None and len(output_lines) > 0:
            output_lines.pop(0)
        return output_lines
    else:
        # 如果命令执行失败，打印错误信息
        print(f"Error: {output}")
        return None


def git_commit_amend(file_list, amend_date):
    # 获取指定窗口的焦点，可以使用窗口标题或其他标识符
    window_title = "MINGW64"

    try:
        pyautogui.getWindowsWithTitle(window_title)[0].activate()

        # 等待一段时间以确保窗口获得焦点
        pyautogui.sleep(1)
        # 定义计数器
        counter = 0

        # 'zip' 函数会以最短地输入长度为准
        for file_list, amend_data in zip(file_list, amend_date):
            # 添加计数器
            counter += 1
            print(f"循环第 {counter} 次")

            # 模拟键盘输入 "git add dll/"
            pyautogui.typewrite("git add dll/")

            pyautogui.typewrite(file_list)
            # 模拟按下键盘的enter键
            pyautogui.press('enter')
            # 模拟释放键盘的enter键
            # pyautogui.release('enter')
            pyautogui.sleep(0.3)

            pyautogui.typewrite("git commit -m \"Upload\"")
            pyautogui.press('enter')
            pyautogui.sleep(0.3)

            # 输入git commit --amend
            pyautogui.typewrite(amend_data)
            # 模拟按下键盘的enter键
            pyautogui.press('enter')
            # pyautogui.hotkey('alt', 's')
            pyautogui.sleep(0.3)

            pyautogui.typewrite(":q")
            pyautogui.press('enter')
            pyautogui.sleep(0.3)

        return counter

    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    file = get_directory_path()
    print(file)

    time = run_git_amend_date_tool()
    print(time)

    git_commit_amend(file, time)
