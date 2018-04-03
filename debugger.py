from ctypes import *
from debugger_defines import *

# BOOL WINAPI CreateProcessA(
#     LPCSTR lpApplicationName,
#     LPTSTR lpCommandLine,
#     LPSECURITY_ATTRIBUTES lpProcessAttributes,
#     LPSECURITY_ATTRIBUTES lpThreadAttributes,
#     BOOL bInheritHandles,
#     DWORD dwCreationFlags,
#     LPVOID lpEnvironment,
#     LPCTSTR lpCurrentDirectory,
#     LPSTARTUPINFO lpStartupInfo,
#     LPPROCESS_INFORMATION lpProcessInformation
# );

# HANDLE WINAPI OpenProcess(
#   _In_ DWORD dwDesiredAccess,
#   _In_ BOOL  bInheritHandle,
#   _In_ DWORD dwProcessId
# );

kernel32 = windll.kernel32

class debugger():
    def __init__(self):
        self.h_process       = None
        self.pid             = None
        self.debugger_active = False

    def load(self, path_to_exe):
        # dWCreation flag determines how to create the process
        # set creation_flags = CREATE_NEW_CONSOLE if you want too see calc.exe gui
        creation_flags = DEBUG_PROCESS

        # Instantiate structs
        startupinfo = STARTUPINFO()
        process_information = PROCESS_INFORMATION()

        # The following two options allow the started process
        # to be shown as a separate window. This also illustrates
        # how different settings in the STARTUPINFO struct can affect
        # the debuggee.
        startupinfo.dwFlags = 0x1
        startupinfo.wShowWindow = 0x0

        # We then initialize the cb variable in the STARTUPINFO struct
        # which is just the size of the struct itself
        startupinfo.cb = sizeof(startupinfo)

        if kernel32.CreateProcessA(path_to_exe,
                                   None,
                                   None,
                                   None,
                                   None,
                                   creation_flags,
                                   None,
                                   None,
                                   byref(startupinfo),
                                   byref(process_information)):

            print "[*] We have successfully launched the process!"
            print "[*] PID: %d" % process_information.dwProcessId

            self.h_process = self.open_process(process_information.dwProcessID)


        else:
            print "[*] Error: 0x%08x." % kernel32.GetLastError()

    def open_process(self, pid):
        h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS,False,pid)
        return h_process

    def attach(self,pid):
        self.h_process = self.open_process(pid)

        # Attempt to attach to process, if fails exit
        if kernel32.DebugActiveProcess(pid):
            self.debugger_active = True
            self.pid = int(pid)

        else:
            print "[*] Unable to attach to the process."

    def run(self):
        # Now we need to poll the debugee for debug events
        while self.debugger_active == True:
            self.get_debug_event()

    def get_debug_event(self):
        debug_event = DEBUG_EVENT()
        continue_status = DBG_CONTINUE

        if kernel32.WaitForDebugEvent(byref(debug_event), INFINITE):
            #raw_input("Enter to continue..")
            #self.debugger_active = False
            kernel32.ContinueDebugEvent(debug_event.dwProcessId,
                                        debug_event.dwThreadId,
                                        continue_status)

    def detach(self):
        if kernel32.DebugActiveProcessStop(self.pid):
            print "[*] Finished debugging. Exiting..."
            return True
        else:
            print "There was an error."
            return False



