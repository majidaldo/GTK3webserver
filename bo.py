from __future__ import division
from __future__ import print_function
import numpy as np
import matplotlib
matplotlib.rcParams['toolbar'] = 'None'
matplotlib.rcParams['figure.figsize'] = 14, 5
matplotlib.use("GTK3Cairo")
import matplotlib.pyplot as pl

pl.ion()#ioff()#.ion()

from time import sleep

""" bayesian optimizer game  """


# Define the kernel
def kernel(a, b):
    """ GP squared exponential kernel """
    kernelParameter = 0.1
    sqdist = np.sum(a**2,1).reshape(-1,1) + np.sum(b**2,1) - 2*np.dot(a, b.T)
    return np.exp(-.5 * (1/kernelParameter) * sqdist)

N = 50         # number of test points.
sn = 0#.05    # noise variance.

# points we're going to make predictions at.
Xtest = np.linspace(-5, 5, N).reshape(-1,1)


from numpy import random
import scipy
from scipy import interpolate
def randomfunction(N=N,seed=None):
    """makes a smooth squiggly function """
    np.random.seed(seed=seed)
    #number of pts to go through  ~num of knots
    nc=np.random.choice(12)+7 #from 7 to 19. dont add too many pts
    #with these vales
    ys=np.random.randn(nc)
    #sprinkle it in the domain
    xis=np.random.choice(N, size=nc, replace=False)
    xis.sort();
    #dont want edges flyhing off or diving down
    ys[0]=ys[1]; 
    ys[-1]=ys[-2]
    xis[0]=0
    xis[-1]=N-1
    xs=Xtest[xis].reshape(nc) #get rid of a dim
    spl= scipy.interpolate.InterpolatedUnivariateSpline( xs,ys
    )#,s=.1 )
    return spl(Xtest[:,0])

def init_randomfuction(**kwargs):
    global yall, ixmax #sinner!
    yall=randomfunction(**kwargs)
    ixmax=np.argmax(yall)

def init_u(etav=.01):#utility funciton
    global eta
    eta=etav

def init_compute():
    global computedis
    computedis=[]

def compute(ipt):#index of point
    global K, L, Lk, mu, K_, s, y 
    if ipt in computedis: return    
    if not 0<=ipt<N: raise ValueError('index not in range')
    computedis.append(ipt)
    
    y= yall[computedis]
    X=Xtest[computedis]
    K = kernel(X, X)
    L = np.linalg.cholesky(K + sn*np.eye(len(computedis)))
    # compute the mean at our test points.
    Lk = np.linalg.solve(L, kernel(X, Xtest))
    mu = np.dot(Lk.T, np.linalg.solve(L, y))

    # compute the variance at our test points.
    K_ = kernel(Xtest, Xtest)
    s2 = np.diag(K_) - np.sum(Lk**2, axis=0)
    s = np.sqrt(s2)

#initial point.. which shouldn't be at the max
def init_initpt():
    global ip
    ip=np.random.choice(N)
    while(ismax(ip) == True):
        ip=np.random.choice(N)
    compute(ip)

import scipy as sp
from scipy import stats
def PI(ix,ixp): #xp is 'encumbent' ..using indices
    #global eta
    #eta=.05 #doesn't make much diff
    return sp.stats.norm.cdf( (mu[ix]-yall[ixp]-eta)/(s[ix]+1e-6)  )
def maxiPI():
    global ixp
    ixp= computedis[np.argmax(yall[computedis])]
    PIs=(  PI(None, ixp))[0] #toss a dim.
    PIs[computedis]=-1e-6 #if i know it then no improvement duh
    #PIl.append(PIs)
    return np.argmax(PIs)
#see
#"A Tutorial on Bayesian Optimization of
#Expensive Cost Functions, with Application to
#Active User Modeling and Hierarchical
#Reinforcement Learning"
#by Eric Brochu, Vlad M. Cora and Nando de Freitas
#for an overview of these utility funcitons
def EI(ix,ixp): #xp is 'encumbent' ..using indices
    mu_y_eta=mu[ix]-yall[ixp]-eta
    Z=mu_y_eta/(s[ix]+1e-6)
    return mu_y_eta*sp.stats.norm.cdf(Z) + s[ix]*sp.stats.norm.pdf(Z)
def maxiEI():
    global ixp
    ixp= computedis[np.argmax(yall[computedis])]
    PIs=(  PI(None, ixp))[0] #toss a dim.
    PIs[computedis]=-1e-6 #if i know it then no improvement duh
    #PIl.append(PIs)
    return np.argmax(PIs)


def ismax(ipt,tol=.02):
    """lets you know if a point is max"""
    #if not 0<=ipt<=N: raise ValueError('index not in range')
    #if ipt in computedis: return
    #if ipt==ixmax: return True
    tol=tol*(Xtest[-1][0]-Xtest[0][0])
    if Xtest[ixmax]-tol<Xtest[ipt]<=Xtest[ixmax]+tol: #equals is important!..
                                    #...what if tol ~=0 ?
        return True
    else:
        compute(ipt) #this shouldnt be here
    return False

def init_all(kwargs):
    kwargs.setdefault('rf',{})
    kwargs.setdefault('compute',{})
    kwargs.setdefault('u',{})
    kwargs.setdefault('ip',{})
    init_randomfuction(**kwargs['rf'])
    init_compute(**kwargs['compute'])
    init_u(**kwargs['u'])
    init_initpt(**kwargs['ip'])

def play(player):#,initkw={}):
    """returns number of guesses"""
    #global PIl
    #PIl=[]
    #init_all(initkw)
    n=0
    while True:
        guess=ismax(player.guess())
        n+=1;
        if n==N: return None #todo raise exception
        if guess==True: return n
        else: continue


	
def game():
    
    pt=plttxt()    
    printer=lambda txt:pt.printt(txt)

     
    scores={'h':0,'c':0} #well...number of tries
    
    for i in xrange(999):
        stt=np.random.randint(1,123456789)
        
        cp=puter()
        hp=human(printer=printer)      
        printer('Try, human.')
        init_all({'rf':{'seed':stt}})
        nh=play(hp)
        
        init_all({'rf':{'seed':stt}})
        nc=play(cp)

        pl.plot([Xtest[ixmax]],[np.max(yall)],'r^',ms=12)
        if nh<nc:
            w='You win this time, human!'
            printer(w+' '
            +'You took '+str(nh)+' tries while the computer took '+str(nc)
            +'. (click to continue)')
        elif nh>nc:
            w='Computer won!'
            printer(w+' '
            +'You took '+str(nh)+' tries while the computer took '+str(nc)
            +'. (click to continue)')
        else:# nh==nc:
            printer('Tie! You both took '+str(nh)+' tries. (click to continue)')
        
        pl.plot(Xtest[cp.my_guesses],yall[cp.my_guesses],'gx',ms=8,mew=1)
        pl.plot(Xtest,yall,c='black')
        while ( (pl.waitforbuttonpress(timeout=-1) !=False) ): #false is mouse
            sleep(.1); continue
        scores['h']+=nh
        scores['c']+=nc
        
        
        if   scores['h']<scores['c']: ptr=' <-- '
        elif scores['h']>scores['c']: ptr=' --> '
        else:                         ptr=' <-> '
        printer('Avg. num. of tries after '+str(1+i)+' games: '\
                +'You= '+       format((scores['h'])/float(i+1),'.1f')\
                +ptr
                +' Computer= '+format((scores['c'])/float(i+1),'.1f')\
                +' (click to continue)')
        while ( (pl.waitforbuttonpress(timeout=-1) !=False) ): #false is mouse
            sleep(.1); continue


class player(object):
    def __init__(self):
        self.my_guesses=[]
        

class puter(player):
    
    def guess(self):
        gs=maxiEI()#maxiPI() #didn't see much differece
        self.my_guesses.append(gs)
        return self.my_guesses[-1]


class plttxt(object):
    
    def __init__(self,fig='current'):
        if fig == 'current': self.fig=pl.gcf()
        else: self.fig=fig
    
    def printt(self,txt):
        self.clear()
        self.txt=txt
        self.fig.text(.15,0.02,txt)
        pl.draw()
    def clear(self):
        #assuming it was the last one in
        try: self.fig.texts.remove(self.fig.texts[-1])
        except: pass        
        pl.draw()


class human(player):
    #todo plt thin vertical lines
    def __init__(self,printer=print):
        super(human, self).__init__()
        self.fig = pl.gcf();
        self.fig.patch.set_facecolor('white')
        self.printer=printer
        pl.clf()
        self.pcid = self.fig.canvas.mpl_connect('button_press_event' 
                , lambda event: self.guessclick(event))
        
    def setupplay(self):
        pl.axis('off')
        pl.xlim((min(Xtest)-.5,max(Xtest)+.5))
        pl.title("Guess where the max is")
        pl.plot(Xtest[ip],[yall[ip]],'bo')
        mx=max(yall)
        mn=min(yall)
        m=np.random.uniform(.5,1) #plot margin.players shouldn't know when ..
        #..they are close to the max
        mx=max(yall)
        mn=min(yall)
        pl.ylim((mn-m*(-mn+mx)
                ,mx+m*(-mn+mx) )) #+some margin
        for apt in Xtest: pl.plot([apt,apt],[mn-m*(-mn+mx),mx+m*(-mn+mx)]
            ,color='.2',lw=.2)
        pl.tight_layout()
        pl.draw()
        return

    def guess(self):
        if len(self.my_guesses)==0: #sigh hacky
            self.setupplay();
        while ( pl.waitforbuttonpress(timeout=-1) ==False ): #false is mouse
            try:
                if ( self.guesschk(self.last_click)==True ): break
            except: pass
            else: sleep(.1); continue
        igs=self.last_click
        self.my_guesses.append(igs)
        pl.plot([Xtest[igs]],[yall[igs]],'bo'); pl.draw()
        return self.my_guesses[-1]

    def guessclick(self,event):
        try: self.last_click=np.abs(Xtest - event.xdata).argmin()
        except:
            self.last_click=None
            return None
        return self.last_click
    
    def guesschk(self,ig):
        #g=Xtest[ig]
        if ig== ip:#todo except no coorrds (nonetype)
            self.printer('initial guess given')
            return False
        if ig in self.my_guesses:
            self.printer('already guessed')
            return False
        if (min(Xtest)<=Xtest[ig]<=max(Xtest))==False: #never comes here...
            self.printer('not in range') #..but i left these two lines
            return False
        #finally
        self.printer('')
        return True


def main():
    import sys
    def switch_closed(event):
        sys.exit(0)
		
    cf=pl.gcf(); 
    cf.canvas.mpl_connect('close_event', switch_closed)
    game()
	

if __name__=='__main__':
    main()

