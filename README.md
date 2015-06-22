# Ainneve, an example game for Evennia

Welcome! The [Evennia](http://www.evennia.com/) community has created Ainneve for you to use as a base to learn from and build off of.  Ainneve currently is an early work in progress. 

The main configuration file is found in
`server/conf/settings.py` (but you don't need to change it to get
started). If you just created this directory, `cd` to this directory
then initialize a new database using

    evennia migrate

To start the server, `cd` to this directory and run

    evennia -i start

This will start the server so that it logs output to the console. Make
sure to create a superuser when asked. By default you can now connect
to your new game using a MUD client on localhost:4000.  You can also
log into the web client by pointing a browser to
http://localhost:8000.

# Getting started

It's highly recommended that you look up Evennia's extensive
documentation found here: https://github.com/evennia/evennia/wiki.

Plenty of beginner's tutorials can be found here:
http://github.com/evennia/evennia/wiki/Tutorials.

# Contributing

Currently the best resource for learning about Ainneve is the original proposal document, https://docs.google.com/document/d/1fu-zYvFytKHGxFHD6_bLQ4FrotAQ0izXuWE_gn8q2Oc/edit?usp=sharing . Soon we'll be moving that information to this repo's wiki. 

To let us know you're interested in helping out visit the [Evennia developer IRC](http://webchat.freenode.net/?channels=evennia&uio=MT1mYWxzZSY5PXRydWUmMTE9MTk1JjEyPXRydWUbb) and the [Ainneve](https://groups.google.com/forum/?fromgroups#!categories/evennia/ainneve) category of the mailing list. 


# License

Ainneve uses the BSD license, the [same as Evennia](https://github.com/evennia/evennia/wiki/Licensing). 