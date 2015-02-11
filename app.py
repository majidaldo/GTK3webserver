"""encaplulate the 'pure' matplotlib script with 'real' gtk3"""

from gi.repository import Gtk

from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams['toolbar'] = 'None'
import bo

myfirstwindow = Gtk.Window()

sw = Gtk.ScrolledWindow()
#myfirstwindow.set_default_size(800, 400)
myfirstwindow.add(sw)

bo.main()
#plt.plot([1,2,3]);#plt.show()

canvas = FigureCanvas(plt.gcf())
canvas.set_size_request(400,800)
sw.add_with_viewport(canvas)

myfirstwindow.connect("delete-event", Gtk.main_quit)
myfirstwindow.show_all()
Gtk.main()