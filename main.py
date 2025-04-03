import os
import re
import datetime
import ctypes
from ctypes import wintypes

def set_file_times():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(base_dir, "ChangeFiles")
    pattern = re.compile(r'^(\d{8})_(\d{6})')

    modified_entries = []
    unmodified_entries = []

    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    SetFileTime = kernel32.SetFileTime
    SetFileTime.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.FILETIME),
                            ctypes.POINTER(wintypes.FILETIME), ctypes.POINTER(wintypes.FILETIME)]
    CreateFileW = kernel32.CreateFileW
    CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                            wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    
    GENERIC_WRITE = 0x40000000
    OPEN_EXISTING = 3
    FILE_SHARE_READ = 0x00000001
    FILE_SHARE_WRITE = 0x00000002

    def to_filetime(dt):
        posix_ts = int(dt.timestamp() * 10000000 + 116444736000000000)
        return wintypes.FILETIME(posix_ts & 0xFFFFFFFF, posix_ts >> 32)

    for file_name in os.listdir(target_dir):
        if not os.path.isfile(os.path.join(target_dir, file_name)):
            continue
        base, _ = os.path.splitext(file_name)
        match = pattern.match(base)
        if match:
            yyyymmdd, hhmmss = match.groups()
            dt = datetime.datetime.strptime(yyyymmdd+hhmmss, '%Y%m%d%H%M%S')
            handle = CreateFileW(
                os.path.join(target_dir, file_name),
                GENERIC_WRITE,
                FILE_SHARE_READ | FILE_SHARE_WRITE,
                None,
                OPEN_EXISTING,
                0,
                None
            )
            if handle != -1:
                ft = to_filetime(dt)
                SetFileTime(handle, ctypes.byref(ft), ctypes.byref(ft), ctypes.byref(ft))
                ctypes.windll.kernel32.CloseHandle(handle)
            modified_entries.append(f"{file_name} -> {dt.strftime('%Y年%m月%d日 %H:%M:%S')}")
        else:
            unmodified_entries.append(f"{file_name} -> 未修改")

    log_path = os.path.join(base_dir, "log.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        for entry in modified_entries:
            f.write(entry + "\n")
        if modified_entries and unmodified_entries:
            f.write("\n")
        for entry in unmodified_entries:
            f.write(entry + "\n")
    

if __name__ == "__main__":
    set_file_times()