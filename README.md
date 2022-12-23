# Ainneve, an example game for Evennia 
|  main  | develop |
|--------|---------|
| [![Main build Status](https://travis-ci.org/evennia/ainneve.svg?branch=main)](https://travis-ci.org/evennia/ainneve) | [![Develop build Status](https://travis-ci.org/evennia/ainneve.svg?branch=develop)](https://travis-ci.org/evennia/ainneve) |

### Codebase is undergoing major refactoring - please join the ainneve on Discord if you wish to discuss ideas for Ainneve's future.

Welcome! The [Evennia](http://www.evennia.com/) community has created Ainneve for you to use as a base to learn from and build off of.  Ainneve currently is an early work in progress. 

## Getting started

We recommended you look up [Evennia's extensive documentation](https://evennia.com/docs/latest). It has several beginner-level tutorials and a thoroughly documented codebase.

To learn about Ainneve's game systems and world setting, check out [our wiki](https://github.com/evennia/ainneve/wiki).

## Installation

The main configuration file is found in `server/conf/settings.py` - 
but you don't need to change it to get started. All of the necessary settings
come pre-configured

Once you have the ainneve directory, `cd` into it in a shell and install the pip requirements.
(It's recommended you set up a python venv first!)

    pip install -r requirements.txt

> If you have trouble with installing the requirements, please check [Evennia's troubleshooting guide](https://www.evennia.com/docs/latest/Setup/Installation-Troubleshooting.html)

Next, initialize the game in evennia:

    evennia migrate

To start the server, make sure you're in the ainneve directory and run:

    evennia -i start

This will start the server so that it logs output to the console. Make
sure to create a superuser when asked. By default you can now connect
to your new game using a MUD client or the built-in website - telnet at localhost:4000 or 127.0.0.1:4000
or your web browser at http://localhost:4001.

## Current To-Do (feel free to contribute!)

In flux: check out the [design doc](design_doc.md) for an idea of the project's plans.

(To-do: write a to-do list)

## Contributing

If you're looking for what tasks we need help with, look at our [current open issues](https://github.com/evennia/ainneve/issues). (NOTE: these need to be reviewed, so they may not be current!)

To let us know you're interested in helping out, you can also visit the #ainneve channel in the [Evennia Discord](https://discord.gg/2aNJQGfx)

Please submit pull requests as feature branches rather than from your main branch -- see https://github.com/evennia/evennia/wiki/Version-Control#making-a-work-branch. 

# License

Ainneve uses the BSD license, the [same as Evennia](https://github.com/evennia/evennia/wiki/Licensing).

> Legacy note: Originally, our game was based on [Open Adventure](http://www.geekguild.com/openadventure), copyright 2014 Kyle Mecklem and released under the Creative Commons Attribution [CC-by-SA license](https://creativecommons.org/licenses/by-sa/4.0/).  It is no longer.
