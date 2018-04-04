from debugger_defines import *

# 1) CreateProcessA creates a process with pid
# 2) OpenProcess creates a handle to a process with pid
# 3) DebugActiveProcess allows us to debug the process with handle above
# 4) WaitForDebugEvent is a loop listening for breakpoints, etc
# 5) CreateToolhelp32Snapshot grabs a list of the current active threads
# 6) We then loop through the list of threads..
#    And if their owner pid matches self.pid, we add them to a list
# 7) We open a handle to each thread in the list with OpenThread
# 8) GetThreadContext gets the state of the registers for each thread

import sys
import time

kernel32 = windll.kernel32


class debugger():

    def __init__(self):
        self.h_process = None
        self.pid = None
        self.debugger_active = False
        self.h_thread = None
        self.context = None
        self.breakpoints = {}
        self.first_breakpoint = True
        self.hardware_breakpoints = {}

        # Here let's determine and store
        # the default page size for the system
        # determine the system page size.
        system_info = SYSTEM_INFO()
        kernel32.GetSystemInfo(byref(system_info))
        self.page_size = system_info.dwPageSize

        # TODO: test
        self.guarded_pages = []
        self.memory_breakpoints = {}

    def load(self, path_to_exe):

        # dwCreation flag determines how to create the process
        # set creation_flags = CREATE_NEW_CONSOLE if you want
        # to see the calculator GUI
        creation_flags = DEBUG_PROCESS

        # instantiate the structs
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
            print "[*] The Process ID I have is: %d" % \
                  process_information.dwProcessId
            self.pid = process_information.dwProcessId
            self.h_process = self.open_process(self, process_information.dwProcessId)
            self.debugger_active = True
        else:
            print "[*] Error with error code %d." % kernel32.GetLastError()

    def open_process(self, pid):

        # PROCESS_ALL_ACCESS = 0x0x001F0FFF
        h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)

        return h_process

    def attach(self, pid):

        self.h_process = self.open_process(pid)

        # We attempt to attach to the process
        # if this fails we exit the call
        if kernel32.DebugActiveProcess(pid):
            self.debugger_active = True
            self.pid = int(pid)

        else:
            print "[*] Unable to attach to the process."

    def run(self):

        # Now we have to poll the debuggee for
        # debugging events
        while self.debugger_active == True:
            self.get_debug_event()

    def get_debug_event(self):

        debug_event = DEBUG_EVENT()
        continue_status = DBG_CONTINUE

        if kernel32.WaitForDebugEvent(byref(debug_event), 100):
            # grab various information with regards to the current exception.
            self.h_thread = self.open_thread(debug_event.dwThreadId)
            self.context = self.get_thread_context(self.h_thread)
            self.debug_event = debug_event

            kernel32.ContinueDebugEvent(debug_event.dwProcessId, debug_event.dwThreadId, continue_status)

    def detach(self):

        if kernel32.DebugActiveProcessStop(self.pid):
            print "[*] Finished debugging. Exiting..."
            return True
        else:
            print "There was an error"
            return False

    def open_thread(self, thread_id):

        # Open a handle to a thread so we can access it
        h_thread = kernel32.OpenThread(THREAD_ALL_ACCESS, None, thread_id)

        if h_thread is not None:
            return h_thread
        else:
            print "[*] Could not obtain a valid thread handle."
            return False

    def enumerate_threads(self):

        thread_entry = THREADENTRY32()
        thread_list = []
        # Get a list of the current threads in the processor
        snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, self.pid)

        if snapshot is not None:

            # You have to set the size of the struct
            # or the call will fail
            thread_entry.dwSize = sizeof(thread_entry)

            # Begin looping through the threads
            success = kernel32.Thread32First(snapshot, byref(thread_entry))

            while success:
                if thread_entry.th32OwnerProcessID == self.pid:
                    thread_list.append(thread_entry.th32ThreadID)
                # Go to next thread in list
                success = kernel32.Thread32Next(snapshot, byref(thread_entry))

            # No need to explain this call, it closes handles
            # so that we don't leak them.
            kernel32.CloseHandle(snapshot)
            return thread_list
        else:
            return False

    def get_thread_context(self, thread_id=None, h_thread=None):

        context = CONTEXT()
        context.ContextFlags = CONTEXT_FULL | CONTEXT_DEBUG_REGISTERS

        # Obtain a handle to the thread
        if h_thread is None:
            self.h_thread = self.open_thread(thread_id)

        # Populate CONTEXT struct which contains cpu registor information
        if kernel32.GetThreadContext(self.h_thread, byref(context)):

            return context
        else:
            return False

