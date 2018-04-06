#!/usr/bin/env python3

from ctypes import *
import sys

PAGE_READWRITE = 0x04
PROCESS_ALL_ACCESS = ( 0x000F0000 | 0x00100000 | 0xFFF )
VIRTUAL_MEM = ( 0x1000 | 0x2000 )

kernel32 = windll.kernel32
pid = sys.argv[1]
dll_path = sys.argv[2]
dll_len = len(dll_path)

# Open handle to desired process
process_handle = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, int(pid))

if not process_handle:
    print("Could not open handle to desired process")
    sys.exit(0)

# Allocate space for DLL path
inject_address = kernel32.VirtualAllocEx(process_handle, 0, dll_len, VIRTUAL_MEM, PAGE_READWRITE)

# Write DLL path into allocated space
written = c_int(0)
kernel32.WriteProcessMemory(process_handle, inject_address, dll_path, dll_len, byref(written))

# Resolve the address for LoadLibraryA
kernel32_handle = kernel32.GetModuleHandleA("kernel32.dll")
loadlib_handle = kernel32.GetProcAddress(kernel32_handle, "LoadLibraryA")

# Attempt to create the thread with entry point set to LoadLibraryA
# and a parameter as the DLL path
thread_id = c_ulong(0)
if not kernel32.CreateRemoteThread(process_handle, None, 0, loadlib_handle, inject_address, 0, byref(thread_id)):
    print("Failed to inject the DLL. Exiting..")
    sys.exit(0)

print("Remote thread with ID 0x%08x created." % thread_id.value)