"""
tool to resize window

Features:
- get_hwnd_from_pid(pid)
- get_hwnd_from_exe(exe)
- get_hwnd_from_title(title)

- get_pid_from_exe(exe)
- get_title_from_hwnd(hwnd)

- get_window_pos(hwnd)
- set_window_pos(hwnd, left, top, right, bottom)

- make_resizable(hwnd)

- show_title_bar(hwnd)
- hide_title_bar(hwnd)

Author: tabethereal
License: MIT License
"""

from ctypes import *
from ctypes.wintypes import *

FindWindow = windll.user32.FindWindowW
SetWindowPos = windll.user32.SetWindowPos
GetWindowRect = windll.user32.GetWindowRect
CreateToolhelp32Snapshot= windll.kernel32.CreateToolhelp32Snapshot
Process32First = windll.kernel32.Process32First
Process32Next = windll.kernel32.Process32Next
CloseHandle = windll.kernel32.CloseHandle
IsWindowVisible = windll.user32.IsWindowVisible
EnumWindows = windll.user32.EnumWindows
EnumWindowsType = WINFUNCTYPE(BOOL, HWND, LPARAM)
GetWindowThreadProcessId = windll.user32.GetWindowThreadProcessId
GetWindowText = windll.user32.GetWindowTextW
GetWindowTextLength = windll.user32.GetWindowTextLengthW
GetWindowLong = windll.user32.GetWindowLongW
SetWindowLong = windll.user32.SetWindowLongW
ShowWindow = windll.user32.ShowWindow

SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
TH32CS_SNAPPROCESS = 0x00000002
GWL_STYLE = -16
WS_MAXIMIZEBOX = 0x00010000
WS_MINIMIZEBOX = 0x00020000
WS_SIZEBOX = 0x00040000
WS_SYSMENU = 0x00080000
WS_CAPTION = 0x00c00000
SW_NORMAL = 1
SW_MAXIMIZE = 3
SW_MINIMIZE = 6

class RECT(Structure):
    _fields_ = [
    ('left',    c_long),
    ('top',     c_long),
    ('right',   c_long),
    ('bottom',  c_long),
    ]
    def width(self):  return self.right  - self.left
    def height(self): return self.bottom - self.top

class PROCESSENTRY32(Structure):
    _fields_ = [('dwSize', DWORD),
                ('cntUsage', DWORD),
                ('th32ProcessID', DWORD),
                ('th32DefaultHeapID', LPVOID),
                ('th32ModuleID', DWORD),
                ('cntThreads', DWORD),
                ('th32ParentProcessID', DWORD),
                ('pcPriClassBase', LONG),
                ('dwFlags', DWORD), 
                ('szExeFile', c_char * 260)]

def get_title_from_hwnd(hwnd):
    length = GetWindowTextLength(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    GetWindowText(hwnd, buff, length + 1)
    return buff.value

def get_pid_from_exe(exe):
    if type(exe) != bytes: exe = exe.encode()
    pids = []
    handle = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, None)
    process = PROCESSENTRY32()
    process.dwSize = sizeof(process)
    if Process32First(handle, byref(process)):
        while True:
            if process.szExeFile == exe:
                pids.append(process.th32ProcessID)
            if not Process32Next(handle, byref(process)):
                break
    CloseHandle(handle)
    return pids[0]

def get_hwnd_from_pid(pid):
    handles = []
    def callback(hwnd, pid):
        current_pid = DWORD()
        GetWindowThreadProcessId(hwnd, byref(current_pid))
        if current_pid.value == pid:
            if IsWindowVisible(hwnd) and get_title_from_hwnd(hwnd):
                handles.append(hwnd)
        return True
    EnumWindows(EnumWindowsType(callback), pid)
    return handles[0]

def get_hwnd_from_exe(exe):
    return get_hwnd_from_pid(get_pid_from_exe(exe))

def get_hwnd_from_title(title):
    return FindWindow(None, title)

def get_window_pos(hwnd):
    pos = RECT()
    GetWindowRect(hwnd, byref(pos))
    return (pos.left, pos.top, pos.right, pos.bottom)

def set_window_pos(hwnd, left, top, right, bottom):
    ShowWindow(hwnd, SW_NORMAL)
    SetWindowPos(hwnd, 0, left, top, right - left, bottom - top, SWP_NOZORDER)

def make_resizable(hwnd):
    style = GetWindowLong(hwnd, GWL_STYLE)
    style |= WS_SIZEBOX
    SetWindowLong(hwnd, GWL_STYLE, style)

def show_title_bar(hwnd):
    style = GetWindowLong(hwnd, GWL_STYLE)
    style |= WS_CAPTION | WS_SYSMENU | WS_MAXIMIZEBOX | WS_MINIMIZEBOX
    SetWindowLong(hwnd, GWL_STYLE, style)

def hide_title_bar(hwnd):
    style = GetWindowLong(hwnd, GWL_STYLE)
    style &= ~WS_CAPTION
    SetWindowLong(hwnd, GWL_STYLE, style)

