from random import randint

from evadventure.enums import Ability

death_table = (
    ("1-2", "dead"),
    ("3", "strength"),
    ("4", "dexterity"),
    ("5", "constitution"),
    ("6", "intelligence"),
    ("7", "wisdom"),
    ("8", "charisma"),
)


class EvAdventureRollEngine:

    def roll(self, roll_string):
        """
        Roll XdY dice, where X is the number of dice
        and Y the number of sides per die.

        Args:
            roll_string (str): A dice string on the form XdY.
        Returns:
            int: The result of the roll.

        """

        # split the XdY input on the 'd' one time
        number, diesize = roll_string.split("d", 1)

        # convert from string to integers
        number = int(number)
        diesize = int(diesize)

        # make the roll
        return sum(randint(1, diesize) for _ in range(number))

    def roll_with_advantage_or_disadvantage(self, advantage=False, disadvantage=False):

        if not (advantage or disadvantage) or (advantage and disadvantage):
            # normal roll - advantage/disadvantage not set or they cancel
            # each other out
            return self.roll("1d20")
        elif advantage:
            # highest of two d20 rolls
            return max(self.roll("1d20"), self.roll("1d20"))
        else:
            # disadvantage - lowest of two d20 rolls
            return min(self.roll("1d20"), self.roll("1d20"))

    # get result of normal d20 roll, with advantage/disadvantage (or not)

    def saving_throw(self, character, bonus_type=Ability.STR, target=15, advantage=False, disadvantage=False):
        """
        Do a saving throw, trying to beat a target.

        Args:
           character (Character): A character (assumed to have Ability bonuses
               stored on itself as Attributes).
           bonus_type (Ability): A valid Ability bonus enum.
           target (int): The target number to beat. Always 15 in Knave.
           advantage (bool): If character has advantage on this roll.
           disadvantage (bool): If character has disadvantage on this roll.

        Returns:
            tuple: A tuple (bool, Ability), showing if the throw succeeded and
                the quality is one of None or Ability.CRITICAL_FAILURE/SUCCESS

        """

        # make a roll
        dice_roll = self.roll_with_advantage_or_disadvantage(advantage, disadvantage)

        # figure out if we had critical failure/success
        quality = None
        if dice_roll == 1:
            quality = Ability.CRITICAL_FAILURE
        elif dice_roll == 20:
            quality = Ability.CRITICAL_SUCCESS

            # figure out bonus
        bonus = getattr(character, bonus_type.value, 1)

        # return a tuple (bool, quality)
        return (dice_roll + bonus) > target, quality

    def opposed_saving_throw(self, attacker, defender,
                             attack_type=Ability.STR, defense_type=Ability.ARMOR,
                             advantage=False, disadvantage=False):

        defender_defense = getattr(defender, defense_type.value, 1) + 10
        result, quality = self.saving_throw(
            attacker,
            bonus_type=attack_type,
            target=defender_defense,
            advantage=advantage,
            disadvantage=disadvantage
        )

        return result, quality

    def roll_random_table(self, dieroll, table_choices):
        """
        Args:
             dieroll (str): A die roll string, like "1d20".
             table_choices (iterable): A list of either single elements or
                of tuples.
        Returns:
            Any: A random result from the given list of choices.

        Raises:
            RuntimeError: If rolling dice giving results outside the table.

        """
        roll_result = self.roll(dieroll)

        if isinstance(table_choices[0], (tuple, list)):
            # the first element is a tuple/list; treat as on the form [("1-5", "item"),...]
            for (valrange, choice) in table_choices:
                minval, *maxval = valrange.split("-", 1)
                minval = abs(int(minval))
                maxval = abs(int(maxval[0]) if maxval else minval)

                if minval <= roll_result <= maxval:
                    return choice

                    # if we get here we must have set a dieroll producing a value
            # outside of the table boundaries - raise error
            raise RuntimeError("roll_random_table: Invalid die roll")
        else:
            # a simple regular list
            roll_result = max(1, min(len(table_choices), roll_result))
            return table_choices[roll_result - 1]

    def morale_check(self, defender):
        return self.roll("2d6") <= getattr(defender, "morale", 9)

    def heal_from_rest(self, character):
        """
        A night's rest retains 1d8 + CON HP

        """
        con_bonus = getattr(character, Ability.CON.value, 1)
        character.heal(self.roll("1d8") + con_bonus)

    def roll_death(self, character):
        ability_name = self.roll_random_table("1d8", death_table)

        if ability_name == "dead":
            # TODO - kill the character!
            pass
        else:
            loss = self.roll("1d4")

            current_ability = getattr(character, ability_name)
            current_ability -= loss

            if current_ability < -10:
                # TODO - kill the character!
                pass
            else:
                # refresh 1d4 health, but suffer 1d4 ability loss
                character.heal(self.roll("1d4"))
                setattr(character, ability_name, current_ability)

                character.msg(
                    "You survive your brush with death, and while you recover "
                    f"some health, you permanently lose {loss} {ability_name} instead."
                )


dice = EvAdventureRollEngine()