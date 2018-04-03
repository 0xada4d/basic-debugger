import debugger

debugger = debugger.debugger()

#debugger.load("C:\\Windows\\system32\\calc.exe")

pid = raw_input("Enter pid of process to which to attach: ")

debugger.attach(int(pid))
debugger.detach()