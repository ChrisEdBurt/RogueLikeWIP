import tcod as tc

import tcod.event
import tcod.map

import json
from random import randint

from death_functions import kill_monster, kill_player
from entity import get_blocking_entities_at_location, spawn_enemy, cycle_target_distance_to
from fov_functions import initialize_fov, recompute_fov
from game_messages import Message
from game_states import GameStates
from input_handlers import handle_keys, handle_mouse, handle_main_menu, handle_tutorial_menu, handle_mouse_teleport, handle_help_menu
from loader_functions.initialize_new_game import get_constants, get_game_variables
from loader_functions.data_loaders import load_game, save_game, load_json
from menus import main_menu, message_box, tutorial_menu, help_menu
from render_functions import clear_all, render_all
from loader_functions.data_loaders import load_json
from components.fighter import Fighter
from components.mage import Mage

def play_game(player, entities, game_map, message_log, game_state, con, panel, constants):
    
    fov_recompute = True
    fov_map = initialize_fov(game_map)
    key = tc.Key()
    mouse = tc.Mouse()
    targeting_item = None
    visible_enemies = []
    room_enemies_index = 0
    room_enemies_length = 0
    event = tc.event.get()
    
    while event != "QUIT":
    # while not tc.console_is_window_closed():
        tc.sys_check_for_event(tc.EVENT_KEY_PRESS | tc.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, constants['fov_radius'], constants['fov_light_walls'],
                          constants['fov_algorithm'])

        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log,
                   constants['screen_width'], constants['screen_height'], constants['bar_width'],
                   constants['panel_height'], constants['panel_y'], mouse, constants['colors'], game_state)

        fov_recompute = False
        tc.console_flush()
        clear_all(con, entities)

        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)
        mouse_teleport_action = handle_mouse_teleport(mouse)

        move = action.get('move')
        wait = action.get('wait')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')
        ranged_index = action.get('ranged_index')
        take_stairs = action.get('take_stairs')
        level_up = action.get('level_up')
        show_character_screen = action.get('show_character_screen')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')
        god_mode = action.get('god_mode')
        show_help_menu = action.get('show_help_menu')
        close_help_menu = action.get('close_help_menu')
        cycle_target = action.get('cycle_target')
        cycle_target_right = action.get('right_target')
        cycle_target_left = action.get('left_target')
        poisoned = action.get('poisoned')
        burning = action.get('burning')
        reveal_map = action.get('reveal_map')
        decrease_limb_damage = action.get('decrease_limb_damage')
        increase_limb_damage = action.get('increase_limb_damage')
        teleport = action.get('teleport')
        mouse_teleport = mouse_teleport_action.get('mouse_teleport')
        ranged = action.get('ranged')
        spawn_enemy_at = action.get('spawn_enemy_at')
        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        player_turn_results = []

        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)
                    fov_recompute = True


                if player.fighter.turns_since_special <= 5:
                    player.fighter.turns_since_special += 1

                game_state = GameStates.ENEMY_TURN

        elif wait:

            if player.fighter.turns_since_special <= 5:
                player.fighter.turns_since_special += 1

            game_state = GameStates.ENEMY_TURN

        elif pickup and game_state == GameStates.PLAYERS_TURN:
            
            for entity in entities:
                
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)

                    break
            else:
                message_log.add_message(Message('There is nothing here to pick up.', tc.yellow))

        if show_inventory:
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if show_help_menu:
            previous_game_state = game_state
            game_state = GameStates.SHOW_HELP_MENU

        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(player.inventory.items):
            item = player.inventory.items[inventory_index]

            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        if ranged_index is not None and previous_game_state != GameStates.PLAYER_DEAD and ranged_index < len(player.inventory.items):
            item = player.inventory.items[ranged_index]

            if game_state == GameStates.RANGED:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))

        if take_stairs and game_state == GameStates.PLAYERS_TURN:
            
            for entity in entities:
                
                if entity.stairs and entity.x == player.x and entity.y == player.y and entity.stairs.direction == 'down':
                    entities = game_map.next_floor(player, message_log, constants)
                    fov_map = initialize_fov(game_map)
                    fov_recompute = True
                    con.clear()
                    break

                elif entity.stairs and entity.x == player.x and entity.y == player.y and entity.stairs.direction == 'up':
                    entities = game_map.previous_floor(player, message_log, constants)
                    fov_map = initialize_fov(game_map)
                    fov_recompute = True
                    con.clear()
                    break

                elif entity.area and entity.x == player.x and entity.y == player.y:
                    entities = game_map.load_area(player, message_log, constants)
                    fov_map = initialize_fov(game_map)
                    fov_recompute = True
                    con.clear()
                    break

            else:
                message_log.add_message(Message('There are no stairs here.', tc.yellow))
 
        if cycle_target:
            previous_game_state = game_state
            game_state = GameStates.CYCLE_TARGET
            visible_enemies.clear()

            for entity in entities:
                
                if entity.ai != None:
                    
                    if tc.map_is_in_fov(fov_map, entity.x, entity.y):
                        visible_enemies.append([cycle_target_distance_to(player, entity),entity.x, entity.y, entity.name])

            if len(visible_enemies) != 0:
                con.default_fg = tc.black
                con.default_fg = tc.white
                con.print(int(constants['screen_width'] / 2), 1, 'Press RIGHT arrow or LEFT arrow key to cycle targets or ESCAPE to cancel targeting'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
                tc.console_blit(con, 0, 0, constants['screen_width'], constants['screen_height'], 0, 0, 0)
                visible_enemies.sort()  
                room_enemies_length = len(visible_enemies)

            else:
                con.print(int(constants['screen_width'] / 2), 1, 'There are no enemies present! Press ESCAPE to cancel targeting'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)

        if cycle_target_right:
            
            if len(visible_enemies) != 0:    
                fov_recompute = True
                
                con.clear()
                con.default_fg = tc.black
                con.default_fg = tc.white
                
                con.print(int(constants['screen_width'] / 2), 1, 'Press RIGHT arrow or LEFT arrow key to cycle targets or ESCAPE to cancel targeting'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
                tc.console_blit(con, 0, 0, constants['screen_width'], constants['screen_height'], 0, 0, 0)
                
                con.draw_frame((visible_enemies[room_enemies_index][1]) - 1, (visible_enemies[room_enemies_index][2]) - 1 , 3, 3, "", True, fg=tc.white, bg=tc.black)
                con.print((visible_enemies[room_enemies_index][1]) + 1, (visible_enemies[room_enemies_index][2]) - 2, '{0}'.format(visible_enemies[room_enemies_index][3]), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)

                for entity in entities:
                    
                    if tc.map_is_in_fov(fov_map, entity.x, entity.y):
                       
                        if visible_enemies[room_enemies_index][3] == entity.name:
                                names = entity.name
                                names = names + ' ' + Mage.get_stats(entity) + Fighter.get_stats(entity)
                                con.print((visible_enemies[room_enemies_index][1]) + 1, (visible_enemies[room_enemies_index][2]) - 2, '{0}'.format(names, tc.white), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)

                if room_enemies_index == room_enemies_length - 1:
                    room_enemies_index = 0
                
                else:
                    room_enemies_index += 1

        if cycle_target_left:
            
            if len(visible_enemies) != 0:  
                fov_recompute = True

                con.clear()

                con.default_fg = tc.black
                con.default_fg = tc.white
                con.print(int(constants['screen_width'] / 2), 1, 'Press RIGHT arrow or LEFT arrow key to cycle targets or ESCAPE to cancel targeting'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
                
                tc.console_blit(con, 0, 0, constants['screen_width'], constants['screen_height'], 0, 0, 0)
                con.draw_frame((visible_enemies[room_enemies_index][1]) - 1, (visible_enemies[room_enemies_index][2]) - 1 , 3, 3, "", True, fg=tc.white, bg=tc.black)
                con.print((visible_enemies[room_enemies_index][1]) + 1, (visible_enemies[room_enemies_index][2]) - 2, '{0}'.format(visible_enemies[room_enemies_index][3]), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)

                for entity in entities:
                    
                    if tc.map_is_in_fov(fov_map, entity.x, entity.y):
                        
                        if visible_enemies[room_enemies_index][3] == entity.name:
                                names = entity.name
                                names = names + ' ' + Mage.get_stats(entity) + Fighter.get_stats(entity)
                                con.print((visible_enemies[room_enemies_index][1]) + 1, (visible_enemies[room_enemies_index][2]) - 2, '{0}'.format(names, tc.white), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)

                if room_enemies_index == 0:
                    room_enemies_index = room_enemies_length - 1
                
                else:
                    room_enemies_index -= 1

        if god_mode:
            player.fighter.hp = 2500
        
        if poisoned:
            
            if player.fighter.is_poisoned == False:
                player.fighter.is_poisoned = True
                player.fighter.poison_turns_remaining = 5
                player.color = tc.green

        if burning:
            
            if player.fighter.is_burning == False:
                player.fighter.is_burning = True
                player.fighter.burning_turns_remaining = 5
                player.color = tc.red

        if reveal_map:            
            
            if constants['fov_radius'] == 8:
                constants['fov_radius'] = 250
                
                for i in range(len(game_map.tiles)):
                    
                    for j in range(len(game_map.tiles[i])):
                        
                        if not game_map.tiles[i][j].blocked:
                            game_map.tiles[i][j].explored = True
                            game_map.tiles[i][j].block_sight = False
                        
                fov_map = initialize_fov(game_map)
                fov_recompute = True

                con.default_fg = tc.black
                con.default_fg = tc.white

                for entity in entities:
                    #ALL ENTITIES
                    # con.draw_frame(entity.x - 1, entity.y - 1 , 3, 3, "", False, fg=tc.black, bg=tc.black) 
                    #ENEMIES ONLY
                    if entity.ai != None:
                        #ENEMY SEEING POWER
                        con.draw_frame(entity.x - 1, entity.y - 1 , 3, 3, "", False, fg=tc.black, bg=tc.black) 

            elif constants['fov_radius'] != 8:
                constants['fov_radius'] = 8

                fov_recompute = True
                con.clear()

        if spawn_enemy_at:
            mouse_x = mouse.cx
            mouse_y =  mouse.cy
            spawn_enemy(mouse_x, mouse_y, entities, game_map.dungeon_level)
            
        if increase_limb_damage:
            player.fighter.take_limb_damge(randint(1, 12))

        if decrease_limb_damage:
            player.fighter.heal(randint(1, 12))
            
        if teleport:
            
            for entity in entities:
                
                if entity.name == "Stairs Down":
                    player.x = entity.x
                    player.y = entity.y + 1

        if mouse_teleport:
            player.x = mouse.cx
            player.y = mouse.cy

        if ranged:
            previous_game_state = game_state
            game_state = GameStates.RANGED  

        if level_up:
            
            if level_up == 'hp':
                player.fighter.base_max_hp += 20
                player.fighter.hp += 20
            
            elif level_up == 'str':
                player.fighter.base_strength += 1
            
            elif level_up == 'def':
                player.fighter.base_defense += 1

            game_state = previous_game_state

        if show_character_screen:
            previous_game_state = game_state
            game_state = GameStates.CHARACTER_SCREEN

        if game_state == GameStates.TARGETING:
            
            if left_click: 
                target_x, target_y = left_click
                item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map, target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)

            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        if exit:
            
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.CHARACTER_SCREEN, GameStates.RANGED, GameStates.TARGETING, GameStates.SHOW_TUTORIAL, GameStates.SHOW_HELP_MENU):
                game_state = previous_game_state
            
            elif game_state == GameStates.CYCLE_TARGET:
                game_state = previous_game_state
                con.clear()
                clear_all(con, entities)
                fov_map = initialize_fov(game_map)
                fov_recompute = True
                con.clear()

            elif game_state == GameStates.TARGETING:
                game_state = previous_game_state
                player_turn_results.append({'targeting_cancelled': True})
                con.clear()
                clear_all(con, entities)
                fov_map = initialize_fov(game_map)
                fov_recompute = True
                con.clear()

            else:
                save_game(player, entities, game_map, message_log, game_state)

                return True

        if fullscreen:
            tc.console_set_fullscreen(not tc.console_is_fullscreen())

        for player_turn_result in player_turn_results:
            
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            equip = player_turn_result.get('equip')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')
            xp = player_turn_result.get('xp')
            god_mode = player_turn_result.get('god_mode')

            if message:
                message_log.add_message(message)

            if dead_entity:
                
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)

                else:
                    message = kill_monster(dead_entity)
                    last_index = len(entities)
                    pre_dead_name = dead_entity.name.replace('remains of ', '')

                    if dead_entity.inventory != None:
                        
                        for items in dead_entity.inventory.items:
                            items.x = dead_entity.x
                            items.y = dead_entity.y
                            entities.insert(last_index, items)
                            message_log.add_message(Message('{0}'.format(pre_dead_name) + ' dropped' + ' {0}'.format(items.name)))

                message_log.add_message(message)

            if item_added:
                entities.remove(item_added)

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if item_dropped:
                entities.append(item_dropped)

            if equip:
                equip_results = player.equipment.toggle_equip(equip)

                for equip_result in equip_results:
                    equipped = equip_result.get('equipped')
                    unequipped = equip_result.get('unequipped')
                    failed = equip_result.get('failed')

                    if equipped:
                        message_log.add_message(Message('You equipped the {0}'.format(equipped.name)))

                    if unequipped:
                        message_log.add_message(Message('You unequipped the {0}'.format(unequipped.name)))

                    if failed:
                        message_log.add_message(Message('You failed to equip the {0} due to your injuries'.format(failed.name)))

                game_state = GameStates.ENEMY_TURN

            if targeting:
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING
                targeting_item = targeting
                message_log.add_message(targeting_item.item.targeting_message)

            if targeting_cancelled:
                game_state = previous_game_state
                message_log.add_message(Message('Targeting cancelled'))

            if xp:
                leveled_up = player.level.add_xp(xp)
                message_log.add_message(Message('You gain {0} experience points.'.format(xp)))

                if leveled_up:
                    previous_game_state = game_state
                    game_state = GameStates.LEVEL_UP

        if game_state == GameStates.ENEMY_TURN:
            
            for entity in entities:

                if entity.ai:
                    # #TRACK ENEMY SPECIAL TURNS
                    # if tc.map_is_in_fov(fov_map, entity.x, entity.y):
                    #     print(entity.name + ":" + " " + str(entity.fighter.turns_since_special))
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                    if entity.fighter.is_poisoned == True:
                        message = entity.fighter.take_poison_damage()
                        message_log.add_message(message)

                    elif entity.fighter.is_burning == True:
                        message = entity.fighter.take_burning_damage()
                        message_log.add_message(message)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break
            else:

                if player.fighter.is_poisoned == True:
                    message = player.fighter.take_poison_damage()
                    message_log.add_message(message)

                elif player.fighter.is_burning == True:                   
                    message = player.fighter.take_burning_damage()
                    message_log.add_message(message)

                game_state = GameStates.PLAYERS_TURN

        if game_state == GameStates.SHOW_TUTORIAL:           
            action = handle_tutorial_menu(key)
            close_tutorial = action.get('close_tutorial')

            if close_tutorial:
                con.clear()
                clear_all(con, entities)
                fov_map = initialize_fov(game_map)
                fov_recompute = True
                con.clear()
                game_state = GameStates.PLAYERS_TURN

        if game_state == GameStates.SHOW_HELP_MENU:       
            action = handle_help_menu(key)
            close_help_menu = action.get('close_help_menu')

            if close_help_menu:
                con.clear()
                clear_all(con, entities)
                fov_map = initialize_fov(game_map)
                fov_recompute = True
                con.clear()
                game_state = GameStates.PLAYERS_TURN


def main():    
    constants = get_constants()
    tc.console_set_custom_font('arial10x10.png', tc.FONT_TYPE_GREYSCALE | tc.FONT_LAYOUT_TCOD)       
    tc.console.Console(constants['screen_width'], constants['screen_height'])
    tc.console_init_root(constants['screen_width'], constants['screen_height'], constants['window_title'], 
        False, tc.RENDERER_SDL2, "F", True)

    con = tc.console.Console(constants['screen_width'], constants['screen_height'])
    panel = tc.console.Console(constants['screen_width'], constants['screen_height'])
    
    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_error_message = False

    # main_menu_background_image = tc.image_load('menu_background.png')
    main_menu_background_image = tc.image_load('')

    key = tc.Key()
    mouse = tc.Mouse()

    event = tc.event.get()
    
    # for event in tcod.event.wait():
    while event != "QUIT":
        tc.sys_check_for_event(tc.EVENT_KEY_PRESS | tc.EVENT_MOUSE, key, mouse)

        if show_main_menu:
            con.clear()
            clear_all(con, entities)
            tc.console_blit(con, 0, 0, constants['screen_width'], constants['screen_height'], 0, 0, 0, 1.0, 1.0)
            main_menu(con, main_menu_background_image, constants['screen_width'],constants['screen_height'])

            if show_load_error_message:
                message_box(con, 'No save game to load', 50, constants['screen_width'], constants['screen_height'])

            tc.console_flush()
            action = handle_main_menu(key)
            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            exit_game = action.get('exit')

            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False
            
            elif new_game:
                player, entities, game_map, message_log, game_state = get_game_variables(constants)
                show_main_menu = False
                #REVERT BEFORE COMMIT
                # game_state = GameStates.SHOW_TUTORIAL
                game_state = GameStates.PLAYERS_TURN

            elif load_saved_game:
                
                try:
                    player, entities, game_map, message_log, game_state = load_game()
                    show_main_menu = False
                
                except FileNotFoundError:
                    show_load_error_message = True
            
            elif exit_game:
                break

        else:
            con.clear()
            play_game(player, entities, game_map, message_log, game_state, con, panel, constants)
            show_main_menu = True

if __name__ == '__main__':
    main()
