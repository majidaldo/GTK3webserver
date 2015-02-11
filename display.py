"""manages GTK3 broadwayd displays
.. and to minimize bash scripting ugggh

usage:
#display.add(8080)
display.app('gedit',8080) #where gedit is a gtk3 app

"""

import os
import subprocess
from collections import defaultdict

def display_is_port(display):
    port=display
    return port
d2pf=display_is_port
class keydefaultdict(defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError( key )
        else:
            ret = self[key] = self.default_factory(key)
            return ret
display2port=keydefaultdict(d2pf)

#procs assoc with each display
running_displays=defaultdict(list) 

from time import sleep
def add(display,block=True):
    remove_zombies()
    """runs the html5 part of the app returning the port number
    blocks until the dispaly server is up by default"""
    port=display2port.default_factory(display)
    if display in running_displays:
        raise ValueError('display server already running')
    else:
        if isport_running(port) is True:
            raise Exception("can't get port "+str(port))
        running_displays[display].append(subprocess.Popen(
        ['./display.sh'
        ,str(display),str(port)]
        #,preexec_fn=os.setsid
        ))

    #block until 'app' is ready on the port
    if block==True:
        while ( isport_running(port) is not True ):
            sleep(.1); continue
    return display2port[display]

def remove_zombies():
    delthese=[]
    for adisplay in running_displays:
        for an,aproc in enumerate(running_displays[adisplay]):
            if aproc.poll() is None: continue# running
            else: delthese.append( (adisplay,an) )
    for adisplay,an in delthese:
        running_displays[adisplay].pop(an)

def app(cmd,display,**kwargs):
    """runs a gtk3 prog on display. if the display is not
    running it will create a display"""
    remove_zombies()
    if display not in running_displays:
        add(display)
    #    raise ValueError('display does not exist')
    
    #cmd_args=list(cmd_args)
    #kwargs['preexec_fn']=os.setpgid
    sp=subprocess.Popen(['./runon_display.sh',cmd,str(display)]
                        ,**kwargs)
    running_displays[display].append(sp)
    return sp

import socket
def isport_running(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cr=s.connect_ex(('127.0.0.1', port))
    if cr==0: return True
    else: return cr

import signal
def stop(display,signal=signal.SIGINT):
    """stops display and everything running on it"""
    if display not in running_displays:
        raise ValueError('no display #'+str(display)+'to kill')
    #os.killpg(p.pid, signal.SIGTERM)
    proclist= running_displays[display]
    for p in reversed(proclist):
        p.send_signal(signal);
        #p.kill()
        p.wait()
    running_displays.pop(display)
    remove_zombies()

def kill_all():
    """kills all display apps on the server forecefully"""
    for ad in running_displays.keys():
        stop(ad,signal=signal.SIGKILL)