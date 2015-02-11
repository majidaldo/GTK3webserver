"""manages GTK3 broadwayd displays"""

import os
import subprocess

running_displays={}
display2port={}

from time import sleep
def run(display,block=True):
    """runs the html5 part of the app returning the port number"""
    port = display
    #one  display at a time
    if display in running_displays:
        raise ValueError('display server already running')
    else:
        running_displays[display]=subprocess.Popen(
        ['./display.sh',str(display)]
        ,preexec_fn=os.setsid
        )

    #block until 'app' is ready on the port
    if block==True:
        while ( isport_running(port) is not True ):
            sleep(.1); continue
    display2port[display]=port
    return port

def run_app(cmd,display):

import socket
def isport_running(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cr=s.connect_ex(('127.0.0.1', port))
    if cr==0: return True
    else: return cr

import signal
def kill(display):
    p= running_displays[display]
    os.killpg(p.pid, signal.SIGTERM)#p.send_signal(signal.SIGINT);
    p.wait()
    running_displays.pop(display)
    return 'killed display'+str(display)

def kill_all():
    """kills all broadways on the server forecefully"""
    subprocess.call(['pkill','display.sh'])
    subprocess.call(['pkill','runon_display.sh'])
    subprocess.call(['pkill','broadwayd'])