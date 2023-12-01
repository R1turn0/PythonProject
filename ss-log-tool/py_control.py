import ctypes
import json
from ctypes.wintypes import HLOCAL
import platform
import binascii


# slm_ctrl_client_close                                @6
# slm_ctrl_client_open                                 @7
# slm_ctrl_get_local_description                       @21
# slm_ctrl_get_license_id                              @20
# slm_ctrl_read_brief_license_context                  @35
# slm_ctrl_free                                        @12
def init_slm_control():
    # 加载 so，初始化接口函数
    # 引用 so（x86或x64） 与当前运行环境中的 python.exe 解释器（32位、64位）保持相同，否则会加载失败。
    archi = platform.architecture()
    print(archi[0])
    if platform.system() == "Windows":
        if archi[0] == '32bit':
            control_dll_path = r'./x86/slm_control.dll'
        elif archi[0] == '64bit':
            control_dll_path = r'./x64/slm_control.dll'

        slm_control = ctypes.cdll.LoadLibrary(control_dll_path)

    if platform.system() == "Windows":
        # windows中的函数需要手动定位在动态库中的位置
        slm_control.slm_ctrl_get_license_id = slm_control[20]
        slm_control.slm_ctrl_get_local_description = slm_control[21]
        slm_control.slm_ctrl_client_open = slm_control[7]
        slm_control.slm_ctrl_client_close = slm_control[6]
        slm_control.slm_ctrl_free = slm_control[12]
        slm_control.slm_ctrl_read_brief_license_context = slm_control[35]

    # 处理返回值

    slm_control.slm_ctrl_get_local_description.restype = ctypes.c_uint32
    slm_control.slm_ctrl_get_license_id.restype = ctypes.c_uint32
    slm_control.slm_ctrl_client_open.restype = ctypes.c_uint32
    slm_control.slm_ctrl_client_close.restype = ctypes.c_uint32
    slm_control.slm_ctrl_read_brief_license_context.restype = ctypes.c_uint32
    slm_control.slm_ctrl_free.restype = ctypes.c_uint32
    return slm_control


def print_license_context():
    JSON = 2
    h_ipc = ctypes.c_void_p()
    local_desc = ctypes.c_char_p()
    license_result = ctypes.c_char_p()
    slm_control = init_slm_control()

    r = slm_control.slm_ctrl_client_open(ctypes.byref(h_ipc))
    r = slm_control.slm_ctrl_get_local_description(h_ipc, JSON, ctypes.byref(local_desc))
    if r != 0:
        print('slm_ctrl_get_local_description error:0x%08X', r)
    else:
        print('slm_ctrl_get_local_description ok')
        print('slm_ctrl_get_local_description r', r, local_desc.value)
        python_data = json.loads(local_desc.value)
        result_dict = python_data[0]
        converted_result = ctypes.c_char_p(json.dumps(result_dict).encode('utf-8'))

    # r = slm_control.slm_ctrl_get_license_id(h_ipc, JSON, converted_result, ctypes.byref(license_result))
    r = slm_control.slm_ctrl_read_brief_license_context(h_ipc, JSON, converted_result, ctypes.byref(license_result))
    if r != 0:
        print('slm_ctrl_read_brief_license_context error:0x%08X', r)
    else:
        print('slm_ctrl_read_brief_license_context ok')
        print('slm_ctrl_read_brief_license_context r', r, license_result.value)

    r = slm_control.slm_ctrl_client_close(h_ipc)
    return r

# if __name__ == "__main__":
#
#  JSON = 2
#  local_desc = ctypes.c_char_p()
#  license_result = ctypes.c_char_p()
#  h_ipc = ctypes.c_uint32(0)
#  slm_control = init_slm_control()
#  r = slm_control.slm_ctrl_client_open(ctypes.byref(h_ipc))
#  r = slm_control.slm_ctrl_get_local_description(h_ipc, JSON, ctypes.byref(local_desc))
#  if r != 0:
#      print('slm_ctrl_get_local_description error:0x%08X',r)
#  else:
#      print('slm_ctrl_get_local_description ok')
#      print('slm_ctrl_get_local_description r', r, local_desc.value)
#      python_data = json.loads(local_desc.value)
#      result_dict = python_data[0]
#      converted_result = ctypes.c_char_p(json.dumps(result_dict).encode('utf-8'))
#
# #r = slm_control.slm_ctrl_get_license_id(h_ipc, JSON, converted_result, ctypes.byref(license_result))
#  r = slm_control.slm_ctrl_read_brief_license_context(h_ipc, JSON, converted_result, ctypes.byref(license_result))
#  if r != 0:
#      print('slm_ctrl_get_license_id error:0x%08X',r)
#  else:
#      print('slm_ctrl_get_license_id ok')
#      print('slm_ctrl_get_license_id r', r, license_result.value)
#
#  r = slm_control.slm_ctrl_client_close(h_ipc)

# r = print_license_context()
