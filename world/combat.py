
from .enums import CombatRange

_MAX_RANGE = max([en.value for en in CombatRange])

# format for combat prompt, currently unused
# health, mana, current attack cooldown
COMBAT_PROMPT = "HP {hp} - MP {mp} - ACD {cd}"

class CombatHandler:
    positions = None
    
    def __init__(self, attacker, target):
        # the starting position logic could be better
        self.positions = { attacker: 1, target: 2 }
        attacker.ndb.combat = self
        target.ndb.combat = self
    
    def add(self, participant):
        """Add a new combatant to the combat instance."""
        # only add if they aren't already part of the fight
        if participant not in self.positions:
          self.positions[participant] = 0
          participant.ndb.combat = self
    
    def remove(self, participant):
        """Removes a combatant from the combat instance."""
        # only remove if they're actually in combat
        if participant in self.positions:
            self.positions.pop(participant)
            participant.nattributes.remove("combat")

            survivors = self.positions.keys()
            if len(survivors) == 1:
                # only one participant means no more fight
                survivors[0].nattributes.remove("combat")
                self.positions = None
  
    def merge(self, other):
        """Merge another combat instance into this one"""
        # an entity can't be in two combat instances at once, so there should be no dupes
        self.positions |= other.positions
        for obj in other.positions.keys():
            obj.ndb.combat = self
        other.positions = None

    def get_range(self, attacker, target):
        """Get the distance from target in terms of weapon range."""
        # both combatants must be in combat
        if not (attacker in self.positions and target in self.positions):
            return None

        distance = abs(self.positions[attacker] - self.positions[target])
        range = None
        for range_enum in CombatRange:
            if range_enum.value > distance:
                break
            range = range_enum.name

        return range

    def in_range(self, attacker, target, range):
        """Check if target is within the specified range of attacker."""
        # both combatants must be in combat
        if not (attacker in self.positions and target in self.positions):
            return None
        
        range_enum = [en for en in CombatRange if en.name == range]
        if not range_enum:
            return False
        range_enum = range_enum[0]
        distance = abs(self.positions[attacker] - self.positions[target])
        return range_enum.value >= distance

    def any_in_range(self, attacker, range):
        if attacker not in self.positions:
            return False
        
        range_enum = [en for en in CombatRange if en.name == range]
        if not range_enum:
            return False
        range_enum = range_enum[0]
        return any( p for p in self.positions.values() if p <= range_enum.value )

    def approach(self, mover, target):
        """
        Move a combatant towards the target.
        Returns True if the distance changed, or False if it didn't.
        """
        # both combatants must be in combat
        if not (mover in self.positions and target in self.positions):
            return False

        start = self.positions[mover]
        end = self.positions[target]
        
        if start == end:
            # already as close as you can get
            return False
        
        change = 1 if start < end else -1
        self.positions[mover] += change
        return True

    def retreat(self, mover, target):
        """
        Move a combatant away from the target.
        Returns True if the distance changed, or False if it didn't.
        """
        # both combatants must be in combat
        if not (mover in self.positions and target in self.positions):
            return False

        start = self.positions[mover]
        end = self.positions[target]
        
        # can't move beyond maximum weapon range
        if abs(start-end) >= _MAX_RANGE:
            return False

        change = -1 if start < end else 1
        self.positions[mover] += change
        return True
