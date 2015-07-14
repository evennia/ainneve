from world.abilities.ability import Ability
                                           
# Create the spells database               
spell_db = {}                              
                                           
# Initalise every spell                    
spell_db['fireball'] = Ability()               
spell_db['icebolt'] = Ability()               
           
# fireball spell 
spell_db['fireball'].affects = {}
spell_db['fireball'].description = 'A fireball ready to singe your foe'
spell_db['fireball'].hp_cost = 0
spell_db['fireball'].level = 1
spell_db['fireball'].mana_cost = 10
spell_db['fireball'].max_level = 99
spell_db['fireball'].modifier = 100
spell_db['fireball'].move_cost = 0
spell_db['fireball'].msg_to_caller = 'You cast %s on %s.'
spell_db['fireball'].msg_to_room = '%s cast %s on %s.'
spell_db['fireball'].msg_to_target = '%s cast %s on you!'
spell_db['fireball'].name = 'fireball'
spell_db['fireball'].type = 'spell'
spell_db['fireball'].use_delay = 1
           
# icebolt spell 
spell_db['icebolt'].affects = {}
spell_db['icebolt'].description = 'An icebolt is ready to freeze your foe'
spell_db['icebolt'].hp_cost = 0
spell_db['icebolt'].level = 1
spell_db['icebolt'].mana_cost = 10
spell_db['icebolt'].max_level = 99
spell_db['icebolt'].modifier = 200
spell_db['icebolt'].move_cost = 0
spell_db['icebolt'].msg_to_caller = 'You cast %s on %s.'
spell_db['icebolt'].msg_to_room = '%s cast %s on %s.'
spell_db['icebolt'].msg_to_target = '%s cast %s on you!'
spell_db['icebolt'].name = 'icebolt'
spell_db['icebolt'].type = 'spell'
spell_db['icebolt'].use_delay = 1

