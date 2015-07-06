# Room typeclass
### Flags and Sectors

**Flags** are static attributes that are turned on/off during area building. They are modifiers of room's behavior and are checked by a multitude of things. They are actual room *properties* that can trigger some effects of object's method. As an example, a room flagged as NO_FIGHT, won't allow any offensive action/spell to the occupants.
Codewise, flags are **evennia tags** setted with the command **@flag**. See help for instructions.

####*Think about flags as special attributes that serve to allow or deny some special actions. Standard rooms may be built with no flag at all.*

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
+ **has_road**

#### Forest:

*Desc...*

#### Desert:

*Desc...*

*and so on*