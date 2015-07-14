from world.traits.trait import Trait

#Create the race database
primary_trait_db = {}
secondary_trait_db = {}

# ------------------------------
# Initalise every primary trait
# ------------------------------
primary_trait_db['strength'] = Trait('strength', static=True)
primary_trait_db['perception'] = Trait('perception', static=True)
primary_trait_db['intelligence'] = Trait('intelligence', static=True)
primary_trait_db['dexterity'] = Trait('dexterity', static=True)
primary_trait_db['charisma'] = Trait('charisma', static=True)
primary_trait_db['vitality'] = Trait('vitality', static=True)
primary_trait_db['magic'] = Trait('magic', static=True)

secondary_trait_db['health'] = Trait('health')              #vit
secondary_trait_db['stamina'] = Trait('stamina')            #vit
secondary_trait_db['skills'] = Trait('skills')
secondary_trait_db['languages'] = Trait('languages')        #int
secondary_trait_db['fortitude'] = Trait('fortitude')        #vit
secondary_trait_db['reflex'] = Trait('reflex')              #dex
secondary_trait_db['will'] = Trait('will')                  #int
secondary_trait_db['mana'] = Trait('mana')                  #int
secondary_trait_db['armor'] = Trait('armor', static=True)
