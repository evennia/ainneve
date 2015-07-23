from world.abilities.ability import Ability

#Create the spells database
spell_manager = {}

# fireball sample spell; adjust/remove later
spell_manager['fireball'] = Ability()
spell_manager['fireball'].name = 'fireball'
spell_manager['fireball'].type = 'spell'
spell_manager['fireball'].description = 'Allows a player to cast fireball'
spell_manager['fireball'].level = 1
spell_manager['fireball'].hp_cost = 0
spell_manager['fireball'].mana_cost = 10
spell_manager['fireball'].move_cost = 0
spell_manager['fireball'].modifier = 200
spell_manager['fireball'].msg_to_caller = 'You cast *ability* on *target*'
spell_manager['fireball'].msg_to_room = '*target* cast *ability* on *target*'
spell_manager['fireball'].msg_to_target = '*caller* cast *ability* on you.'
spell_manager['fireball'].use_delay = 1
spell_manager['fireball'].affects = {}

# icebolt sample spell; adjust/remove later
spell_manager['icebolt'] = Ability()
spell_manager['icebolt'].name = 'icebolt'
spell_manager['icebolt'].type = 'spell'
spell_manager['icebolt'].description = 'Allows a player to cast icebolt'
spell_manager['icebolt'].level = 1
spell_manager['icebolt'].hp_cost = 0
spell_manager['icebolt'].mana_cost = 10
spell_manager['icebolt'].move_cost = 0
spell_manager['icebolt'].modifier = 100
spell_manager['icebolt'].msg_to_caller = 'You cast *ability* on *target*'
spell_manager['icebolt'].msg_to_room = '*target* cast *ability* on *target*'
spell_manager['icebolt'].msg_to_target = '*caller* cast *ability* on you.'
spell_manager['icebolt'].use_delay = 1
spell_manager['icebolt'].affects = {}

def show_spell_msg(mode=None,spell_name=None,caller=None,target=None):
    """
    from world.config.spellmanager import show_spell_msg

    usage:  show_spell_msg('MSG_TO_CALLER', 'fireball', caller, target)   # send msg to caller
            show_spell_msg('MSG_TO_TARGET', 'fireball', caller, target)   # send msg to target
            show_spell_msg('MSG_TO_ROOM', 'fireball', caller, target)     # send msg to room
    """
    MSG_OPTIONS = {'*caller*'  : str(caller.name if caller else None),
                   '*target*'  : str(target.name if target else None),
                   '*ability*' : str(spell_manager[spell_name].name if target else None),
                   }

    spell = spell_manager[spell_name]
    msg_to_caller = spell.msg_to_caller
    msg_to_target = spell.msg_to_target
    msg_to_room = spell.msg_to_room

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
