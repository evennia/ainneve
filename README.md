# Ainneve, an example game for Evennia 
| master | develop |
|--------|---------|
| [![Master build Status](https://travis-ci.org/evennia/ainneve.svg?branch=master)](https://travis-ci.org/evennia/ainneve) | [![Develop build Status](https://travis-ci.org/evennia/ainneve.svg?branch=develop)](https://travis-ci.org/evennia/ainneve) |

# Codebase is undergoing major refactoring - please join #ainneve on Freenode if you wish to discuss ideas for Ainneve's future direction.

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

We recommended you look up Evennia's extensive
documentation found here: https://github.com/evennia/evennia/wiki.

Plenty of beginner's tutorials can be found here:
http://github.com/evennia/evennia/wiki/Tutorials.

To learn about Ainneve's game systems and world setting, check out [our wiki](https://github.com/evennia/ainneve/wiki).

# Contributing

If you're looking for what tasks we need help with, look at our [current open issues](https://github.com/evennia/ainneve/issues).

To let us know you're interested in helping out visit the [Evennia developer IRC](http://webchat.freenode.net/?channels=evennia&uio=MT1mYWxzZSY5PXRydWUmMTE9MTk1JjEyPXRydWUbb) and the [Ainneve](https://groups.google.com/forum/?fromgroups#!categories/evennia/ainneve) category of the mailing list. 

Please submit pull requests as feature branches rather than from your master -- see https://github.com/evennia/evennia/wiki/Version-Control#making-a-work-branch. 


# License

Ainneve uses the BSD license, the [same as Evennia](https://github.com/evennia/evennia/wiki/Licensing).

Our game rules use [Open Adventure](http://www.geekguild.com/openadventure), copyright 2014 Kyle Mecklem and released under the Creative Commons Attribution [CC-by-SA license](https://creativecommons.org/licenses/by-sa/4.0/).
