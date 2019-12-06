import tcod as tc

from game_states import GameStates

def handle_keys(key, game_state):
    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn_keys(key)

    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)

    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key)

    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_inventory_keys(key)

    elif game_state == GameStates.SHOW_TUTORIAL:
        return handle_tutorial_menu(key)

    elif game_state == GameStates.SHOW_HELP_MENU:
        return handle_help_menu(key)

    elif game_state == GameStates.CYCLE_TARGET:
        return handle_cycle_target(key)

    elif game_state == GameStates.RANGED:
        return handle_ranged_keys(key)

    elif game_state == GameStates.LEVEL_UP:
        return handle_level_up_menu(key)

    elif game_state == GameStates.CHARACTER_SCREEN:
        return handle_character_screen(key)
        
    return {}

# tcod.event.KeyDown
def handle_player_turn_keys(key):
    
    key_char = chr(key.c)
    # Movement keys
    #UP
    if key.vk == tc.KEY_UP or key.vk == tc.KEY_KP8:
        return {'move': (0, -1)}
    #DOWN
    elif key.vk == tc.KEY_DOWN or key.vk == tc.KEY_KP2:
        return {'move': (0, 1)}
    #LEFT
    elif key.vk == tc.KEY_LEFT or key.vk == tc.KEY_KP4:
        return {'move': (-1, 0)}
    #RIGHT
    elif key.vk == tc.KEY_RIGHT or key.vk == tc.KEY_KP6:
        return {'move': (1, 0)}
    #UP+LEFT
    elif key.vk == tc.KEY_KP7:
        return {'move': (-1, -1)}
    #UP+RIGHT
    elif key.vk == tc.KEY_KP9:
        return {'move': (1, -1)}
    #DOWN+LEFT
    elif key.vk == tc.KEY_KP1:
        return {'move': (-1, 1)}
    #DOWN+RIGHT
    elif key.vk == tc.KEY_KP3:
        return {'move': (1, 1)}
    #WAIT
    elif key_char == 't':
        return {'wait': True}
    #i for Pickup
    if key_char == 'e':
        return {'pickup': True}
    #i for Inventory
    elif key_char == 'i':
        return {'show_inventory': True}
    #d for Drop 
    elif key_char == 'd':
        return {'drop_inventory': True}
    # Enter use stairs
    elif key.vk == tc.KEY_ENTER:
        return {'take_stairs': True}
    # c Character sreen
    elif key_char == 'c':
        return {'show_character_screen': True}

    # p TARGET CYCLE MODE
    elif key_char == 'r':
        return {'cycle_target': True}
    # p GOD MODE
    elif key_char == 'p':
        return {'god_mode': True}
    # y BURNING
    elif key_char == 'y':
        return {'burning': True}
    # u POISON
    elif key_char == 'u':
        return {'poisoned': True}
    # u REVEALMAP
    elif key_char == 'm':
        return {'reveal_map': True}
    # / INCREASE LIMB DAMAGE
    elif key_char == '.':
        return {'increase_limb_damage': True}
    # / DECREASE LIMB DAMAGE
    elif key_char == ',':
        return {'decrease_limb_damage': True}
    # o TELEPORT
    elif key_char == 'o':
        return {'teleport': True} 
    # SPWAN ENEMY
    elif key.vk == tc.KEY_SPACE:
        return {'spawn_enemy_at' : True}
    
    # SHOW HELP
    elif key_char == '/':
        return {'show_help_menu' : True}

    # Alt: toggle full screen
    if key.vk == tc.KEY_1:
        return {'fullscreen': True}
    # Exit the game
    elif key.vk == tc.KEY_ESCAPE:
        return {'exit': True}
    # No key was pressed
    return {}

def handle_full_screen(key):
    if key.vk == tc.KEY_1:
        return {'fullscreen': True}

def handle_targeting_keys(key):
    if key.vk == tc.KEY_ESCAPE:
        return {'exit': True}

    return {}

def handle_cycle_target(key):
    # key_char =chr(key.c)
    # if key_char == 'r':
    #     return {'activate_cycle_target' : True}
    if key.vk == tc.KEY_ESCAPE:
        return {'exit': True}
    elif key.vk == tc.KEY_RIGHT:
        return {'right_target': True}
    # elif key.vk == tc.KEY_LEFT or key.vk == tc.KEY_KP6 or key_char == 'a':
    elif key.vk == tc.KEY_LEFT:
        return {'left_target': True}
    return {}

def handle_burning(key):
    key_char = chr(key.c)
    if key_char == 'u':
        return {'burning': True}

    return {}

def handle_poisoned(key):
    key_char = chr(key.c)
    if key_char == 'y':
        return {'poisoned': True}

    return {}

def reveal_map(key):
    key_char = chr(key.c)
    if key_char == 'm':
        return {'reveal_map': True}

def handle_increase_limb_damage(key):
    key_char = chr(key.c)
    if key_char == '/':
        return {'increase_limb_damage': True}

    return {}

def handle_decrease_limb_damage(key):
    key_char = chr(key.c)
    if key_char == '.':
        return {'decrease_limb_damage': True}

    return {}

def handle_player_dead_keys(key):
    key_char = chr(key.c)

    if key_char == 'i':
        return {'show_inventory': True}

    if key.vk == tc.KEY_ENTER and key.lalt:
        return {'fullscreen': True}
    elif key.vk == tc.KEY_ESCAPE:
        return {'exit': True}

    return {}

def handle_inventory_keys(key):
    index = key.c - ord('a')
    if index >= 0:
        return {'inventory_index': index}
    if key.vk == tc.KEY_ENTER and key.lalt:
        return {'fullscreen': True}
    elif key.vk == tc.KEY_ESCAPE:
        return {'exit': True}

    return {}

def handle_ranged_keys(key):
    index = key.c - ord('a')

    if index >= 0:
        return {'ranged_index': index}

    elif key.vk == tc.KEY_ESCAPE:
        return {'exit': True}

    return {}

def handle_main_menu(key):
    key_char = chr(key.c)

    if key_char == 'a':
        return {'new_game': True}
        # return {'show_tutorial': True}
    elif key_char == 'b':
        return {'load_game': True}
    elif key_char == 'c' or  key.vk == tc.KEY_ESCAPE:
        return {'exit': True}

    return {}

def handle_tutorial_menu(key):
    if key.vk == tc.KEY_ESCAPE:
        return {'close_tutorial': True}

    return {}

def handle_help_menu(key):
    if key.vk == tc.KEY_ESCAPE:
        return {'close_help_menu': True}

    return {}

def handle_level_up_menu(key):
    if key:
        key_char = chr(key.c)

        if key_char == 'a':
            return {'level_up': 'hp'}
        elif key_char == 'b':
            return {'level_up': 'str'}
        elif key_char == 'c':
            return {'level_up': 'def'}

    return {}

def handle_character_screen(key):
    if key.vk == tc.KEY_ESCAPE:
        return {'exit': True}

    return {}

def handle_mouse(mouse):
    (x, y) = (mouse.cx, mouse.cy)

    if mouse.lbutton_pressed:
        return {'left_click': (x, y)}
    # elif mouse.rbutton_pressed:
    #     return {'right_click': (x, y)}

    return {}

def handle_mouse_teleport(mouse):
    (x, y) = (mouse.cx, mouse.cy)
    
    if mouse.rbutton_pressed:
        return {'mouse_teleport': (x, y)}

    return {}

def spawn_enemy_at(key):
    if key.vk == tc.KEY_SPACE:
        return {'spawn_enemy_at': True}

    return {}