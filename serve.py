from flask import Flask ,redirect, url_for

app = Flask(__name__)

#todo somehow hide the :808x from the user so that



@app.route("/boweb")
def boweb(): #since only one display at a time...
    #.. no problem from multiple hits from the same user
    p=rundisplay()
    h=gethost()
    return redirect('http://'+h+':'+str(p),code=307)

from flask import request
@app.route("/host")
def host(): return (gethost())
from urlparse import urlsplit
def gethost():
    o=urlsplit( 'stub://'+request.headers.get('Host') )
    return o.hostname #, o.port

@app.route("/")
def root():
    return boweb()

if __name__ == "__main__":
    #except: pass
    app.debug = True
    app.run()