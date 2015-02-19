# GTK3 Applications Served on the Web
this code serves up any gtk3 app through a browser (but it started as a way to webhost my interactive matplotlib demo).

you'll need:
* tornado
* pygobject
* gobject (python-gi on aptget)
* some gui components that would get install if you install matplotlib from aptget
* psutl
* gtk3 of course with the broadwayd display backend
* [this](https://github.com/matplotlib/matplotlib/pull/4093) change if you want to display gtk3-backended matplotlib
