"""
Prototype module containing mobs.
"""

from evennia.utils import fill
from world.rulebook import d_roll
import random
from sdesc_vars import *

### Notes
#variable traits: 'traits': {'STR': lambda: d_roll('1d8')}
#Icarus_: I just pushed an update to the spawner mechanism; you should be able to use callable for all fields now (keys, locations, whatever). There is also the 'exec' field where you can put executable python code. in that code you can use 'obj' to access the object just created. That way you can do e.g. exec:"obj.sdesc('sdesc_string')" to call the sdesc handler on creation.
#    "exec": "obj.execute_cmd('say My tags include {}'.format(obj.db.tag))",


SAMPLE_NPC = {
    "key": "a sample npc",
    "aliases": ["sample", "npc"],
    "tags": ["NPC"],
    "typeclass": "typeclasses.characters.NPC",
    "desc": "I'm a doctor Jim, not a bloody NPC",
    "traits": {'STR': 5, 'DEX': 5, 'PER': 5, 'CHA': 5, 'INT': 5, 'VIT': 5,
               'BM': 5, 'WM': 5, 'MAG': 10,
               'REFL': 5, 'FORT': 5, 'WILL': 5, 'ENC': 50,
               'HP': 5, 'MV': 5, 'SP': 5, 'LV': 1, 'ACT': 5,
               'ATKM': 5, 'DEF': 5, 'ATKR': 5, 'PP': 5, 'ATKU': 5},
    "skills": {'escape': 1, 'climb': 1, 'jump': 1,
               'lockpick': 1, 'listen': 1, 'sense': 1,
               'appraise': 1, 'medicine': 1, 'survival': 1,
               'balance': 1, 'sneak': 1, 'throwing': 1,
               'animal': 1, 'barter': 1, 'leadership': 1},
}

RAT = {
    "key":"a rat npc",
    "sdesc": lambda: "{}, {} rat".format(random.choice(rat_adj_1),random.choice(rat_adj_2)),
    "tags": ["NPC"],
    "typeclass": "typeclasses.characters.NPC",
    "desc": "Beware of rat poison.",
    "traits": {'STR': 5, 'DEX': 5, 'PER': 5, 'CHA': 5, 'INT': 5, 'VIT': 5,
               'BM': 5, 'WM': 5, 'MAG': 10,
               'REFL': 5, 'FORT': 5, 'WILL': 5, 'ENC': 50,
               'HP': 5, 'MV': 5, 'SP': 5, 'LV': 1, 'ACT': 5,
               'ATKM': 5, 'DEF': 5, 'ATKR': 5, 'PP': 5, 'ATKU': 5},
    "skills": {'escape': 1, 'climb': 1, 'jump': 1,
               'lockpick': 1, 'listen': 1, 'sense': 1,
               'appraise': 1, 'medicine': 1, 'survival': 1,
               'balance': 1, 'sneak': 1, 'throwing': 1,
               'animal': 1, 'barter': 1, 'leadership': 1},
}

RABBIT = {
    "key":"a rabbit npc",
    "sdesc": "a small rabbit",
    "tags": ["NPC"],
    "typeclass": "typeclasses.characters.NPC",
    "desc": "This is a small, fluffy white rabbit. It is likely harmless",
    "traits": {'STR': 5, 'DEX': 5, 'PER': 5, 'CHA': 5, 'INT': 5, 'VIT': 5,
               'BM': 5, 'WM': 5, 'MAG': 10,
               'REFL': 5, 'FORT': 5, 'WILL': 5, 'ENC': 50,
               'HP': 5, 'MV': 5, 'SP': 5, 'LV': 1, 'ACT': 5,
               'ATKM': 5, 'DEF': 5, 'ATKR': 5, 'PP': 5, 'ATKU': 5},
    "skills": {'escape': 1, 'climb': 1, 'jump': 1,
               'lockpick': 1, 'listen': 1, 'sense': 1,
               'appraise': 1, 'medicine': 1, 'survival': 1,
               'balance': 1, 'sneak': 1, 'throwing': 1,
               'animal': 1, 'barter': 1, 'leadership': 1},
}

DEER = {
    "key":"a deer npc",
    "sdesc": "a brown deer",
    "tags": ["NPC"],
    "typeclass": "typeclasses.characters.NPC",
    "desc": "This is a relatively sturdy looking deer.",
    "traits": {'STR': 5, 'DEX': 5, 'PER': 5, 'CHA': 5, 'INT': 5, 'VIT': 5,
               'BM': 5, 'WM': 5, 'MAG': 10,
               'REFL': 5, 'FORT': 5, 'WILL': 5, 'ENC': 50,
               'HP': 5, 'MV': 5, 'SP': 5, 'LV': 1, 'ACT': 5,
               'ATKM': 5, 'DEF': 5, 'ATKR': 5, 'PP': 5, 'ATKU': 5},
    "skills": {'escape': 1, 'climb': 1, 'jump': 1,
               'lockpick': 1, 'listen': 1, 'sense': 1,
               'appraise': 1, 'medicine': 1, 'survival': 1,
               'balance': 1, 'sneak': 1, 'throwing': 1,
               'animal': 1, 'barter': 1, 'leadership': 1},
}
WOLF = {
    "key":"a wolf npc",
    "sdesc": lambda: "{}, {} wolf".format(random.choice(wolf_adj_1),random.choice(wolf_adj_2)),
    "tags": ["NPC", "AGGRESSIVE"],
    "typeclass": "typeclasses.characters.NPC",
    "desc": "Oh look, here's a wolf. It's probably going to attempt to eat you.",
    "emote_aggressive": "growls ferociously",
    "traits": {'STR': 2, 'DEX': 3, 'PER': 2, 'CHA': 1, 'INT': 2, 'VIT': 4,
               'BM': 0, 'WM': 0, 'MAG': 0,
               'REFL': 3, 'FORT': 2, 'WILL': 2, 'ENC': 50,
               'HP': 4, 'MV': 4, 'SP': 4, 'LV': 1, 'ACT': 5, 'XP': 1,
               'ATKM': 2, 'DEF': 3, 'ATKR': 2, 'PP': 0, 'ATKU': 2},
    "skills": {'escape': 1, 'climb': 1, 'jump': 1,
               'lockpick': 1, 'listen': 1, 'sense': 1,
               'appraise': 1, 'medicine': 1, 'survival': 1,
               'balance': 1, 'sneak': 1, 'throwing': 1,
               'animal': 1, 'barter': 1, 'leadership': 1},
}

SPIDER = {
    "key": "a spider npc",
    "sdesc": lambda: "{}, {} spider".format(random.choice(spider_adj_1),random.choice(spider_adj_2)),
    "tags": ["NPC", "AGGRESSIVE"],
    "typeclass": "typeclasses.characters.NPC",
    "desc": "Need a hand? Well just you wait. We'll help you out, we each have eight.",
    "traits": {'STR': 5, 'DEX': 5, 'PER': 5, 'CHA': 5, 'INT': 5, 'VIT': 5,
               'BM': 5, 'WM': 5, 'MAG': 10,
               'REFL': 5, 'FORT': 5, 'WILL': 5, 'ENC': 50,
               'HP': 5, 'MV': 5, 'SP': 5, 'LV': 1, 'ACT': 5,
               'ATKM': 5, 'DEF': 5, 'ATKR': 5, 'PP': 5, 'ATKU': 5},
    "skills": {'escape': 1, 'climb': 1, 'jump': 1,
               'lockpick': 1, 'listen': 1, 'sense': 1,
               'appraise': 1, 'medicine': 1, 'survival': 1,
               'balance': 1, 'sneak': 1, 'throwing': 1,
               'animal': 1, 'barter': 1, 'leadership': 1},
}

ORC = {
    "key": "an orc npc",
    "sdesc": lambda: "{}, {} orc".format(random.choice(orc_adj_1),random.choice(orc_adj_2)),
    "tags": ["NPC", "AGGRESSIVE"],
    "exec": "obj.execute_cmd('say My tags include {}'.format(obj.db.tag))",
    "typeclass": "typeclasses.characters.NPC",
    "desc": "An intellectual creature at heart, the orc is a misunderstood beast who simply desires to be understood and loved. It expresses this love through extreme violence.",
    "traits": {'STR': 5, 'DEX': 5, 'PER': 5, 'CHA': 5, 'INT': 5, 'VIT': 5,
               'BM': 5, 'WM': 5, 'MAG': 10,
               'REFL': 5, 'FORT': 5, 'WILL': 5, 'ENC': 50,
               'HP': 5, 'MV': 5, 'SP': 5, 'LV': 1, 'ACT': 5,
               'ATKM': 5, 'DEF': 5, 'ATKR': 5, 'PP': 5, 'ATKU': 5},
    "skills": {'escape': 1, 'climb': 1, 'jump': 1,
               'lockpick': 1, 'listen': 1, 'sense': 1,
               'appraise': 1, 'medicine': 1, 'survival': 1,
               'balance': 1, 'sneak': 1, 'throwing': 1,
               'animal': 1, 'barter': 1, 'leadership': 1},
}


GOBLIN = {
    "key": "a tiny little goblin",
    "aliases": ["goblin", "tiny"],
    "tags": ["NPC"],
    "typeclass": "typeclasses.characters.NPC",
    "desc": "It's a little green goblin. It wants your love and affection",
    "traits": {'STR': lambda: d_roll('1d8'), 'DEX': lambda: d_roll('1d8')},
    "skills": {'escape': 10, 'barter': 3},
}


