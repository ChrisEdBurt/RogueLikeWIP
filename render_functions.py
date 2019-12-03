import tcod as tc

from enum import Enum, auto
from game_states import GameStates
from menus import character_screen, inventory_menu, level_up_menu, ranged_menu
from components.fighter import Fighter
from components.mage import Mage

from game_messages import Message

class RenderOrder(Enum):
    STAIRS = auto()
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()

def get_names_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)

    for entity in entities:
        if entity.x == x and entity.y == y and tc.map_is_in_fov(fov_map, entity.x, entity.y) and entity.fighter != None:
            names = [entity.name for entity in entities if entity.x == x and entity.y == y and tc.map_is_in_fov(fov_map, entity.x, entity.y)]
            names = ''.join(names) + ' ' + Mage.get_stats(entity) + Fighter.get_stats(entity)
            return names

    else:
        names = [entity.name for entity in entities
            if entity.x == x and entity.y == y and tc.map_is_in_fov(fov_map, entity.x, entity.y)]
        names = ', '.join(names)

        return names.capitalize()

def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    tc.console_set_default_background(panel, back_color)
    tc.console_rect(panel, x + 16, y + 1, total_width, 1, False, tc.BKGND_SCREEN)

    tc.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        tc.console_rect(panel, x + 16, y + 1, bar_width, 1, False, tc.BKGND_SCREEN)

    # body_panel.default_fg(panel, tc.white)
    panel.default_fg = tc.white
    tc.console_print_ex(panel, int(x + total_width / 2) + 16, y + 1, tc.BKGND_NONE, tc.CENTER, '{0}: {1}/{2}'.format(name, value, maximum))
    
    tc.console_hline(panel, x - 1 , y - 1 , 133)
    tc.console_hline(panel, x - 1, y + 8, 133)    
    tc.console_vline(panel, x + 37, y, 8)
    # tc.console_vline(panel, x + 131, y, 8)

fov_recompute = False

def render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, screen_height,
               bar_width, panel_height, panel_y, mouse, colors, game_state):
    if fov_recompute:
    # Draw all the tiles in the game map
        for y in range(game_map.height):
            for x in range(game_map.width):

                visible = tc.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight

                if visible:
                    if wall:
                        tc.console_set_char_background(con, x, y, tc.darkest_red, tc.BKGND_SET)
                    else:
                        tc.console_set_char_background(con, x, y, tc.darkest_orange, tc.BKGND_SET)

                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored:
                    if wall:
                        tc.console_set_char_background(con, x, y, tc.darkest_grey, tc.BKGND_SET)
                    else:
                        tc.console_set_char_background(con, x, y, tc.darkest_sepia, tc.BKGND_SET)


    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

    # Draw all entities in the list
    for entity in entities_in_render_order:
        draw_entity(con, entity, fov_map, game_map)
        
    tc.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

    tc.console_set_default_background(panel, tc.black)
    panel.clear()
    # tc.console_clear(panel)

    # Print the game messages, one line at a time
    # y = 1
    y = 0

    for message in message_log.messages:
        # body_panel.default_fg(panel, message.color)
        panel.default_fg = message.color

        # tc.console_print_ex(panel, message_log.x + 15, y, tc.BKGND_NONE, tc.LEFT, message.text)
        tc.console_print_ex(panel, (screen_width - screen_width) + 54, y, tc.BKGND_NONE, tc.LEFT, message.text)
        y += 1
    
    render_bar(panel, 1 - 3, 1, bar_width, 'HP', player.fighter.hp, player.fighter.max_hp,tc.light_red, tc.darker_red)
    tc.console_print_ex(panel, 15, 5, tc.BKGND_NONE, tc.LEFT,'Dungeon level: {0}'.format(game_map.dungeon_level))
        
    # body_panel.default_fg(panel, tc.light_gray)
    panel.default_fg = tc.light_gray

    tc.console_blit(panel, 0, 0, screen_width, panel_height + 1, 0, 0, panel_y)

    mouse_display_panel = tc.console.Console(screen_width, 1)
    tc.console_print_ex(mouse_display_panel, 0, 0, tc.BKGND_NONE, tc.LEFT,get_names_under_mouse(mouse, entities, fov_map))
    tc.console_blit(mouse_display_panel, -13, 0, screen_width, panel_height + 1, 0, 0, panel_y - 1)

    head_list = list(str(player.fighter.head_hp))
    if player.fighter.head_hp < 100:
        head_list.insert(0,'0')
        if player.fighter.head_hp < 10:
            head_list.insert(0,'0')
            head_list.insert(0,'0')

    chest_list = list(str(player.fighter.chest_hp))
    if player.fighter.chest_hp < 100:
        chest_list.insert(0,'0')
        if player.fighter.chest_hp < 10:
            chest_list.insert(0,'0')
            chest_list.insert(0,'0')

    right_arm_list = list(str(player.fighter.right_arm_hp))
    if player.fighter.right_arm_hp < 100:
        right_arm_list.insert(0,'0')
        if player.fighter.right_arm_hp < 10:
            right_arm_list.insert(0,'0')
            right_arm_list.insert(0,'0')
    
    left_arm_list = list(str(player.fighter.left_arm_hp))
    if player.fighter.left_arm_hp < 100:
        left_arm_list.insert(0,'0')
        if player.fighter.left_arm_hp < 10:
            left_arm_list.insert(0,'0')
            left_arm_list.insert(0,'0')

    left_leg_list = list(str(player.fighter.left_leg_hp))
    if player.fighter.left_leg_hp < 100:
        left_leg_list.insert(0,'0')
        if player.fighter.left_leg_hp < 10:
            left_leg_list.insert(0,'0')
            left_leg_list.insert(0,'0')

    right_leg_list = list(str(player.fighter.right_leg_hp))
    if player.fighter.right_leg_hp < 100:
        right_leg_list.insert(0,'0')
        if player.fighter.right_leg_hp < 10:
            right_leg_list.insert(0,'0')
            right_leg_list.insert(0,'0')

    ##BODY HEALTH PANEL
    body_panel = tc.console.Console(13, 15)
    body_panel.draw_frame(0, 0, body_panel.width, body_panel.height - 1, " Body", False, fg=tc.white, bg=tc.black)
    
    #HEAD
    if int(player.fighter.head_hp) >= 75:
        body_panel.default_fg = tc.green
        body_panel.draw_frame(int(body_panel.width / 2) - 2, 1, 5, 4, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2), 3, tc.BKGND_NONE, tc.CENTER,'{0}'.format(head_list[0]+head_list[1]+head_list[2]))
    
    if int(player.fighter.head_hp) >= 50 and int(player.fighter.head_hp) <= 74:
        body_panel.default_fg  = tc.yellow
        body_panel.draw_frame(int(body_panel.width / 2) - 2, 1, 5, 4, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2), 3, tc.BKGND_NONE, tc.CENTER,'{0}'.format(head_list[0]+head_list[1]+head_list[2]))
    
    if int(player.fighter.head_hp) >= 26 and int(player.fighter.head_hp) <= 49:
        body_panel.default_fg = tc.orange
        body_panel.draw_frame(int(body_panel.width / 2) - 2, 1, 5, 4, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2), 3, tc.BKGND_NONE, tc.CENTER,'{0}'.format(head_list[0]+head_list[1]+head_list[2]))
    
    if int(player.fighter.head_hp) >= 11 and int(player.fighter.head_hp) <= 25:
        body_panel.default_fg = tc.red
        body_panel.draw_frame(int(body_panel.width / 2) - 2, 1, 5, 4, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2), 3, tc.BKGND_NONE, tc.CENTER,'{0}'.format(head_list[0]+head_list[1]+head_list[2]))
    
    if int(player.fighter.head_hp) <= 10:
        body_panel.default_fg= tc.grey
        body_panel.draw_frame(int(body_panel.width / 2) - 2, 1, 5, 4, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2), 3, tc.BKGND_NONE, tc.CENTER,'{0}'.format(head_list[0]+head_list[1]+head_list[2]))

    #TORSO
    if int(player.fighter.chest_hp) >= 75:
        body_panel.default_fg = tc.green
        body_panel.draw_frame(int(body_panel.width / 2) - 2, 4, 5, 5, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2), 5, tc.BKGND_NONE, tc.CENTER,'{0}'.format(chest_list[0]+"\n"+chest_list[1]+"\n"+chest_list[2]))
    
    if int(player.fighter.chest_hp) >= 50 and int(player.fighter.chest_hp) <= 74:
        body_panel.default_fg = tc.yellow
        body_panel.draw_frame(int(body_panel.width / 2) - 2, 4, 5, 5, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2), 5, tc.BKGND_NONE, tc.CENTER,'{0}'.format(chest_list[0]+"\n"+chest_list[1]+"\n"+chest_list[2]))
    
    if int(player.fighter.chest_hp) >= 26 and int(player.fighter.chest_hp) <= 49:
        body_panel.default_fg = tc.orange
        body_panel.draw_frame(int(body_panel.width / 2) - 2, 4, 5, 5, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2), 5, tc.BKGND_NONE, tc.CENTER,'{0}'.format(chest_list[0]+"\n"+chest_list[1]+"\n"+chest_list[2]))
   
    if int(player.fighter.chest_hp) >= 11 and int(player.fighter.chest_hp) <= 25:
        body_panel.default_fg = tc.red
        body_panel.draw_frame(int(body_panel.width / 2) - 2, 4, 5, 5, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2), 5, tc.BKGND_NONE, tc.CENTER,'{0}'.format(chest_list[0]+"\n"+chest_list[1]+"\n"+chest_list[2]))
    
    if int(player.fighter.chest_hp) <= 10:
        body_panel.default_fg = tc.grey
        body_panel.draw_frame(int(body_panel.width / 2) - 2, 4, 5, 5, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2), 5, tc.BKGND_NONE, tc.CENTER,'{0}'.format(chest_list[0]+"\n"+chest_list[1]+"\n"+chest_list[2]))

    ##ARMS
    ##LEFT
    if int(player.fighter.left_arm_hp) >= 75:
        body_panel.default_fg = tc.green
        body_panel.draw_frame(int(body_panel.width / 2) - 4, 4, 3, 5, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2) - 3, 5, tc.BKGND_NONE, tc.CENTER,'{0}'.format(left_arm_list[0]+"\n"+left_arm_list[1]+"\n"+left_arm_list[2]))  
    
    if int(player.fighter.left_arm_hp) >= 50 and int(player.fighter.left_arm_hp) <= 74:
        body_panel.default_fg  = tc.yellow
        body_panel.draw_frame(int(body_panel.width / 2) - 4, 4, 3, 5, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2) - 3, 5, tc.BKGND_NONE, tc.CENTER,'{0}'.format(left_arm_list[0]+"\n"+left_arm_list[1]+"\n"+left_arm_list[2]))  

    if int(player.fighter.left_arm_hp) >= 26 and int(player.fighter.left_arm_hp) <= 49:
        body_panel.default_fg = tc.orange
        body_panel.draw_frame(int(body_panel.width / 2) - 4, 4, 3, 5, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2) - 3, 5, tc.BKGND_NONE, tc.CENTER,'{0}'.format(left_arm_list[0]+"\n"+left_arm_list[1]+"\n"+left_arm_list[2]))

    if int(player.fighter.left_arm_hp) >= 11 and int(player.fighter.left_arm_hp) <= 25:
        body_panel.default_fg = tc.red
        body_panel.draw_frame(int(body_panel.width / 2) - 4, 4, 3, 5, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2) - 3, 5, tc.BKGND_NONE, tc.CENTER,'{0}'.format(left_arm_list[0]+"\n"+left_arm_list[1]+"\n"+left_arm_list[2])) 

    if int(player.fighter.left_arm_hp) <= 10:
        body_panel.default_fg = tc.grey
        body_panel.draw_frame(int(body_panel.width / 2) - 4, 4, 3, 5, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2) - 3, 5, tc.BKGND_NONE, tc.CENTER,'{0}'.format(left_arm_list[0]+"\n"+left_arm_list[1]+"\n"+left_arm_list[2])) 

    ##ARMS
    ##RIGHT
    if int(player.fighter.right_arm_hp) >= 75:
        body_panel.default_fg = tc.green
        body_panel.draw_frame(int(body_panel.width / 2) + 2, 4, 3, 5, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2) + 3, 5, tc.BKGND_NONE, tc.CENTER,'{0}'.format(right_arm_list[0]+"\n"+right_arm_list[1]+"\n"+right_arm_list[2]))  
    
    if int(player.fighter.right_arm_hp) >= 50 and int(player.fighter.right_arm_hp) <= 74:
        body_panel.default_fg = tc.yellow
        body_panel.draw_frame(int(body_panel.width / 2) + 2, 4, 3, 5, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2) + 3, 5, tc.BKGND_NONE, tc.CENTER,'{0}'.format(right_arm_list[0]+"\n"+right_arm_list[1]+"\n"+right_arm_list[2]))  

    if int(player.fighter.right_arm_hp) >= 26 and int(player.fighter.right_arm_hp) <= 49:
        body_panel.default_fg = tc.orange
        body_panel.draw_frame(int(body_panel.width / 2) + 2, 4, 3, 5, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2) + 3, 5, tc.BKGND_NONE, tc.CENTER,'{0}'.format(right_arm_list[0]+"\n"+right_arm_list[1]+"\n"+right_arm_list[2])) 

    if int(player.fighter.right_arm_hp) >= 11 and int(player.fighter.right_arm_hp) <= 25:
        body_panel.default_fg = tc.red
        body_panel.draw_frame(int(body_panel.width / 2) + 2, 4, 3, 5, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2) + 3, 5, tc.BKGND_NONE, tc.CENTER,'{0}'.format(right_arm_list[0]+"\n"+right_arm_list[1]+"\n"+right_arm_list[2])) 

    if int(player.fighter.right_arm_hp) <= 10:
        body_panel.default_fg = tc.grey
        body_panel.draw_frame(int(body_panel.width / 2) + 2, 4, 3, 5, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2) + 3, 5, tc.BKGND_NONE, tc.CENTER,'{0}'.format(right_arm_list[0]+"\n"+right_arm_list[1]+"\n"+right_arm_list[2])) 

    #LEGS
    #LEFT
    if int(player.fighter.left_leg_hp) >= 75:
        body_panel.default_fg = tc.green
        body_panel.draw_frame(int(body_panel.width / 2) - 2, 8, 3, 5, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2) + 1, 9, tc.BKGND_NONE, tc.CENTER,'{0}'.format(left_leg_list[0]+"\n"+left_leg_list[1]+"\n"+left_leg_list[2]))

    if int(player.fighter.left_leg_hp) >= 50 and int(player.fighter.left_leg_hp) <= 74:
        body_panel.default_fg = tc.yellow
        body_panel.draw_frame(int(body_panel.width / 2) - 2, 8, 3, 5, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2) + 1, 9, tc.BKGND_NONE, tc.CENTER,'{0}'.format(left_leg_list[0]+"\n"+left_leg_list[1]+"\n"+left_leg_list[2]))  

    if int(player.fighter.left_leg_hp) >= 26 and int(player.fighter.left_leg_hp) <= 49:
        body_panel.default_fg = tc.orange
        body_panel.draw_frame(int(body_panel.width / 2) - 2, 8, 3, 5, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2) + 1, 9, tc.BKGND_NONE, tc.CENTER,'{0}'.format(left_leg_list[0]+"\n"+left_leg_list[1]+"\n"+left_leg_list[2]))

    if int(player.fighter.left_leg_hp) >= 11 and int(player.fighter.left_leg_hp) <= 25:
        body_panel.default_fg = tc.red
        body_panel.draw_frame(int(body_panel.width / 2) - 2, 8, 3, 5, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2) + 1, 9, tc.BKGND_NONE, tc.CENTER,'{0}'.format(left_leg_list[0]+"\n"+left_leg_list[1]+"\n"+left_leg_list[2]))

    if int(player.fighter.left_leg_hp) <= 10:
        body_panel.default_fg = tc.grey
        body_panel.draw_frame(int(body_panel.width / 2) - 2, 8, 3, 5, "")
        tc.console_print_ex(body_panel, int(body_panel.width / 2) + 1, 9, tc.BKGND_NONE, tc.CENTER,'{0}'.format(left_leg_list[0]+"\n"+left_leg_list[1]+"\n"+left_leg_list[2]))

    #LEGS
    #RIGHT
    if int(player.fighter.right_leg_hp) >= 75:
        body_panel.default_fg = tc.green
        body_panel.draw_frame(int(body_panel.width / 2), 8, 3, 5, "", False)
        tc.console_print_ex(body_panel, int(body_panel.width / 2) - 1, 9, tc.BKGND_NONE, tc.CENTER,'{0}'.format(right_leg_list[0]+"\n"+right_leg_list[1]+"\n"+right_leg_list[2]))

    if int(player.fighter.right_leg_hp) >= 50 and int(player.fighter.right_leg_hp) <= 74:
        body_panel.default_fg = tc.yellow
        body_panel.draw_frame(int(body_panel.width / 2), 8, 3, 5, "", False)
        tc.console_print_ex(body_panel, int(body_panel.width / 2) - 1, 9, tc.BKGND_NONE, tc.CENTER,'{0}'.format(right_leg_list[0]+"\n"+right_leg_list[1]+"\n"+right_leg_list[2]))

    if int(player.fighter.right_leg_hp) >= 26 and int(player.fighter.right_leg_hp) <= 49:
        body_panel.default_fg = tc.orange
        body_panel.draw_frame(int(body_panel.width / 2), 8, 3, 5, "", False)
        tc.console_print_ex(body_panel, int(body_panel.width / 2) - 1, 9, tc.BKGND_NONE, tc.CENTER,'{0}'.format(right_leg_list[0]+"\n"+right_leg_list[1]+"\n"+right_leg_list[2]))

    if int(player.fighter.right_leg_hp) >= 11 and int(player.fighter.right_leg_hp) <= 25:
        body_panel.default_fg = tc.red
        body_panel.draw_frame(int(body_panel.width / 2), 8, 3, 5, "", False)
        tc.console_print_ex(body_panel, int(body_panel.width / 2) - 1, 9, tc.BKGND_NONE, tc.CENTER,'{0}'.format(right_leg_list[0]+"\n"+right_leg_list[1]+"\n"+right_leg_list[2]))

    if int(player.fighter.right_leg_hp) <= 10:
        body_panel.default_fg = tc.grey
        body_panel.draw_frame(int(body_panel.width / 2), 8, 3, 5, "", False)
        tc.console_print_ex(body_panel, int(body_panel.width / 2) - 1, 9, tc.BKGND_NONE, tc.CENTER,'{0}'.format(right_leg_list[0]+"\n"+right_leg_list[1]+"\n"+right_leg_list[2]))

    tc.console_blit(body_panel, 0, 0, body_panel.width, body_panel.height, 0, 0, screen_height - body_panel.height + 1, 1.0, 1.0)


    ##BODY POISON/BURNING PANEL
    status_panel = tc.console.Console(18, 11)
    status_panel.draw_frame(0, 0, status_panel.width, status_panel.height - 1, "Status", False, fg=tc.white, bg=tc.black)
    tc.console_print_ex(status_panel, int(body_panel.width / 2 + 3), 3, tc.BKGND_NONE, tc.CENTER,'Hunger {0}/100'.format(player.fighter.hunger_level))
    tc.console_print_ex(status_panel, int(body_panel.width / 2 + 3), 4, tc.BKGND_NONE, tc.CENTER,'Thirst {0}/100'.format(player.fighter.thirst_level))

    if player.fighter.is_burning == True:
        status_panel.default_fg = tc.red
        tc.console_print_ex(status_panel, int(body_panel.width / 2 + 3), 6, tc.BKGND_NONE, tc.CENTER,'BURNING')
    else:
        status_panel.default_fg =  tc.black
        tc.console_print_ex(status_panel, int(body_panel.width / 2 + 3), 6, tc.BKGND_NONE, tc.CENTER,'BURNING')

    if player.fighter.is_poisoned == True:
        status_panel.default_fg = tc.green
        tc.console_print_ex(status_panel, int(body_panel.width / 2 + 3), 7, tc.BKGND_NONE, tc.CENTER,'POISONED')
    else:
        status_panel.default_fg = tc.black
        tc.console_print_ex(status_panel, int(body_panel.width / 2 + 3), 7, tc.BKGND_NONE, tc.CENTER,'POISONED')

    tc.console_blit(status_panel, 0, 0, status_panel.width, status_panel.height, 0, (screen_width - screen_width) + 35, screen_height - status_panel.height + 1, 1.0, 1.0)

    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        inventory_menu(con, player, 98, screen_width, screen_height)

    if game_state == GameStates.RANGED:
        if game_state == GameStates.RANGED:
            ranged_title = 'Press the key next to the ranged item you want to use, or Esc to cancel\n\n\nName               |Damage|Range|Charge|\n'
        else:
            ranged_title = 'Press the key next to the ranged item you want to use, or Esc to cancel\n\n\nName               |Damage|Range|Charge|\n'

        ranged_menu(con, ranged_title, player, 98, screen_width, screen_height)

    elif game_state == GameStates.LEVEL_UP:
        level_up_menu(con, 'Level up! Choose a stat to raise:', player, 40, screen_width, screen_height)

    elif game_state == GameStates.CHARACTER_SCREEN:
        character_screen(player, 30, 10, screen_width, screen_height)

def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)

def draw_entity(con, entity, fov_map, game_map):
   if tc.map_is_in_fov(fov_map, entity.x, entity.y) or (entity.stairs and game_map.tiles[entity.x][entity.y].explored) or (entity.area):
        con.default_fg = entity.color
        tc.console_put_char(con, entity.x, entity.y, entity.char, tc.BKGND_NONE)

def draw_overworld(con, entity, fov_map, game_map):
    con.default_fg =  entity.color
    tc.console_put_char(con, entity.x, entity.y, entity.char, tc.BKGND_NONE)

def clear_entity(con, entity):
    # erase the character that represents this object
    tc.console_put_char(con, entity.x, entity.y, ' ', tc.BKGND_NONE)