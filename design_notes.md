# Ainneve Game Design

A game made using simple systems which show off Evennia's many features - especially the available contribs - while still being fun to play. (Emphasis on fun).

*(This is an initial sketch of what's been suggested so far, with some gaps noted via questions you can answer.)*

## Setting and World

- "Magic Dungeon for Sale"
	- Light-hearted fantasy theme.
	- Bonus points for puns.
- The main hub of the game is a stereotypical sword & sorcery town. POI in town include:
	- *IMPLEMENTATION NOTE* - Use the XYZGrid contrib
	- What notable NPCs should be at these locations or wandering the town?
  - A bar/pub/tavern
		- What eating/drinking mechanics should be implemented to support this?
	- A smithy
		- Is this a shop? A crafting station? Both?
		- Smithies often act as a repair hub. Do armor/weapons have durability and take damage with use?
	- An arena
		- PvP, PvE, or both?
	- A shop. "Ye Olde Magick Shoppe"
- A procedurally generated dungeon, which resets whenever it empties.
	- *IMPLEMENTATION NOTE* - Use the wilderness contrib
	- Global dungeon or instanced for parties?
	- Source of gear, treasure, or both?
- The Overworld
	- What do you do here?

## Characters
- Six planned classes (names pending), with major/minor stat focuses:
	- "Warrior": Strength/Cunning
		- special ability: combat specialist?
	- "Paladin": Strength/Will
		- special ability: defense and support?
	- "Rogue": Cunning/Strength
		- special ability: stealth?
	- "Bard": Cunning/Will
		- special ability: ?
	- "Shaman": Will/Strength
		- special ability: ?
	- "Wizard": Will/Cunning
		- special ability: spells?
	- Classes can be swapped at will at a trainer NPC
- Progression
	- Gear vs Attribute progression?
		- Gear progression is when you improve your character by getting better gear
		- Attribute progression is when you improve your character by increasing character stat numbers
		- Both can and often are gated by character level
- Skills?
	- *IMPLEMENTATION NOTE* - If included, use the Traits contrib

## Mechanics

- Three-stat system, with three "resource" pools
	- *IMPLEMENTATION NOTE* - Use the Traits contrib
	- Stats: Strength, Cunning, Will
	- Resources: Health, Mana, Stamina
	- Player Set Information: Aggression, Block Position, Parry Position
- NOT turn-based combat
	- *Notes from friar are at the end of the section.  All values subject to future tweaking for game balance/fun-ness*
	- Dice rolls are standardized as 2d6+stat
		- *IMPLEMENTATION NOTE* - Make this a single point-of-access method which passes in the stat.
	- Agression:
		- Defensive (x1/2), Normal (x1), or Aggressive (x1.5)
		- Increases damage dealt, delay, and stamina costs by Aggression factor
		- Changing Aggression will incur an attack delay.
	- Weapon stats
		- Min and Max Weapon Range (melee/short/medium/long), Polearms could have Min: melee, Max: Short
		- Physical Damage Range (1 for Unarmed, 1-3 pt for a dagger, 2-4 for a longsword, 3-8 for a battleaxe/polearm)
		- Stun Damage Duration (An amount of delay to add to the Target's action delay)
		- Base Stamina Cost to attack with it (Fist: 2 points, Daggers: 2 point, longsword: 4pts, Battleaxe: 6pts, Polearms/Bow: 8 pts)
		- Base Delay Duration (polearms take longer to recover after an attack than daggers, for example)
		- Optional extra delay to reload (bows/crossbows, for example)
		- It can be thrown effectively: Boolean
	- Armor stats
		- Heavier armor adds a dodge penalty to your defenses (-1 dodge for light armor, -2 medium, -3 heavy)
		- Heavier armor adds an Extra Stamina cost to all actions (1 stamina for light, 2 for medium, 3 for heavy)
		- Acts as Damage reduction when hit (ex: Light is 2 points of Physical reduction, Medium is 4 points, Heavy is 6 points)
		- Heavier armor adds to the delay modifier of all of the wearers actions (Light is 1.1, Medium is 1.2, Heavy is 1.3)
		- Exotic armors may affect the other non-physical types of damage
	- Target zones
		- Combatants can set their defense and attack zones as an XY coordinate, left/center/right, low/mid/high
			- Changing attack zone is a free action
			- Changing defense zone incurs an attack delay
		- Attacks landing on your defended zone procs a defense auto-action, which if successful gives a counter-attack bonus.
			- Should there be any effect for landing "near" a defended zone? e.g. if you have left/mid and someone aims for left/high
		- Attacks landing outside the defense zones successfully land on armor in the strike zone
	- Combat movement
		- While in combat, you can "advance" or "retreat" to/from an opponent to change your active range
		- Advancing and retreating incur movement delays
			- Ahould this be separate from the attack delay, or should moving prevent attacks/attacking prevent movement?
			- Movement and Attacking are separate delays, but Movement and Casting spells should probably be mutually exclusive
	- Overall Attack Algorithm:
		- Check to see if the attacker is still counting down a previous attack delay
			- if so, send an error message about it and early exit.
		- If this is a Throw attack, check the Throwable flag on the Attackers Weapon
			- if not throwable, set the Base Physical Damage Range to 1-2 and the Base Stamina Cost to 4.
		- Check to see if the attacker has enough Stamina for the attack, based on weapon/spell, modified for their aggression and armor.
			- if not early exit with an error message
		- Check to see if the target is within the attackers weapon range (both melee or ranged attacks)
			- If not early exit with an error message
		- Set the Attackers delay to the Weapon's delay time modified for Armor/Aggression
		- Subtract the Weapon/Armor/Aggression modified Stamina cost from the Attacker
		- Check to see if the target is using a shield and their Block zone matches the Attacker's target zone
			- if so, set Blocked 
		- Check if target is wielding something that can parry, and if their Parry zone matches the Attacker's target zone.
			- if so, set Parried
		- If Blocked or Parried 
			- Subtract a small amount of Stamina from the target for the Block/Parry
			- Check to see if the range to the target is melee and the attackers weapon Minimum allows melee
				- Add extra time to the attackers delay for being melee Blocked/Parried
				- if Parried, Set the target's Parry Bonus to +2 against this attacker
			- early exit
		- if melee, Roll Attackers (2d6+Strength+Agression+Bonuses) versus (2d6 + Targets Cunning + Buffs - Target's Armor Dodge penalty)
		- if ranged, Roll Attackers (2d6+Cunning+Aggression+Bonuses) versus (5 + Target's size modifier + Buffs +2/+4 for medium/long range)
		- if spell, Roll Attackers (2d6+Will+Aggression+Bonuses) versus (4 + Target's Will + Buffs)
		- if melee or ranged and this roll exceeds the target number:
			- generate a damage value from the Attackers weapon's base damage range
			- Add Attackers Strength for Melee/Thrown attacks, Cunning for Ranged weapon attacks
			- multiply the result by the Attackers Agression factor (round up)
			- Subtract off the Target's armor, if any, and apply the remainder to the Targets Health
				- if the target dies, perform corpse operations.
		- if spell, and this roll exceeds the target number:
			- call that spell's custom code.

- Crafting weapons/armor/potions as a counter-option to buying them.
	- *IMPLEMENTATION NOTE* - Use the crafting contrib
- Containers
	- If we want them, they need to be implemented, including custom get/put/drop commands.
	- EvAdventure is built with the concept of a backpack but does not yet implement containers
- Inventory management
	- Do characters have a carrying limit in terms of objects or size?
		- EvAdventure comes with a built-in carrying capacity
	- If there are containers, do they allow you to carry more?
