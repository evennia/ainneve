
# maximum range for different weapon types
_WEAPON_RANGES = {
    "grapple": 0,
    "melee": 1,
    "reach": 2,
    "ranged": 6,
}

# format for combat prompt, currently unused
# health, mana, current attack cooldown
COMBAT_PROMPT = "HP {hp} - MP {mp} - ACD {cd}"

class CombatHandler:
    positions = None
    
    def __init__(self, attacker, target):
        # the starting position logic could be better
        positions = { attacker: 1, target: 2 }
        attacker.ndb.combat = self
        target.ndb.combat = self
    
    def add(self, participant):
        """Add a new combatant to the combat instance."""
        # only add if they aren't already part of the fight
        if participant not in self.positions:
          positions[participant] = 0
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
    

    def get_range(self, attacker, target):
        """Get the distance from target in terms of weapon range."""
        # both combatants must be in combat
        if not (attacker in self.positions and target in self.positions):
            return None

        distance = abs(self.positions[attacker] - self.positions[target])
        range = None
        for key, val in _WEAPON_RANGES.items():
            if val > distance:
                break
            range = key

        return range

    def in_range(self, attacker, target, range):
        """Check if target is within the specified range of attacker."""
        # both combatants must be in combat
        if not (attacker in self.positions and target in self.positions):
            return None
        
        if range not in _WEAPON_RANGES:
            return False

        distance = abs(self.positions[attacker] - self.positions[target])
        return _WEAPON_RANGES[range] >= distance
    
    def any_in_range(self, attacker, range):
        if attacker not in self.positions:
            return False
        
        if range not in _WEAPON_RANGES:
            return False
        
        return any( p for p in self.positions.values() if p <= _WEAPON_RANGES[range] )

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
        if abs(start-end) >= max(_WEAPON_RANGES.values()):
            return False

        change = -1 if start < end else 1
        self.positions[mover] += change
        return True
