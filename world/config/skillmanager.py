from world.abilities.ability import Ability

#Create the skills database
skill_manager = {}

# hide skill
skill_manager['hide'] = Ability()
skill_manager['hide'].name = 'hide'
skill_manager['hide'].type = 'skill'
skill_manager['hide'].description = 'Allows a player to hide'
skill_manager['hide'].level = 1
skill_manager['hide'].hp_cost = 0
skill_manager['hide'].mana_cost = 10
skill_manager['hide'].move_cost = 0
skill_manager['hide'].modifier = 200
skill_manager['hide'].msg_to_caller = 'You slip into the shadows.'
skill_manager['hide'].msg_to_room = '*caller* slips into the shadow.'
skill_manager['hide'].msg_to_target = ''
skill_manager['hide'].use_delay = 1
skill_manager['hide'].affects = {}

# kick skill
skill_manager['kick'] = Ability()
skill_manager['kick'].name = 'kick'
skill_manager['kick'].type = 'skill'
skill_manager['kick'].level = 1
skill_manager['kick'].description = 'Allows a player to kick'
skill_manager['kick'].hp_cost = 0
skill_manager['kick'].mana_cost = 0
skill_manager['kick'].move_cost = 10
skill_manager['kick'].modifier = 150
skill_manager['kick'].msg_to_caller = 'You kick *target*.'
skill_manager['kick'].msg_to_room = '*caller* kicks *target*.'
skill_manager['kick'].msg_to_target = '*caller* kicks you.'
skill_manager['kick'].use_delay = 1
skill_manager['kick'].affects = {}

def show_skill_msg(mode=None,skill_name=None,caller=None,target=None):
    """
    from world.config.skillmanager import show_skill_msg

    usage:  show_skill_msg('MSG_TO_CALLER', 'kick', caller, target)   # send msg to caller
            show_skill_msg('MSG_TO_TARGET', 'kick', caller, target)   # send msg to target
            show_skill_msg('MSG_TO_ROOM', 'kick', caller, target)     # send msg to room
    """

    MSG_OPTIONS = {'*caller*'  : str(caller.name if caller else None),
                   '*target*'  : str(target.name if target else None),
                   '*ability*' : str(skill_manager[skill_name].name if target else None),
                   }

    skill = skill_manager[skill_name]
    msg_to_caller = skill.msg_to_caller
    msg_to_target = skill.msg_to_target
    msg_to_room = skill.msg_to_room

    for option in MSG_OPTIONS:
        msg_to_caller = msg_to_caller.replace(option, MSG_OPTIONS[option])
    for option in MSG_OPTIONS:
        msg_to_target = msg_to_target.replace(option, MSG_OPTIONS[option])
    for option in MSG_OPTIONS:
        msg_to_room = msg_to_room.replace(option, MSG_OPTIONS[option])

    if caller and msg_to_caller and 'MSG_TO_CALLER' in mode:
        caller.msg(msg_to_caller)
    elif target and msg_to_target and 'MSG_TO_TARGET' in mode:
        target.msg(msg_to_target)
    elif caller and msg_to_room and 'MSG_TO_ROOM' in mode:
        caller.location.msg_contents(msg_to_room,exclude=[caller,target])
