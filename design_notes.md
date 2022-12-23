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
- NOT turn-based combat
	- *Notes from friar are at the end of the section.*
	- Weapon stats
		- Are they bonus to-hit, bonus damage, or defining attack/damage type?
	- Armor stats
		- Heavier armor adds a dodge penalty
		- Damage reduction or general defense bonus?
	- Dice rolls are standardized as 2d6+stat
		- *IMPLEMENTATION NOTE* - Make this a single point-of-access method which passes in the stat.
	- Since this isn't turn-based, there should be no "initiative" but instead "attack speed".
		- Attack speed defines your delay after attacking - weapon speed minus armor encumbrance?
		- Attacking also costs stamina - what exactly determines the cost?
	- Target zones
		- Combatants can set their defense and attack zones as an XY coordinate, left/center/right, low/mid/high
			- Changing attack zone is a free action
			- Changing defense zone incurs an attack delay
		- Attacks landing on your defended zone procs a defense auto-action, which if successful gives a counter-attack bonus.
			- Should there be any effect for landing "near" a defended zone? e.g. if you have left/mid and someone aims for left/high
		- Attacks landing outside the defense zones successfully land on armor in the strike zone
	- Combat movement
		- While in combat, you can "advance" or "retreat" to/from an opponent to change your active range
			- Weapons can have different min/max ranges
		- Advancing and retreating incur movement delays
			- Ahould this be separate from the attack delay, or should moving prevent attacks/attacking prevent movement?
- Crafting weapons/armor/potions as a counter-option to buying them.
	- *IMPLEMENTATION NOTE* - Use the crafting contrib
- Containers
	- If we want them, they need to be implemented, including custom get/put/drop commands.
	- EvAdventure is built with the concept of a backpack but does not yet implement containers
- Inventory management
	- Do characters have a carrying limit in terms of objects or size?
		- EvAdventure comes with a built-in carrying capacity
	- If there are containers, do they allow you to carry more?

----

friar's combat notes (included as-is until I figure out how to condense them to concise bullet points):
> Each combatant would use 2d6 + stat for initiative, ties go to the higher stat, then roll off again if they have the same stat.
> 
> Each combatant will have a preferred aggression level pre-set before combat begins (Low, Medium, High)...each swing costs stamina and aggression multiplies the stamina cost (but reduces the post-swing delay).
> 
> Each combatant would also have pre-set defensive parry, block and dodge locations (left/center/right, low/medium/high).
> 
> Each attack would set a target location (left/center/right, low/medium/high)
> 
> Any attack that avoids one of the 3 defensive locations auto-hits armor near that location
> 
> Any attack that meets one of those 3 defensive locations gets checked for the right equipment (parry needs a weapon to parry with, block needs a shield/bracer to block with, dodge needs  lighter armor to dodge with, etc).
> 
> if they successfully defend, they get a bonus on their next attack response.
> 
> Attackers then have to wait for their attack delay to expire before they can take their next action.
> 
> armor reduces damage.
> 
> heavier armors can remove the ability to dodge.
> 
> Changing defense locations requires a short delay
> 
> (critters will likely use patterns of attack and defenses).
> 
> Oh, and aggression will also multiply damage by some factor.
> 
> I figure there should be multiple types of damage as well, stun (which can add to or multiply action delays), normal healable wounds, and aggravated damage which requires some out-of-combat effect to heal and reduces maximum stamina.
