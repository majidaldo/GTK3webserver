from flask import Flask ,redirect, url_for
import subprocess
import os
app = Flask(__name__)

#todo somehow hide the :808x from the user so that
#todo func to remove and kill child procs that closd
running_displays={}

from time import sleep
def rundisplay(display=8888):
    """runs the html5 part of the app returning the port number"""
    try: kill_display(display)
    except: pass
    port = display
    #one  display at a time
    if display in running_displays:
        return port()
    else:
        running_displays[display]=subprocess.Popen(
        ['./display.sh',str(display)]
        ,preexec_fn=os.setsid
        )

    #block until 'app' is ready on the port
    while ( isport_running(port) is not True ): sleep(.1); continue

    return port

import socket
def isport_running(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cr=s.connect_ex(('127.0.0.1', port))
    if cr==0: return True
    else: return cr

import signal
@app.route('/kill')
def kill_display(display=8888):
    p= running_displays[display]
    os.killpg(p.pid, signal.SIGTERM)#p.send_signal(signal.SIGINT);
    p.wait()
    running_displays.pop(display)
    return 'kiling'

@app.route("/boweb")
def boweb(): #since only one display at a time...
    #.. no problem from multiple hits from the same user
    rundisplay()
    return redirect('http://localhost:8888',code=307)

	
@app.route("/")
def hello():
    return boweb()#"Hello World!"

if __name__ == "__main__":
    app.run()