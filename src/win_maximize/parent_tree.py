import ctypes

# Usage of CreateToolhelp32Snapshot, thanks of Fabio Zadrozny
# https://pydev.blogspot.com/2013/01/python-get-parent-process-id-pid-in.html

# Changed to return full parent tree by Dawid Gosławski

# ParentTree aligned according to:
# https://stackoverflow.com/questions/52139683/ctypes-defined-processentry32-yields-incorrect-size-when-using-ctypes-sizeof

TH32CS_SNAPPROCESS = 0x00000002

CreateToolhelp32Snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot

MAX_PATH = 260

_kernel32dll = ctypes.windll.Kernel32
CloseHandle = _kernel32dll.CloseHandle


class PROCESSENTRY32(ctypes.Structure):
    _pack_ = 8
    _fields_ = [
        ("dwSize", ctypes.c_ulong),
        ("cntUsage", ctypes.c_ulong),
        ("th32ProcessID", ctypes.c_ulong),
        ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_uint64)),
        ("th32ModuleID", ctypes.c_ulong),
        ("cntThreads", ctypes.c_ulong),
        ("th32ParentProcessID", ctypes.c_ulong),
        ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", ctypes.c_ulong),
        ("szExeFile", ctypes.c_wchar * MAX_PATH),
    ]


Process32FirstW = _kernel32dll.Process32FirstW
Process32NextW = _kernel32dll.Process32NextW

def parent_tree(pid: int):
    """
    :return: Tree of process parents.
    """
    pe = PROCESSENTRY32()
    pe.dwSize = ctypes.sizeof(PROCESSENTRY32)
    snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, pid)

    all_proc = {}
    try:
        have_record = Process32FirstW(snapshot, ctypes.byref(pe))
        while have_record:
            all_proc[pe.th32ProcessID] = pe.th32ParentProcessID
            have_record = Process32NextW(snapshot, ctypes.byref(pe))
    finally:
        CloseHandle(snapshot)

    curr = pid
    tree = set()
    while curr:
        tree.add(curr)
        curr = all_proc.get(curr)

    return tree
