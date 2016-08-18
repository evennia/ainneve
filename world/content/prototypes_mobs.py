"""
Prototype module containing mobs.
"""

from evennia.utils import fill
from random import randint
#"traits": lambda: {'STR':2,'HP':randint(3,5)}

SAMPLE_NPC = {
	"key":"a sample npc",
	"aliases":["sample", "npc"],
	"tag":["NPC"],
	"typeclass": "typeclasses.characters.NPC",
	"desc": "I'm a doctor Jim, not a bloody NPC",
	"traits":{'STR':5,'DEX':5,'PER':5,'CHA':5,'INT':5,'VIT':5,
				'BM':5,'WM':5,'MAG':10,
				'REFL':5,'FORT':5,'WILL':5,'ENC':50,
				'HP':5,'MV':5,'SP':5,'LV':1,'ACT':5,
				'ATKM':5,'DEF':5,'ATKR':5,'PP':5,'ATKU':5},
	"skills":{'escape':1, 'climb':1,'jump':1,
				'lockpick':1,'listen':1,'sense':1,
				'appraise':1, 'medicine':1, 'survival':1,
				'balance':1, 'sneak':1, 'throwing':1,
				'animal':1, 'barter':1, 'leadership':1},
}

GOBLIN = {
	"key":"a tiny little goblin",
	"aliases":["goblin", "tiny"],
	"tag":["NPC"],
	"typeclass": "typeclasses.characters.NPC",
	"desc": "It's a little green goblin. It wants your love and affection",
	"traits":{'STR':9,'DEX':8},
	"skills":{'escape':10, 'barter':3},
}