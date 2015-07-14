from world.abilities.ability import Ability

#Create the skills database
skill_db = {}

#Initalise every skill
skill_db['hide'] = Ability()
skill_db['kick'] = Ability()

# hide skill
skill_db['hide'].affects = {}
skill_db['hide'].description = 'Allows a player to hide'
skill_db['hide'].hp_cost = 0
skill_db['hide'].level = 1
skill_db['hide'].mana_cost = 10
skill_db['hide'].max_level = 99
skill_db['hide'].modifier = 200
skill_db['hide'].move_cost = 0
skill_db['hide'].msg_to_caller = 'You slip into the shadows.'
skill_db['hide'].msg_to_room = ''
skill_db['hide'].msg_to_target = ''
skill_db['hide'].name = 'hide'
skill_db['hide'].type = 'skill'
skill_db['hide'].use_delay = 1

# kick skill
skill_db['kick'].affects = {}
skill_db['kick'].description = 'Kick your opponents right in the throat!'
skill_db['kick'].hp_cost = 0
skill_db['kick'].level = 1
skill_db['kick'].mana_cost = 0
skill_db['kick'].max_level = 99
skill_db['kick'].modifier = 150
skill_db['kick'].move_cost = 10
skill_db['kick'].msg_to_caller = 'You kick %s.'
skill_db['kick'].msg_to_room = '%s kicks %s.'
skill_db['kick'].msg_to_target = '%s kicks %s.'
skill_db['kick'].name = 'kick'
skill_db['kick'].type = 'skill'
skill_db['kick'].use_delay = 1
