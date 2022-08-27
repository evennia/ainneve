# Ainneve, an example game for Evennia 
| master | develop |
|--------|---------|
| [![Master build Status](https://travis-ci.org/evennia/ainneve.svg?branch=master)](https://travis-ci.org/evennia/ainneve) | [![Develop build Status](https://travis-ci.org/evennia/ainneve.svg?branch=develop)](https://travis-ci.org/evennia/ainneve) |

# Codebase is undergoing major refactoring - please join the ainneve on Discord if you wish to discuss ideas for Ainneve's future.

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

# Current To-Do (feel free to contribute!):

evaluate what we'd need to remove and replace with contribs

get a simple MUD-like combat system working (probably including removing the current character classes and builds).

customize the game's homepage to add this todo list, contact information (like Discord), etc...maybe a nice CSS theme?

# Design Goals:

Simple systems to show off Evennia's many features, while still being fun to play (emphasis on fun)

Use Evennia Contribs whenever it makes sense

The online consensus at the time was to make Ainneve's theme something kinda like:  "Magic Dungeon For Sale"

Simple.  Lighthearted, and bonus points for puns.

A stereotypical town with a bar, a smithy, an arena, and Ye-Olde-Magic shop... Next door to a "mega-dungeon"

The dungeon would proc-gen every time it became empty.


# Game System:

To sum up our current game system:

3 stats (names still being decided on)

* Strength
* Cunning
* Will

3 "resource" stats:
* Health
* Mana
* Stamina

6 classes to start with (names still being decided on)
* Warrior [ Primary: Strength, Secondary: Cunning  ]
* Paladin [ Primary: Strength, Secondary: Will     ]
* Rogue   [ Primary: Cunning,  Secondary: Strength ]
* Bard    [ Primary: Cunning,  Secondary: Will     ]
* Shaman  [ Primary: Will,     Secondary: Strength ]
* Wizard  [ Primary: Will,     Secondary: Cunning  ]

classes can be swapped around, not permanent, this will be done at a "trainer" NPC.

Each class would give you some unique abilities, each ability has a possible warmup and a cooldown timer

2d6 vrs a target number (6? 7?) is a typical roll, modified +/-

Races give a +1  to a couple of rolls

Armor reduces damage

Rings of protection type things could add to your defense target number.


# Getting started

We recommended you look up Evennia's extensive
documentation found here: https://github.com/evennia/evennia/wiki.

Plenty of beginner's tutorials can be found here:
http://github.com/evennia/evennia/wiki/Tutorials.

To learn about Ainneve's game systems and world setting, check out [our wiki](https://github.com/evennia/ainneve/wiki).

# Contributing

If you're looking for what tasks we need help with, look at our [current open issues](https://github.com/evennia/ainneve/issues).

To let us know you're interested in helping out visit the [Evennia Discord](https://discord.gg/2aNJQGfx).

Please submit pull requests as feature branches rather than from your master -- see https://github.com/evennia/evennia/wiki/Version-Control#making-a-work-branch. 


# License

Ainneve uses the BSD license, the [same as Evennia](https://github.com/evennia/evennia/wiki/Licensing).

Originally, our game was based on [Open Adventure](http://www.geekguild.com/openadventure), copyright 2014 Kyle Mecklem and released under the Creative Commons Attribution [CC-by-SA license](https://creativecommons.org/licenses/by-sa/4.0/).  It is no longer.
