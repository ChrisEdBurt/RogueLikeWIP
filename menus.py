import tcod as tc

def menu(con, header, options, width, screen_width, screen_height):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    # calculate total height for the header (after auto-wrap) and one line per option
    header_height = tc.console_get_height_rect(con, 0, 0, width, screen_height, header)
    height = len(options) + header_height

    # create an off-screen console that represents the menu's window
    window = tc.console_new(width, height)

    # print the header, with auto-wrap
    tc.console_print_rect_ex(window, 0, 0, width, height, tc.BKGND_NONE, tc.LEFT, header)

    # print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        tc.console_print_ex(window, 0, y, tc.BKGND_NONE, tc.LEFT, text)
        y += 1
        letter_index += 1

    # blit the contents of "window" to the root console
    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)
    tc.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

def ranged_menu(con, header, player, inventory_width, screen_width, screen_height):
    # show a menu with each item of the ranged items as an option
    if len(player.inventory.items) == 0:
        options = ['Inventory is empty.']

    else:
        options = []
        myList = []

        for item in player.inventory.items:
            if item.item.ranged == True:

                myList.clear()
                for i in range(inventory_width):
                    myList.append('')

                newString = ""
                myList.insert(0, item.name)
                myList.insert(2,'|')
                myList.insert(3, item.item.function_kwargs.get('maximum_range'))
                myList.insert(10,'|')
                myList.insert(11, item.item.function_kwargs.get('damage'))
                myList.insert(16,'|')
                myList.insert(17, item.item.uses)  
                myList.insert(24,'|')             
                newString = ' '.join(map(str, myList))
                options.append(newString)

            elif item.equippable:
                options.append(item.name)

    menu(con, header, options, inventory_width, screen_width, screen_height)

def inventory_menu(con, player, inventory_width, screen_width, screen_height):
    width = inventory_width + 15
    height = len(player.inventory.items) + 11

    if height <= 10:
        height = 11

    dest_x = 0
    dest_y = 0

    y = 1
    text_y = 8
    
    name_origin = 5
    equip_origin = 28
    damage_origin = 35
    defense_origin = 41
    intelligence_origin = 47
    range_origin = 53
    charge_origin = 59

    x = int(screen_width / 2 - (inventory_width / 4) - 5)
    y = int(screen_height / 4)
    
    secondary = tc.console.Console(inventory_width - 31, height)

    secondary.draw_frame(dest_x, dest_y, inventory_width - 31, height, "Inventory", False, fg=tc.white, bg=tc.black)

    secondary.draw_frame(1, 5, inventory_width - 33 , 3, "", False, fg=tc.white, bg=tc.black)
    secondary.draw_frame(1, 5, inventory_width - 33, height - 6, "", False, fg=tc.white, bg=tc.black)
    
    secondary.print_box((int(inventory_width / 6) - 3), 2, 40, 2,"Press a letter to equip/unequip or use the corresponding item.", fg=tc.white, bg=None, alignment = tc.CENTER)

    secondary.print_box(name_origin, 6, 10, 1," NAME ", fg=tc.white, bg=None, alignment = tc.CENTER)
    secondary.print_box(equip_origin + 1, 6, 6, 1,"| EQU  ", fg=tc.white, bg=None, alignment = tc.CENTER)
    secondary.print_box(damage_origin, 6, 5, 1,"| DAM ", fg=tc.white, bg=None, alignment = tc.CENTER)
    secondary.print_box(defense_origin, 6, 5, 1,"| DEF ", fg=tc.white, bg=None, alignment = tc.CENTER)
    secondary.print_box(intelligence_origin, 6, 5, 1,"| INT ", fg=tc.white, bg=None, alignment = tc.CENTER)
    secondary.print_box(range_origin, 6, 5, 1,"| RNG ", fg=tc.white, bg=None, alignment = tc.CENTER)
    secondary.print_box(charge_origin, 6, 5, 1,"| USE ", fg=tc.white, bg=None, alignment = tc.CENTER)

    letter_index = ord('a')
    
    for items in player.inventory.items:    
    
        index = player.inventory.items.index(items)
    
        if items.equippable != None:

            if items.equippable.slot.name == 'HEAD_ARMOUR' and items is player.equipment.head_armour and len(player.inventory.items) > 1:
                if index != 0:
                    player.inventory.items.insert(0, items)
                    player.inventory.items.pop(index + 1)

            if items.equippable.slot.name == 'CHEST_ARMOUR' and items == player.equipment.chest_armour and len(player.inventory.items) > 1:
                if index != 1:
                    player.inventory.items.insert(1, items)
                    player.inventory.items.pop(index + 1)

            if items.equippable.slot.name == 'MAIN_HAND' and items == player.equipment.main_hand and len(player.inventory.items) > 1:
                if index != 2:
                    player.inventory.items.insert(2, items)
                    player.inventory.items.pop(index + 1)

            # if items.equippable.slot.name == 'BOTH_HAND' and items == player.equipment.both_hand and len(player.inventory.items) > 1:
            #     if index != 2:
            #         player.inventory.items.insert(2, items)
            #         player.inventory.items.pop(index + 1)

            # if items.equippable.slot.name == 'OFF_HAND' and items == player.equipment.off_hand and len(player.inventory.items) > 1:
            #     if index != 3:
            #         player.inventory.items.insert(3, items)
            #         player.inventory.items.pop(index + 1)

            if items.equippable.slot.name == 'OFF_HAND' and items == player.equipment.off_hand and len(player.inventory.items) > 1:
                if index != 3:
                    player.inventory.items.insert(3, items)
                    player.inventory.items.pop(index + 1)
            
            if items.equippable.slot.name == 'BOTH_HAND' and items == player.equipment.both_hand and len(player.inventory.items) > 1:
                if index != 4:
                    player.inventory.items.insert(4, items)
                    player.inventory.items.pop(index + 1)

    for item in player.inventory.items:

        if player.equipment.main_hand == item:
            text = '(' + chr(letter_index) + ') '
            secondary.print_box(2, text_y, len(text), 1, text, fg=tc.white, bg=None, alignment=tc.LEFT)
            secondary.print_box(name_origin + 1, text_y, len(item.name), 1, item.name, fg=tc.white, bg=None, alignment=tc.LEFT)
            secondary.print_box(equip_origin + 3, text_y, 4, 1, 'MAIN', fg=tc.white, bg=None, alignment=tc.CENTER)
            secondary.print_box(damage_origin + 1, text_y, 5, 1, str(item.equippable.strength_bonus), fg=tc.white, bg=None, alignment=tc.CENTER)
            if item.equippable.intelligence_bonus != 0:
                secondary.print_box(intelligence_origin + 1, text_y, 5, 1, str(item.equippable.intelligence_bonus), fg=tc.white, bg=None, alignment=tc.CENTER)
            text_y += 1
            letter_index += 1
                
        elif player.equipment.off_hand == item:
            text = '(' + chr(letter_index) + ') '
            secondary.print_box(2, text_y, len(text), 1, text, fg=tc.white, bg=None, alignment=tc.LEFT)
            secondary.print_box(name_origin + 1, text_y, len(item.name), 1, item.name, fg=tc.white, bg=None, alignment=tc.LEFT)
            secondary.print_box(equip_origin + 3, text_y, 4, 1, 'OFFH', fg=tc.white, bg=None, alignment=tc.CENTER)
            secondary.print_box(defense_origin + 1, text_y, 5, 1, str(item.equippable.defense_bonus), fg=tc.white, bg=None, alignment=tc.CENTER)
            if item.equippable.intelligence_bonus != 0:
                secondary.print_box(intelligence_origin + 1, text_y, 5, 1, str(item.equippable.intelligence_bonus), fg=tc.white, bg=None, alignment=tc.CENTER)
            text_y += 1
            letter_index += 1

        elif player.equipment.both_hand == item:
            text = '(' + chr(letter_index) + ') '
            secondary.print_box(2, text_y, len(text), 1, text, fg=tc.white, bg=None, alignment=tc.LEFT)
            secondary.print_box(name_origin + 1, text_y, len(item.name), 1, item.name, fg=tc.white, bg=None, alignment=tc.LEFT)
            secondary.print_box(equip_origin + 3, text_y, 4, 1, 'BOTH', fg=tc.white, bg=None, alignment=tc.CENTER)
            secondary.print_box(damage_origin + 1, text_y, 5, 1, str(item.equippable.strength_bonus), fg=tc.white, bg=None, alignment=tc.CENTER)
            secondary.print_box(defense_origin + 1, text_y, 5, 1, str(item.equippable.defense_bonus), fg=tc.white, bg=None, alignment=tc.CENTER)
            if item.equippable.intelligence_bonus != 0:
                secondary.print_box(intelligence_origin + 1, text_y, 5, 1, str(item.equippable.intelligence_bonus), fg=tc.white, bg=None, alignment=tc.CENTER)
            text_y += 1
            letter_index += 1

        elif player.equipment.head_armour == item:
            text = '(' + chr(letter_index) + ') '
            secondary.print_box(2, text_y, len(text), 1, text, fg=tc.white, bg=None, alignment=tc.LEFT)
            secondary.print_box(name_origin + 1, text_y, len(item.name), 1, item.name, fg=tc.white, bg=None, alignment=tc.LEFT)
            secondary.print_box(equip_origin + 3, text_y, 4, 1, 'HEAD', fg=tc.white, bg=None, alignment=tc.CENTER)
            secondary.print_box(defense_origin + 1, text_y, 5, 1, str(item.equippable.defense_bonus), fg=tc.white, bg=None, alignment=tc.CENTER)
            if item.equippable.intelligence_bonus != 0:
                secondary.print_box(intelligence_origin + 1, text_y, 5, 1, str(item.equippable.intelligence_bonus), fg=tc.white, bg=None, alignment=tc.CENTER)
            text_y += 1
            letter_index += 1

        elif player.equipment.chest_armour == item:
            text = '(' + chr(letter_index) + ') '
            secondary.print_box(2, text_y, len(text), 1, text, fg=tc.white, bg=None, alignment=tc.LEFT)
            secondary.print_box(name_origin + 1, text_y, len(item.name), 1, item.name, fg=tc.white, bg=None, alignment=tc.LEFT)
            secondary.print_box(equip_origin + 3, text_y, 4, 1, 'CHST', fg=tc.white, bg=None, alignment=tc.CENTER)
            secondary.print_box(defense_origin + 1, text_y, 5, 1, str(item.equippable.defense_bonus), fg=tc.white, bg=None, alignment=tc.CENTER)
            if item.equippable.intelligence_bonus != 0:
                secondary.print_box(intelligence_origin + 1, text_y, 5, 1, str(item.equippable.intelligence_bonus), fg=tc.white, bg=None, alignment=tc.CENTER)
            text_y += 1
            letter_index += 1

        elif item.equippable:
            if item.equippable.strength_bonus == 0:
                text = '(' + chr(letter_index) + ') '
                secondary.print_box(2, text_y, len(text), 1, text, fg=tc.white, bg=None, alignment=tc.LEFT)
                secondary.print_box(name_origin + 1, text_y, len(item.name), 1, item.name, fg=tc.white, bg=None, alignment=tc.LEFT)
                secondary.print_box(defense_origin + 1, text_y, 5, 1, str(item.equippable.defense_bonus), fg=tc.white, bg=None, alignment=tc.CENTER)
                if item.equippable.intelligence_bonus != 0:
                    secondary.print_box(intelligence_origin + 1, text_y, 5, 1, str(item.equippable.intelligence_bonus), fg=tc.white, bg=None, alignment=tc.CENTER)
                text_y += 1
                letter_index += 1

            elif str(item.item.function_kwargs.get('maximum_range')) == 0:
                text = '(' + chr(letter_index) + ') '
                secondary.print_box(2, text_y, len(text), 1, text, fg=tc.white, bg=None, alignment=tc.LEFT)
                secondary.print_box(name_origin + 1, text_y, len(item.name), 1, item.name, fg=tc.white, bg=None, alignment=tc.LEFT)
                secondary.print_box(damage_origin + 1, text_y, 5, 1, str(item.item.function_kwargs.get('damage')), fg=tc.white, bg=None, alignment=tc.CENTER)
                secondary.print_box(range_origin + 1, text_y, 5, 1, str(item.item.function_kwargs.get('maximum_range')), fg=tc.white, bg=None, alignment=tc.CENTER)
                secondary.print_box(charge_origin + 1, text_y, 5, 1, str(item.item.uses) + '/' + str(item.item.maxUses), fg=tc.white, bg=None, alignment=tc.CENTER)
                text_y += 1
                letter_index += 1

            elif item.equippable.defense_bonus == 0:
                text = '(' + chr(letter_index) + ') '
                secondary.print_box(2, text_y, len(text), 1, text, fg=tc.white, bg=None, alignment=tc.LEFT)
                secondary.print_box(name_origin + 1, text_y, len(item.name), 1, item.name, fg=tc.white, bg=None, alignment=tc.LEFT)
                secondary.print_box(damage_origin + 1, text_y, 5, 1, str(item.equippable.strength_bonus), fg=tc.white, bg=None, alignment=tc.CENTER)
                if item.equippable.intelligence_bonus != 0:
                    secondary.print_box(intelligence_origin + 1, text_y, 5, 1, str(item.equippable.intelligence_bonus), fg=tc.white, bg=None, alignment=tc.CENTER)
                text_y += 1
                letter_index += 1

        elif item.item.ranged == True:
            text = '(' + chr(letter_index) + ') '
            secondary.print_box(2, text_y, len(text), 1, text, fg=tc.white, bg=None, alignment=tc.LEFT)
            secondary.print_box(name_origin + 1, text_y, len(item.name), 1, item.name, fg=tc.white, bg=None, alignment=tc.LEFT)
            secondary.print_box(damage_origin + 1, text_y, 5, 1, str(item.item.function_kwargs.get('damage')), fg=tc.white, bg=None, alignment=tc.CENTER)
            secondary.print_box(range_origin + 1, text_y, 5, 1, str(item.item.function_kwargs.get('maximum_range')), fg=tc.white, bg=None, alignment=tc.CENTER)
            secondary.print_box(charge_origin + 1, text_y, 5, 1, str(item.item.uses) + '/' + str(item.item.maxUses), fg=tc.white, bg=None, alignment=tc.CENTER)
            text_y += 1
            letter_index += 1

        else:    
            text = '(' + chr(letter_index) + ') '
            secondary.print_box(2, text_y, len(text), 1, text, fg=tc.white, bg=None, alignment=tc.LEFT)
            secondary.print_box(name_origin + 1, text_y, len(item.name), 1, item.name, fg=tc.white, bg=None, alignment=tc.LEFT)
            text_y += 1
            letter_index += 1

    tc.console_blit(secondary, 0, 0, width, height, 0, x, y, 1.0, 1.0)    

def main_menu(con, background_image, screen_width, screen_height):
    tc.image_blit_2x(background_image, 0, 0, 0)

    con.default_fg = tc.light_yellow
    tc.console_print_ex(0, int(screen_width / 2), int(screen_height / 2) - 4, tc.BKGND_NONE, tc.CENTER,'INSERT NEW TITLE')

    menu(con, '', ['Play a new game', 'Continue last game', 'Quit'], 24, screen_width, screen_height)

def level_up_menu(con, header, player, menu_width, screen_width, screen_height):
    width = menu_width + 6
    height = menu_width - 18

    dest_x = 0
    dest_y = 0

    x = screen_width // 2 - menu_width // 2
    y = screen_height // 2 - height // 2
    
    secondary = tc.console.Console(width, height)

    secondary.draw_frame(dest_x, dest_y, width, height - 1, "Level Up", False, fg=tc.white, bg=tc.black)
    secondary.draw_frame(dest_x + 1, dest_y + 1, width - 2 , height - 3, "", False, fg=tc.white, bg=tc.black)

    secondary.print_box((menu_width - menu_width) + 3, 4, menu_width, 1,"(a) Constitution", fg=tc.white, bg=tc.black, alignment = tc.CENTER)
    secondary.print_box((menu_width - menu_width) + 3, 6, menu_width, 1,"Increases max HP by 20. Currently: " + str(player.fighter.max_hp), fg=tc.white, bg=None, alignment = tc.CENTER)

    secondary.print_box((menu_width - menu_width) + 3, 9, menu_width, 1,"(b) Strength", fg=tc.white, bg=tc.black, alignment = tc.CENTER)
    secondary.print_box((menu_width - menu_width) + 3, 11, menu_width, 1,"Increases physical damage. Currently: " + str(player.fighter.strength), fg=tc.white, bg=None, alignment = tc.CENTER)

    secondary.print_box((menu_width - menu_width) + 3, 14, menu_width, 1,"(c) Toughness", fg=tc.white, bg=tc.black, alignment = tc.CENTER)
    secondary.print_box((menu_width - menu_width) + 3, 16, menu_width, 1,"Increases physical defense. Currently: " + str(player.fighter.toughness), fg=tc.white, bg=None, alignment = tc.CENTER)

    tc.console_blit(secondary, 0, 0, width, height, 0, x, y, 1.0, 1.0) 

def character_screen(player, character_screen_width, character_screen_height, screen_width, screen_height):
    width = character_screen_width + 8
    height = character_screen_height + 3

    dest_x = 0
    dest_y = 0

    x = screen_width // 2 - character_screen_width // 2
    y = screen_height // 2 - character_screen_height // 2
    
    secondary = tc.console.Console(width, height)

    secondary.draw_frame(dest_x, dest_y, width, height, "Character Information", False, fg=tc.white, bg=tc.black)
    secondary.draw_frame(dest_x + 1, dest_y + 1, width - 2 , height - 2, "", False, fg=tc.white, bg=tc.black)

    secondary.print_box(dest_x + 2, dest_y + 2, character_screen_width, 1,'Level: {0}'.format(player.level.current_level), fg=tc.white, bg=None, alignment = tc.LEFT)
    secondary.print_box(dest_x + 2, dest_y + 3, character_screen_width, 1,'Experience: {0}'.format(player.level.current_xp), fg=tc.white, bg=None, alignment = tc.LEFT)
    secondary.print_box(dest_x + 2, dest_y + 4, character_screen_width, 1,'Experience for next level: {0}'.format(player.level.experience_to_next_level), fg=tc.white, bg=None, alignment = tc.LEFT)
    secondary.print_box(dest_x + 2, dest_y + 5, character_screen_width, 1,'Maximum HP: {0}'.format(player.fighter.max_hp), fg=tc.white, bg=None, alignment = tc.LEFT)
    secondary.print_box(dest_x + 2, dest_y + 6, character_screen_width, 1,'Strength: {0}'.format(player.fighter.base_strength), fg=tc.white, bg=None, alignment = tc.LEFT)
    secondary.print_box(dest_x + 2, dest_y + 7, character_screen_width, 1,'Attack: {0}'.format(player.fighter.attack_damage), fg=tc.white, bg=None, alignment = tc.LEFT)
    secondary.print_box(dest_x + 2, dest_y + 8, character_screen_width, 1,'Armour: {0}'.format(player.fighter.defense), fg=tc.white, bg=None, alignment = tc.LEFT)
    secondary.print_box(dest_x + 2, dest_y + 9, character_screen_width, 1,'Toughness: {0}'.format(player.fighter.toughness), fg=tc.white, bg=None, alignment = tc.LEFT)
    secondary.print_box(dest_x + 2, dest_y + 10, character_screen_width, 1,'Intelligence: {0}'.format(player.mage.intelligence), fg=tc.white, bg=None, alignment = tc.LEFT)

    tc.console_blit(secondary, 0, 0, width, height, 0, x, y, 1.0, 1.0)

def message_box(con, header, width, screen_width, screen_height):
    menu(con, header, [], width, screen_width, screen_height)

def tutorial_menu(con, header, width, screen_width, screen_height):
    
    center_x = int(screen_width / 2)
    center_y = int(screen_height / 2)

    tutorial_panel = tc.console.Console(110, 49)
    tutorial_panel.default_fg = tc.white
    tutorial_panel.default_fbg = tc.black

    tutorial_panel.draw_frame(center_x - int(tutorial_panel.width / 2), center_y - 25, tutorial_panel.width - 10, tutorial_panel.height - 10, "Tutorial Menu", False, fg=tc.white, bg=tc.black)

    tutorial_panel.print(center_x - 6, center_y - 23, '[Key Bindings]'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    tutorial_panel.print(center_x - 6, center_y - 21, '[Movement]'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    tutorial_panel.print(center_x - 6, center_y - 19, 'Number Pad 1-9 or arrow keys for movement'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    tutorial_panel.print(center_x - 6, center_y - 17, 'I to open inventory screen'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    tutorial_panel.print(center_x - 6, center_y - 15, '[Inventory screen]'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    tutorial_panel.print(center_x - 6, center_y - 13, 'Push the letter inside the () to use/equip the corresponding item.'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    tutorial_panel.print(center_x - 6, center_y - 11, 'D to open drop item screen'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    tutorial_panel.print(center_x - 6, center_y - 9,'[Inventory Drop screen]'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    tutorial_panel.print(center_x - 6, center_y - 7, 'Push the letter inside the () to drop the corresponding item.'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    tutorial_panel.print(center_x - 6, center_y - 5, 'T to wait a turn.'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    tutorial_panel.print(center_x - 6, center_y - 3, 'E to pick up items.'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    tutorial_panel.print(center_x - 6, center_y - 1, 'ENTER/RETURN to use flights of stairs.'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    tutorial_panel.print(center_x - 6, center_y + 1, 'ESCAPE to exit various menus/return to the Main Menu/cancel certan item usage.'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    tutorial_panel.print(center_x - 6, center_y + 3, 'R to activate targeting mode.'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    tutorial_panel.print(center_x - 6, center_y + 5, '[Targeting mode]'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    tutorial_panel.print(center_x - 6, center_y + 7, 'Press RIGHT or LEFT key to switch targets.'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    tutorial_panel.print(center_x - 6, center_y + 9, 'Press / or ? to display HELP SCREEN.'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    tutorial_panel.print(center_x - 6, center_y + 11, 'Pick up new equipment(E), weapons(W) and health(H) to improve your chances of survival.'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    tutorial_panel.print(center_x - 6, center_y + 13, 'PRESS ESCAPE TO EXIT TUTORIAL SCREEN.'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)

    tc.console_blit(tutorial_panel, 0, 0, tutorial_panel.width, tutorial_panel.height, 0, 4, 0, 1.0, 1.0)

def help_menu(con, header, width, screen_width, screen_height):
    center_x = int(screen_width / 2)
    center_y = int(screen_height / 2)

    help_menu_panel = tc.console.Console(110, 45)

    help_menu_panel.default_fg = tc.white
    help_menu_panel.default_fbg = tc.black

    help_menu_panel.draw_frame(center_x - int(help_menu_panel.width / 2), center_y - 25, help_menu_panel.width - 10, help_menu_panel.height - 10, "Help Menu", False, fg=tc.white, bg=tc.black)

    help_menu_panel.print(center_x - 6, center_y - 23, '[Key Bindings]'.format(tc.red), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    help_menu_panel.print(center_x - 6, center_y - 21, '[Movement]'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    help_menu_panel.print(center_x - 6, center_y - 19, 'Number Pad 1-9 or arrow keys for movement'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    help_menu_panel.print(center_x - 6, center_y - 17, 'I to open inventory screen'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    help_menu_panel.print(center_x - 6, center_y - 15, '[Inventory screen]'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    help_menu_panel.print(center_x - 6, center_y - 13, 'Push the letter inside the () to use/equip the corresponding item.'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    help_menu_panel.print(center_x - 6, center_y - 11, 'D to open drop item screen'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    help_menu_panel.print(center_x - 6, center_y - 9,'[Inventory Drop screen]'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    help_menu_panel.print(center_x - 6, center_y - 7, 'Push the letter inside the () to drop the corresponding item.'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    help_menu_panel.print(center_x - 6, center_y - 5, 'T to wait a turn.'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    help_menu_panel.print(center_x - 6, center_y - 3, 'E to pick up items.'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    help_menu_panel.print(center_x - 6, center_y - 1, 'ENTER/RETURN to use flights of stairs.'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    help_menu_panel.print(center_x - 6, center_y + 1, 'ESCAPE to exit various menus/return to the Main Menu/cancel certan item usage.'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    help_menu_panel.print(center_x - 6, center_y + 3, 'R to activate targeting mode.'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    help_menu_panel.print(center_x - 6, center_y + 5, '[Targeting mode]'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    help_menu_panel.print(center_x - 6, center_y + 7, 'Press RIGHT or LEFT key to switch targets.'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)
    help_menu_panel.print(center_x - 6, center_y + 9, 'PRESS ESCAPE TO EXIT HELP SCREEN.'.format(), (255, 255, 255), (0, 0, 0), 1, tc.CENTER)

    tc.console_blit(help_menu_panel, 0, 0, help_menu_panel.width, help_menu_panel.height, 0, 4, 0, 1.0, 1.0)