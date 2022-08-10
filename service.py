import socket
import win32serviceutil
import servicemanager
import win32event
import win32service
import time
import sys

class SMWinservice(win32serviceutil.ServiceFramework):
    '''Base class to create winservice in Python'''

    _svc_name_ = 'pythonService'
    _svc_display_name_ = 'Python Service'
    _svc_description_ = 'Python Service Description'

    @classmethod
    def parse_command_line(cls):
        '''
        ClassMethod to parse the command line
        '''
        win32serviceutil.HandleCommandLine(cls)

    def __init__(self, args):
        '''
        Constructor of the winservice
        '''
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        '''
        Called when the service is asked to stop
        '''
        self.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        '''
        Called when the service is asked to start
        '''
        self.start()
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def start(self):
        self.isrunning = True

    def stop(self):
        self.isrunning = False

    def main(self):
        i = 0
        while self.isrunning:
            servicemanager.LogInfoMsg(str("This isrunning"))
            time.sleep(5)


if __name__ == '__main__':
    import threading
    from multiprocessing.connection import Client
    from multiprocessing.connection import Listener

    s = True
    def ser():
        #while (s):
        with Listener(('localhost', 6000)) as listener:
            conn, addr = listener.accept():
                try:
                    print(conn.recv())
                except EOFError:
                    print("Error")

    t = threading.Thread(target=ser)
    t.start()
    while(True):
        print("dsfsd")
        time.sleep(1)
    s = False
    t.terminate()
    t.join(1)


    quit()
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(SMWinservice)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        SMWinservice.parse_command_line()
