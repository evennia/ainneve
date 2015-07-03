# Room typeclass
### Flags and Sectors

**Flags** are static attributes that are turned on/off during area building. They are modifiers of room's behavior and are checked by a multitude of things. They are actual room *properties* that can trigger some effects of object's method. As an example, a room flagged as NO_FIGHT, won't allow any offensive action/spell to the occupants.
Codewise, flags are coded as a single dictionary where key is the actual flag name and the value is a boolean (*True* or *False*) and can be checked with the flag() method.

**Sectors** are room classes that inheritate from the base room typeclass. They describe the room *typology* (forest, desert, urban, etc) and have they own default attributes and methods.

### List of flags and descriptions
#### FLAG {description} <default value\>

+ IS_INDOOR {the room is a closed space} <False\>
+ IS_DARK {artificial light needed for *return_appearance* to work} <False\>
+ IS_SAFE {aggressive actions not permitted} <False\>
+ HAS_ROAD {a road or path is present} <False\>
+ NO_MAGIC {no spell can be casted} <False\>
+ NO_TELEPORT {no teleport action allowed from or to this room} <False\>
+ NO_SUMMON {occupants can't be summoned **from** this room} <False\>
+ IS_SILENT {communication channels won't work} <False\>
+ NO_RANGE {no range combat permitted, only melee} <False\>
+ MAX_PC {if True, checks *self.db.max_ch* value and allows only a defined number of characters to enter the room} <False\>
+ IS_WATER {the room floor is a water surface} <False\>
+ IS_AIR {the room has no floor} <False\>
+ NO_QUIT {players can't quit from this room} <False\>

### List of sector classes and brief descriptions (or flag layout)

+ Urban
+ Forest
+ Desert
+ Mountain
+ Water
+ Air
+ House
+ Shop
+ Building

#### Urban:

Urban rooms are typical city/village transient rooms. They usually have a road or a path and they are not indoor rooms. A good flag scheme could be the following:
```python
self.db.flags = {
    IS_INDOOR:False,
    IS_DARK:False,
    IS_SAFE:False,
    HAS_ROAD:True,
    NO_MAGIC:False,
    NO_TELEPORT:False,
    NO_SUMMON:False,
    IS_SILENT:False,
    NO_RANGE:False,
    MAX_PC:20,
    IS_WATER:False,
    IS_AIR:False,
    NO_QUIT:False,
    }
```

#### Forest:

*Desc...*

#### Desert:

*Desc...*

*and so on*