from flask import Flask ,redirect, url_for
import subprocess
app = Flask(__name__)

#todo somehow hide the :808x from the user so that
#todo func to remove and kill child procs that closd
running_displays={}
import socket
def rundisplay(display=0):
    """runs the html5 part of the app returning the port number"""
    port = 8080+display
    #one  display at a time
    if display in running_displays:
        return port()
    else:
        running_displays[display]=subprocess.Popen(
		['./display.sh',str(display)])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #block until 'app' is ready on the port
    while (0 != s.connect_ex(('127.0.0.1', port))): continue
    
    return port

def isdisplay_running(display):

@app.route("/boweb")
def boweb():
    print rundisplay() #since only one display at a time...
    #.. no problem from multiple hits from the same user
    print 'asdfdsfsf'
    return redirect('http://localhost:8080',code=307)

	
@app.route("/")
def hello():
    return boweb()#"Hello World!"

if __name__ == "__main__":
    app.run()