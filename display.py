#this could be in a repo on its own

"""manages GTK3 broadwayd displays
.. and to minimize bash scripting ugggh

usage:
>displynum, port =display.add()
>display.app('gedit',displaynum) #where gedit is a gtk3 app


you may want to set the limits after import
>import display
>display.DisplayLimit=10
"""
import signal
import os
import atexit
import subprocess
from collections import defaultdict
from time import sleep
import socket

import psutil # optionally used

port2display={}
display2port={}

class LimitError(Exception): val=None; pass
class DisplayLimit(LimitError):
    """a limit to the number of displays"""
    val=10;
    pass
class ApplicationLimit(LimitError):
    """a limit to the number of applications per display"""
    val=10
    pass

#should program onappstart onappclose
#todo capture stdio on procs

def get_openport():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',0))
    return s.getsockname()[1]


class sequenceg(): #should have used a generator but cool to...
    #..hack classes
    dc=0
    @staticmethod
    def getdisplay(self):
        self.dc+=1 ;
        return self.dc
    @staticmethod
    def __call__(self):
        return self.getdisplay(self)
sequence=lambda p: sequenceg.__call__(sequenceg)

def friendly_display(port,begin=8000):
    """for wehn you want some 'web' ports"""
    ret= port-begin
    if ret < 0 or port<0:
        raise ValueError('neg values')
    return ret

def display_is_port(port):
    display=port
    return display
#functions need to be one to one mappings bw out and in

#port2display_function
p2df=sequence
port2display_function=p2df #don't use the port2dispaly_func ...
#... in the code

#display_is_port#friendly_display# 
# class keydefaultdict(defaultdict):
    # def __missing__(self, key):
        # if self.default_factory is None:
            # raise KeyError( key )
        # else:
            # ret = self[key] = self.default_factory(key)
            # return ret


class displaydict(defaultdict):
    #adding issues are covvered by add()
    def removemapping(self,display):
        port2display.pop(display2port.pop(display))
    def __delitem__(self, display):
        super(displaydict, self).__delitem__(display)
        self.removemapping(display)
    def pop(self, display):
        super(displaydict, self).pop(display)
        self.removemapping(display)
#procs assoc with each display
running_displays=displaydict(list) 

#lesson learned:
#def add(port,block=True) not a good idea to specify a port
def add(portgetter=get_openport
        ,block=True):#don't see a reason to not block
    remove_zombie_apps(); kill_zombie_displays()
    if len(running_displays)==DisplayLimit.val:
        raise DisplayLimit(DisplayLimit.val)
    port=portgetter() #not safe. need to reserve port
    """runs the html5 part of the app returning the display number
    blocks until the dispaly server is up by default"""
    display=p2df(port)
    if display in running_displays:
        raise KeyError('display server already running')
    else:
        if isport_openable(port) is True:
            raise ValueError("can't get port "+str(port))

    try:
        p=subprocess.Popen(['./start_display.sh'
                           ,str(display),str(port)]
        #,preexec_fn=os.setsid
        )
    except: #todo: problem: broadwayd does not exit if it
      #cant get the port. it gives back:
      #"Can't listen: Error binding to address: Address already in use"
      #dont' p.wait
        raise Exception("couldn't start display")
    #block until 'app' is ready on the port
    if block==True:#todo if port given not openable
        tries=0
        while ( (isport_openable(port) is not True) ):
            tries+=1 ; #sometimes it gets stuck here if
            #rapid requests
            if tries>10: return add(portgetter,block) #not nice
            sleep(.1); continue
    #registrations
    running_displays[display].append(p) #the only reason it's a...
    #...default dict.. do i really need defaultdict?
    port2display[port]=display;
    display2port[display]=port
    # port->display should be 1 to 1 mapping
    if len(display2port) != len(port2display):
        raise Exception('display and port numbers are not 1-to-1')
    return display, port


#what happens when the app spawns a window or another proc?
#on multiple gedits  only the first one is alive
def app(cmd,display,**kwargs):
    """runs a gtk3 prog on display. """
    if (display) not in running_displays:
        raise ValueError('display does not exist')
    remove_zombie_apps()
    if (len(running_displays[display])-1)==ApplicationLimit.val:
        raise ApplicationLimit(ApplicationLimit.val)
    #kwargs['preexec_fn']=os.setpgid
    sp=subprocess.Popen(['./display.sh',cmd,str(display)]
                        ,**kwargs)
    running_displays[display].append(sp)
    return sp


def isport_openable(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('127.0.0.1',port)) #if can bind then not busy
        s.close()
        return False
    except: return True
    # cr=s.connect_ex(('127.0.0.1', port))
    # if cr==0: return True
    # else: return cr


def stop(display,signal=signal.SIGKILL):#signal.SIGINT):
    # when using this with the server.. can't rely on being nice
    # so just kill it
    """stops display and everything running on it"""
    if display not in running_displays:
        raise KeyError('no display #'+str(display)+' to kill')
    #os.killpg(p.pid, signal.SIGTERM)
    proclist= running_displays[display]
    for p in reversed(proclist):
        p.send_signal(signal);
        #p.kill()
        p.wait()
    running_displays.pop(display)
    remove_zombie_apps()


def remove_zombie_apps():
    #the not immediate
    delthese=[]
    for adisplay in running_displays:
        for an,aproc in enumerate(running_displays[adisplay]):
            if an==0:continue  #skip the broadway proc
            if aproc.poll() is None: continue# running
            else: delthese.append( (adisplay,an) )
    for adisplay,an in delthese:
        #in case empty list
        try: running_displays[adisplay].pop(an) #the process...
        # ..will be removed by the garbage collector eventually
        except: pass


def kill_zombie_displays(really=False):#=True makes a problem. idk Y
    if really is not True: return
    for ap in psutil.process_iter():
        try: cmdline = ap.cmdline[0]
        except: continue
        if cmdline == 'broadwayd':
            print 'TTTTTT',cmdline, ap.cmdline[2]
            # index 2 is the port
            if ap.cmdline[2] not in port2display: ap.kill()


def kill_all():
    """kills all display apps on the server forcefully
    ...that it knows about that is."""
    for ad in running_displays.keys():
        stop(ad,signal=signal.SIGKILL)

atexit.register(kill_all)