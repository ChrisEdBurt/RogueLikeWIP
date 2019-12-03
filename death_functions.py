import tcod as tc

from game_messages import Message
from game_states import GameStates
from render_functions import RenderOrder

def kill_player(player):
    player.char = '%'
    player.color = tc.dark_red

    return Message('You died!', tc.red), GameStates.PLAYER_DEAD

def kill_monster(monster):
    death_message = Message('{0} is dead!'.format(monster.name.capitalize()), tc.orange)

    monster.char = '%'
    # monster.color = tc.dark_red
    # monster.color = tc.red
    monster.color = tc.white
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.render_order = RenderOrder.CORPSE

    return death_message