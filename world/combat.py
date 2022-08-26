
# breakpoints for distance ranges of different weapon types
_WEAPON_RANGES = {
    0: "melee",
    2: "reach",
    4: "ranged",
}

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
        if not (mover in self.positions and target in self.positions):
            return None

        distance = abs(self.positions[attacker] - self.positions[target])
        range = None
        for key, val in _WEAPON_RANGES.items():
            if key > distance:
                break
            range = val

        return range

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
        
        change = -1 if start < end else 1
        self.positions[mover] += change
        return True
