import tcod as tc

from components.equipment import Equipment
from components.equippable import Equippable
from components.fighter import Fighter
from components.mage import Mage
from components.inventory import Inventory
from components.item import Item
from components.level import Level
from entity import Entity
from equipment_slots import EquipmentSlots
from item_functions import cast_confuse, cast_fireball, cast_lightning, heal, magic
from game_messages import MessageLog, Message
from game_states import GameStates
from map_objects.game_map import GameMap
from render_functions import RenderOrder

def get_constants():
    window_title = 'Basically just the tutorial.'

    screen_width = 130
    screen_height = 65

    bar_width = 20
    panel_height = 10
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 130
    map_height = 55

    #ONEROOMBUILD
    # # room_max_size = 50
    # # room_min_size = 46
    # # max_rooms = 30
    # # max_rooms = 1

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 8
    
    ##ONEROOMBUILD
    ## fov_radius = 50

    max_monsters_per_room = 3
    max_items_per_room = 2

    colors = {
        'dark_wall': tc.Color(0, 0, 100),
        'dark_ground': tc.Color(50, 50, 150),
        'light_wall': tc.Color(130, 110, 50),
        'light_ground': tc.Color(200, 180, 50)
    }

    constants = {
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'bar_width': bar_width,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height,
        'map_width': map_width,
        'map_height': map_height,
        'room_max_size': room_max_size,
        'room_min_size': room_min_size,
        'max_rooms': max_rooms,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'max_monsters_per_room': max_monsters_per_room,
        'max_items_per_room': max_items_per_room,
        'colors': colors
    }

    return constants

def get_game_variables(constants):
    fighter_component = Fighter(hp = 100, head_hp = 100, chest_hp = 100, right_arm_hp = 100, left_arm_hp = 100, right_leg_hp = 100, left_leg_hp = 100, toughness = 1, strength = 1)
    mage_component = Mage(intelligence = 1)
    inventory_component = Inventory(10)
    level_component = Level()
    equipment_component = Equipment()
    player = Entity(0, 0, 'A', tc.white, 'You', blocks = True, render_order = RenderOrder.ACTOR,
                    fighter = fighter_component, mage = mage_component, inventory = inventory_component, level = level_component, equipment = equipment_component)  
    entities = [player]

    equippable_component = Equippable(EquipmentSlots.HEAD_ARMOUR, defense_bonus = 1, intelligence_bonus = 0)
    full_helm = Entity(0, 0, 'E', tc.sky, 'Full-Helm', equippable = equippable_component)
    player.inventory.add_item(full_helm)
    player.equipment.toggle_equip(full_helm)

    equippable_component = Equippable(EquipmentSlots.CHEST_ARMOUR, defense_bonus = 1, intelligence_bonus = 0)
    cloth_shirt = Entity(0, 0, 'E', tc.sky, 'Cloth Shirt', equippable = equippable_component)
    player.inventory.add_item(cloth_shirt)
    player.equipment.toggle_equip(cloth_shirt)

    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, strength_bonus = 1)
    club = Entity(0, 0, 'W', tc.sky, 'Club', equippable = equippable_component)
    player.inventory.add_item(club)
    player.equipment.toggle_equip(club)
    
    equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus = 1)
    shield = Entity(0, 0, 'E', tc.sky, 'Shield', equippable = equippable_component)
    player.inventory.add_item(shield)
    player.equipment.toggle_equip(shield)

    # equippable_component = Equippable(EquipmentSlots.BOTH_HAND, strength_bonus = 0)
    # green_two_finger = Entity(0, 0, 'W', tc.sky, 'Green-Two-Finger', equippable = equippable_component)
    # player.inventory.add_item(green_two_finger)
    # player.fighter.turns_since_special = 6

    # item_component = Item(use_function = magic, targeting = True, targeting_message = Message('Left-click an enemy for spell`s target, Right-click to cancel.', tc.light_cyan), damage = 10, maximum_range = 2, ranged = True, uses = 5, maxUses = 5)
    # fireStaff = Entity(0, 0, 'I', tc.white, 'Staff of Fire', render_order = RenderOrder.ITEM, item = item_component) 
    # player.inventory.add_item(fireStaff)

    game_map = GameMap(constants['map_width'], constants['map_height'])
    game_map.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'], constants['map_width'], constants['map_height'], player, entities)

    message_log = MessageLog(constants['message_x'], constants['message_width'], constants['message_height'])

    game_state = GameStates.PLAYERS_TURN

    return player, entities, game_map, message_log, game_state