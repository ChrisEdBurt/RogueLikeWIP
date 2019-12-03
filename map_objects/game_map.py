import tcod as tc
from random import randint

from components.ai import BasicMonster, RetreatingMonster
from components.equipment import EquipmentSlots
from components.equippable import Equippable
from components.equipment import Equipment
from components.fighter import Fighter
from components.item import Item
from components.stairs import Stairs
from components.inventory import Inventory
from components.area import Area
from game_states import GameStates
from entity import Entity
from game_messages import Message
from item_functions import cast_confuse, cast_fireball, cast_lightning, heal, magic
from map_objects.rectangle import Rect
from map_objects.tile import Tile
from random_utils import from_dungeon_level, random_choice_from_dict
from render_functions import RenderOrder
from loader_functions.data_loaders import load_json

class GameMap:
    def __init__(self, width, height, dungeon_level=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.dungeon_level = dungeon_level

    def initialize_tiles(self):    
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]
        
        return tiles

    def make_town(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities):

        rooms = []
        num_rooms = 0

        center_of_last_room_x = None
        center_of_last_room_y = None

        for r in range(max_rooms):

            # random width and height
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)

            # random position without going out of the boundaries of the map
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            # "Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)

            # run through the other rooms and see if they intersect with this one
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # this means there are no intersections, so this room is valid

                # "paint" it to the map's tiles
                self.create_room(new_room)

                # center coordinates of new room, will be useful later
                (new_x, new_y) = new_room.center()

                center_of_last_room_x = new_x
                center_of_last_room_y = new_y

                if num_rooms == 0:
                    # this is the first room, where the player starts at
                    player.x = new_x
                    player.y = new_y

                else:
                    # all rooms after the first:
                    # connect it to the previous room with a tunnel

                    # center coordinates of previous room
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    # flip a coin (random number that is either 0 or 1)
                    if randint(0, 1) == 1:
                        # first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                # finally, append the new room to the list
                rooms.append(new_room)
                num_rooms += 1

        stairs_component = Stairs("Overworld", 'up')
        up_stairs = Entity(center_of_last_room_x, center_of_last_room_y, '<', tc.white, 'Stairs Up',render_order=RenderOrder.STAIRS, stairs=stairs_component)
        entities.append(up_stairs)   

        fighter_component = Fighter(hp=15, head_hp = 100, chest_hp = 100, right_arm_hp = 100, left_arm_hp = 100, right_leg_hp = 100, left_leg_hp = 100, toughness=1, strength=4, xp=25)
        ai_component = RetreatingMonster()
        monster = Entity(new_x, new_y, 'r', tc.desaturated_green, 'Rat', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
        entities.append(monster)

    def get_map_import(self, map_width, map_height, entities):

        x = 0
        y = 0

        with open("maps.txt", "rt") as f:
            for line in f:
                tiles = []
                
                for character in line:
                    if character == '^':
                        tiles.append(Tile(blocked=(character == "^")))
                        self.tiles[x][y].blocked = True
                        self.tiles[x][y].block_sight = True
                        x +=1

                    elif character == '.':
                        tiles.append(Tile(blocked=(character == ".")))
                        self.tiles[x][y].blocked = False
                        self.tiles[x][y].block_sight = False
                        x += 1

                    elif character == 'T':
                        tiles.append(Tile(blocked=(character == "T")))
                        self.tiles[x][y].blocked = False
                        self.tiles[x][y].block_sight = False
                        self.tiles[x][y].building = True
                        x += 1

                    elif character == 'E':
                        tiles.append(Tile(blocked=(character == "T")))
                        self.tiles[x][y].blocked = False
                        self.tiles[x][y].block_sight = False
                        self.tiles[x][y].earth = True
                        x += 1

                    else:
                        y += 1

                # map.append(tiles)
                # self.tiles.append(map)
                x = 0

    def make_overworld(self, map_width, map_height, player, entities):

        self.get_map_import(map_width, map_height, entities)

        area_component = Area('Town')
        town_marker = Entity(60, 15, 'T', tc.white, 'Enter Town', render_order=RenderOrder.STAIRS, area=area_component)
        entities.append(town_marker)

    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities):
        rooms = []
        num_rooms = 0

        center_of_last_room_x = None
        center_of_last_room_y = None

        for r in range(max_rooms):

            # random width and height
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            # #ONEROOMBUILD
            # # w = map_width - 5
            # # h = map_height - 5

            # random position without going out of the boundaries of the map
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            # "Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)

            # run through the other rooms and see if they intersect with this one
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # this means there are no intersections, so this room is valid
                # "paint" it to the map's tiles
                self.create_room(new_room)

                # center coordinates of new room, will be useful later
                (new_x, new_y) = new_room.center()

                center_of_last_room_x = new_x
                center_of_last_room_y = new_y

                if num_rooms == 0:
                    # this is the first room, where the player starts at
                    player.x = new_x
                    player.y = new_y
                else:
                    # all rooms after the first:
                    # connect it to the previous room with a tunnel

                    # center coordinates of previous room
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    # flip a coin (random number that is either 0 or 1)
                    if randint(0, 1) == 1:
                        # first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                self.place_entities(new_room, entities)

                # finally, append the new room to the list
                rooms.append(new_room)
                num_rooms += 1

        stairs_component = Stairs(self.dungeon_level + 1, 'down')
        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, '>', tc.white, 'Stairs Down',
                             render_order=RenderOrder.STAIRS, stairs=stairs_component)
        entities.append(down_stairs)

        # stairs_component = Stairs(self.dungeon_level - 1, 'up')
        # up_stairs = Entity(center_of_last_room_x + 1, center_of_last_room_y + 1, '<', tc.white, 'Stairs Up',
        #                      render_order=RenderOrder.STAIRS, stairs=stairs_component)
        # entities.append(up_stairs)

    def create_room(self, room):
        # go through the tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def place_entities(self, room, entities):
        max_monsters_per_room = from_dungeon_level([[2, 1], [3, 3], [4, 5]], self.dungeon_level)
        max_items_per_room = from_dungeon_level([[1, 1], [2, 4]], self.dungeon_level)
        max_equipment_per_room = from_dungeon_level([[1, 1], [2, 2]], self.dungeon_level)
        # max_chests_per_level = from_dungeon_level([[1, 1], [2, 2], [3,3]], self.dungeon_level)

        # Load JSON for Item/Enemy randomized values
        data = load_json()

        # Get a random number of monsters
        number_of_monsters = randint(0, max_monsters_per_room)

        # Get a random number of items
        number_of_items = randint(0, max_items_per_room)
        # #ONEROOMBUILD
        # # number_of_items = 0

        # Get a random number of equipment
        num_of_equipments = randint(0, max_equipment_per_room)

        # # Get a random number of equipment
        # num_of_chests = randint(0, max_chests_per_level)

        # for i, v in enumerate(['tic', 'tac', 'toe']):
        #     print(i, v)
        #     0 tic
        # for k, v in enemy_chance.items():
        #     print(k, v)

        new_dict = {}
        monster_chance_dict = data["monster_chances"]
        for k, v in monster_chance_dict.items():
            new_dict.update({k: from_dungeon_level([[v[0][0], v[0][1]]], self.dungeon_level)})

        equipment_dict = {}
        equipment_chance_dict = data["items"]["equipment_chances"]
        for k, v in equipment_chance_dict.items():
            equipment_dict.update({k: from_dungeon_level([[v[0][0], v[0][1]]], self.dungeon_level)})

        item_chances = {
            # 'healing_potion': 30,
            'healing_potion': 100,
            # 'lightning_scroll': from_dungeon_level([[25, 4]], self.dungeon_level),
            # 'fireball_scroll': from_dungeon_level([[25, 6]], self.dungeon_level),
            # 'confusion_scroll': from_dungeon_level([[10, 2]], self.dungeon_level)
        }

        # equipment_chances = {
        #     'dirk': 30,
        #     'sword': 30,
        #     'zweihander': 25,
        #     'polearm': 15,
        # }

        # chest_chances = {
        #     'cimim': 25,
        #     'chest':75
        # }

        for i in range(number_of_monsters):
            # Choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):

                monster_choice = random_choice_from_dict(new_dict)
                random_monster_index = 0
                for i, v in enumerate(monster_chance_dict):
                    if v == monster_choice:
                        random_monster_index = i

                enemy_list = data["enemy_list"]["enemy_name"]
                
                ####ONLY ONE MONSTER
                # choices = list(enemy_list.keys())
                # enemy_index = choices[0]
                
                choices = list(enemy_list.keys())
                enemy_index = choices[random_monster_index]

                # # Get Enemy name length, randomise name and apply it to enemy
                # enemy_adjectives = data["enemies"]["adjectives"]
                # max_enemy_name_index = len(enemy_adjectives)
                # random_adjective_index = randint(0, max_enemy_name_index - 1)
                # monster_adjective = enemy_adjectives[random_adjective_index]

                enemy_figher = enemy_list[enemy_index]["fighter"]
                
                # enemy_hp = enemy_figher["hp"]
                # enemy_toughness = enemy_figher["toughness"]
                # enemy_strength = enemy_figher["strength"]
                # enemy_xp = enemy_figher["xp"]

                enemy_hp =  from_dungeon_level(enemy_figher["hp"], self.dungeon_level)
                enemy_toughness = from_dungeon_level(enemy_figher["toughness"], self.dungeon_level)
                enemy_strength = from_dungeon_level(enemy_figher["strength"], self.dungeon_level)
                enemy_xp = from_dungeon_level(enemy_figher["xp"], self.dungeon_level)
                enemy_head_hp = enemy_figher["head_hp"]
                enemy_chest_hp = enemy_figher["chest_hp"]
                enemy_right_arm_hp = enemy_figher["right_arm_hp"]
                enemy_left_arm_hp = enemy_figher["left_arm_hp"]
                enemy_right_leg_hp = enemy_figher["right_leg_hp"]
                enemy_left_leg_hp = enemy_figher["left_leg_hp"]

                enemy_entity = enemy_list[enemy_index]["Entity"]
                enemy_char = enemy_entity["char"]
                enemy_name = enemy_entity["name"]
                enemy_blocks = enemy_entity["blocks"]
                
                random_mutation_chance = randint(0, 100 - 1)
                buff_or_debuff_chance = randint(0, 20 - 1)

                fighter_component = Fighter(hp = enemy_hp, head_hp = enemy_head_hp, chest_hp = enemy_chest_hp, right_arm_hp = enemy_right_arm_hp, left_arm_hp = enemy_left_arm_hp, right_leg_hp = enemy_right_leg_hp, left_leg_hp = enemy_left_leg_hp, toughness = enemy_toughness, strength = enemy_strength, xp = enemy_xp)            
                ai_component = BasicMonster()
                # ai_component = RetreatingMonster()

                if random_mutation_chance >= 1 and random_mutation_chance <= 15:

                    if buff_or_debuff_chance >= 1 and buff_or_debuff_chance <= 10:
                        # Get Enemy name length, randomise name and apply it to enemy
                        enemy_debuff_adjectives = data["enemies"]["negative_adjectives"]
                        max_enemy_name_index = len(enemy_debuff_adjectives)

                        random_debuff_adjective_index = randint(0, max_enemy_name_index - 1)
                        monster_adjective = enemy_debuff_adjectives[random_debuff_adjective_index]

                        fighter_component = Fighter(hp = (enemy_hp - randint(0, 4)), head_hp = (enemy_head_hp - randint(0, 15 - 5)), chest_hp = (enemy_chest_hp - randint(0, 15 - 5)), right_arm_hp = (enemy_right_arm_hp - randint(0, 15 - 5)), left_arm_hp = (enemy_left_arm_hp - randint(0, 15 - 5)), right_leg_hp = (enemy_right_leg_hp - randint(0, 15 - 5)), left_leg_hp = enemy_left_leg_hp - randint(0, 15 - 5), toughness = (enemy_toughness + randint(0, 2 - 1)), strength = (enemy_strength - randint(0, 2 - 1)), xp = (enemy_xp - randint(0, 5)))
                        monster = Entity(x, y, enemy_char, tc.white, monster_adjective + " " + enemy_name, blocks = enemy_blocks, render_order=RenderOrder.ACTOR, fighter = fighter_component, ai = ai_component)
                        
                        # print("enemy_name: " + monster_adjective + " " + enemy_name + '\n' +  \
                        # "enemy_hp: " + str(monster.fighter.hp) + '\n' +  \
                        # "enemy_toughness: " + str(monster.fighter.toughness) + '\n' +  \
                        # "enemy_strength: " + str(monster.fighter.strength) + '\n' +  \
                        # "enemy_xp: " + str(monster.fighter.xp) + '\n' +  \
                        # "enemy_head_hp: " + str(monster.fighter.head_hp) + '\n' +  \
                        # "enemy_chest_hp: " + str(monster.fighter.chest_hp) + '\n' +  \
                        # "enemy_right_arm_hp: " + str(monster.fighter.right_arm_hp) + '\n' +  \
                        # "enemy_left_arm_hp: " + str(monster.fighter.left_arm_hp) + '\n' +  \
                        # "enemy_right_leg_hp: " + str(monster.fighter.right_leg_hp) + '\n' +  \
                        # "enemy_left_leg_hp: " + str(monster.fighter.left_leg_hp) + '\n')

                    elif buff_or_debuff_chance >= 11 and buff_or_debuff_chance <= 20:
                        # Get Enemy name length, randomise name and apply it to enemy
                        enemy_buff_adjectives = data["enemies"]["positive_adjectives"]
                        max_enemy_name_index = len(enemy_buff_adjectives)

                        random_buff_adjective_index = randint(0, max_enemy_name_index - 1)
                        monster_adjective = enemy_buff_adjectives[random_buff_adjective_index]

                        fighter_component = Fighter(hp = (enemy_hp + randint(0, 4)), head_hp = (enemy_head_hp + randint(0, 15 - 5)), chest_hp = (enemy_chest_hp + randint(0, 15 - 5)), right_arm_hp = (enemy_right_arm_hp + randint(0, 15 - 5)), left_arm_hp = (enemy_left_arm_hp + randint(0, 15 - 5)), right_leg_hp = (enemy_right_leg_hp + randint(0, 15 - 5)), left_leg_hp = enemy_left_leg_hp + randint(0, 15 - 5), toughness = (enemy_toughness + randint(0, 2 - 1)), strength = (enemy_strength + randint(0, 2 - 1)), xp = (enemy_xp + randint(0, 10 - 5)))
                        monster = Entity(x, y, enemy_char, tc.red, monster_adjective + " " + enemy_name, blocks = enemy_blocks, render_order=RenderOrder.ACTOR, fighter = fighter_component, ai = ai_component)

                        # print("enemy_name: " + monster_adjective + " " + enemy_name + '\n' +  \
                        # "enemy_hp: " + str(monster.fighter.hp) + '\n' +  \
                        # "enemy_toughness: " + str(monster.fighter.toughness) + '\n' +  \
                        # "enemy_strength: " + str(monster.fighter.strength) + '\n' +  \
                        # "enemy_xp: " + str(monster.fighter.xp) + '\n' +  \
                        # "enemy_head_hp: " + str(monster.fighter.head_hp) + '\n' +  \
                        # "enemy_chest_hp: " + str(monster.fighter.chest_hp) + '\n' +  \
                        # "enemy_right_arm_hp: " + str(monster.fighter.right_arm_hp) + '\n' +  \
                        # "enemy_left_arm_hp: " + str(monster.fighter.left_arm_hp) + '\n' +  \
                        # "enemy_right_leg_hp: " + str(monster.fighter.right_leg_hp) + '\n' +  \
                        # "enemy_left_leg_hp: " + str(monster.fighter.left_leg_hp) + '\n')

                else:
                    monster = Entity(x, y, enemy_char, tc.desaturated_green, enemy_name, blocks = enemy_blocks, render_order=RenderOrder.ACTOR, fighter = fighter_component, ai = ai_component)
               
                entities.append(monster)

        for i in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                item_choice = random_choice_from_dict(item_chances)

                if item_choice == 'healing_potion':
                    item_component = Item(use_function=heal, amount=25)
                    item = Entity(x, y, 'H', tc.violet, 'Healing Potion', render_order=RenderOrder.ITEM,item=item_component)

                # elif item_choice == 'fireball_scroll':
                #     item_component = Item(use_function=cast_fireball, targeting=True, targeting_message=Message(
                #         'Left-click a target tile for the fireball, or right-click to cancel.', tc.light_cyan), damage=25, radius=3)
                #     item = Entity(x, y, 'F', tc.red, 'Fireball Scroll', render_order=RenderOrder.ITEM,item=item_component)

                # elif item_choice == 'confusion_scroll':
                #     item_component = Item(use_function=cast_confuse, targeting=True, targeting_message=Message('Left-click an enemy to confuse it, or right-click to cancel.', tc.light_cyan))
                #     item = Entity(x, y, 'C', tc.light_pink, 'Confusion Scroll', render_order=RenderOrder.ITEM,item=item_component)

                # else:
                #     item_component = Item(use_function=cast_lightning, damage=40, maximum_range=5)
                #     item = Entity(x, y, 'L', tc.yellow, 'Lightning Scroll', render_order=RenderOrder.ITEM,item=item_component)

                entities.append(item)

        for i in range(num_of_equipments):
            # Choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):

                equipment_choice = random_choice_from_dict(equipment_dict)
                random_equipment_index = 0
                for i, v in enumerate(equipment_chance_dict):
                    if v == equipment_choice:
                        random_equipment_index = i

                equipment_list = data["items"]["equipment_item_list"]
                
                ###ONLY SPAWN ONE KIND OF EQUIPMENT
                # equipment_index = choices[3]

                choices = list(equipment_list.keys())
                equipment_index = choices[random_equipment_index]
                equipment_slot = equipment_list[equipment_index]["equipment_slot"]

                if equipment_slot == "MAIN_HAND":
                    equipment_slot = EquipmentSlots.MAIN_HAND
                    equipment_strength_bonus = equipment_list[equipment_index]["strength_bonus"]

                elif equipment_slot == "BOTH_HAND":
                    equipment_slot = EquipmentSlots.BOTH_HAND
                    equipment_strength_bonus = equipment_list[equipment_index]["strength_bonus"]

                elif equipment_slot == "OFF_HAND":
                    equipment_slot = EquipmentSlots.OFF_HAND
                    equipment_defence_bonus = equipment_list[equipment_index]["defense_bonus"]

                elif equipment_slot == "HEAD_ARMOUR":
                    equipment_slot = EquipmentSlots.HEAD_ARMOUR
                    equipment_defence_bonus = equipment_list[equipment_index]["defense_bonus"]

                elif equipment_slot == "CHEST_ARMOUR":
                    equipment_slot = EquipmentSlots.CHEST_ARMOUR
                    equipment_defence_bonus = equipment_list[equipment_index]["defense_bonus"]
                
                equipment_char = equipment_list[equipment_index]["char"]
                equipment_name = equipment_list[equipment_index]["Name"]

                random_mutation_chance = randint(0, 100 - 1)
                buff_or_debuff_chance = randint(0, 20 - 1)

                if random_mutation_chance >= 1 and random_mutation_chance <= 15:
                    if buff_or_debuff_chance >= 1 and buff_or_debuff_chance <= 12:

                        buff_equipment_max_quality_index_length = len(data["items"]["equipment_adjectives"]["positive_adjectives"])
                        buff_weapon_max_quality_index_length = len(data["items"]["weapon_adjectives"]["positive_adjectives"])

                        equipment_adjective_index = randint(0, buff_equipment_max_quality_index_length - 1)
                        weapon_adjective_index = randint(0, buff_weapon_max_quality_index_length - 1)

                        random_equipment_adjective = data["items"]["equipment_adjectives"]["positive_adjectives"][equipment_adjective_index]
                        random_weapon_adjective = data["items"]["weapon_adjectives"]["positive_adjectives"][weapon_adjective_index]

                        if equipment_list[equipment_index]["equipment_slot"] == "HEAD_ARMOUR" or equipment_list[equipment_index]["equipment_slot"] == "CHEST_ARMOUR":
                            equippable_component = Equippable(equipment_slot, defense_bonus = equipment_defence_bonus + randint(1, 2))
                            item = Entity(x, y, equipment_char , tc.yellow, random_equipment_adjective + " " + equipment_name, equippable=equippable_component)
                        
                        elif equipment_list[equipment_index]["equipment_slot"] == "OFF_HAND":
                            equippable_component = Equippable(equipment_slot, defense_bonus = equipment_defence_bonus + randint(1, 2))
                            item = Entity(x, y, equipment_char , tc.yellow, random_equipment_adjective + " " + equipment_name, equippable=equippable_component)

                        elif equipment_list[equipment_index]["equipment_slot"] == "MAIN_HAND" or equipment_list[equipment_index]["equipment_slot"] == "BOTH_HAND":
                            equippable_component = Equippable(equipment_slot, strength_bonus = equipment_strength_bonus + randint(1, 2))
                            item = Entity(x, y, equipment_char , tc.yellow, random_weapon_adjective + " " + equipment_name, equippable=equippable_component)

                    elif buff_or_debuff_chance >= 13 and buff_or_debuff_chance <= 20:

                        debuff_equipment_max_quality_index_length = len(data["items"]["equipment_adjectives"]["negative_adjectives"])
                        debuff_weapon_max_quality_index_length = len(data["items"]["weapon_adjectives"]["negative_adjectives"])
                        
                        equipment_adjective_index = randint(0, debuff_equipment_max_quality_index_length - 1)
                        weapon_adjective_index = randint(0, debuff_weapon_max_quality_index_length - 1)
                        
                        random_equipment_adjective = data["items"]["equipment_adjectives"]["negative_adjectives"][equipment_adjective_index]
                        random_weapon_adjective = data["items"]["equipment_adjectives"]["negative_adjectives"][weapon_adjective_index]

                        if equipment_list[equipment_index]["equipment_slot"] == "HEAD_ARMOUR" or equipment_list[equipment_index]["equipment_slot"] == "CHEST_ARMOUR":
                            equippable_component = Equippable(equipment_slot, defense_bonus = equipment_defence_bonus - randint(1, 2))
                            item = Entity(x, y, equipment_char , tc.grey, random_equipment_adjective + " " + equipment_name, equippable=equippable_component)
                        
                        elif equipment_list[equipment_index]["equipment_slot"] == "OFF_HAND":
                            equippable_component = Equippable(equipment_slot, defense_bonus = equipment_defence_bonus - randint(1, 2))
                            item = Entity(x, y, equipment_char , tc.grey, random_equipment_adjective + " " + equipment_name, equippable=equippable_component)
                            
                        elif equipment_list[equipment_index]["equipment_slot"] == "MAIN_HAND" or equipment_list[equipment_index]["equipment_slot"] == "BOTH_HAND":
                            equippable_component = Equippable(equipment_slot, strength_bonus = equipment_strength_bonus - randint(1, 2))
                            item = Entity(x, y, equipment_char , tc.grey, random_weapon_adjective + " " + equipment_name, equippable=equippable_component)

                else:
                    if equipment_list[equipment_index]["equipment_slot"] == "HEAD_ARMOUR" or equipment_list[equipment_index]["equipment_slot"] == "OFF_HAND" or equipment_list[equipment_index]["equipment_slot"] == "CHEST_ARMOUR":
                        equippable_component = Equippable(equipment_slot, defense_bonus = equipment_defence_bonus)
                        item = Entity(x, y, equipment_char , tc.sky, equipment_name, equippable=equippable_component)

                    elif equipment_list[equipment_index]["equipment_slot"] == "MAIN_HAND" or equipment_list[equipment_index]["equipment_slot"] == "BOTH_HAND":
                        equippable_component = Equippable(equipment_slot, strength_bonus = equipment_strength_bonus)
                        item = Entity(x, y, equipment_char , tc.sky, equipment_name, equippable=equippable_component)

                # print(item.name)
                entities.append(item)

        # for i in range(num_of_chests):
        #     # Choose a random location in the room
        #     x = randint(room.x1 + 1, room.x2 - 1)
        #     y = randint(room.y1 + 1, room.y2 - 1)

        #     if not any([entity for entity in entities if entity.x == x and entity.y == y]):
        #         chest_choice = random_choice_from_dict(chest_chances)

                # if chest_choice == 'cimim':
                
                #     fighter_component = Fighter(hp=1, head_hp = 100, chest_hp = 100, right_arm_hp = 100, left_arm_hp = 100, right_leg_hp = 100, left_leg_hp = 100, toughness=3, strength=6, xp=25)
                #     ai_component = BasicMonster()
                #     inventory_component = Inventory(2)

                #     cimim = Entity(x, y, 'C', tc.desaturated_green, 'Cimim', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component, inventory=inventory_component)

                #     equippable_component = Equippable(EquipmentSlots.HEAD_ARMOUR, defense_bonus=1)
                #     helm = Entity(0, 0, 'E', tc.white, 'Helm', equippable=equippable_component)

                #     cimim.inventory.add_item(helm)

                # elif chest_choice == 'chest':

                #     inventory_component = Inventory(1)
                #     chest = Entity(x, y, 'C', tc.desaturated_green, 'Chest', inventory=inventory_component)

                    # entities.append(cimim)

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False

    def next_floor(self, player, message_log, constants):

        self.dungeon_level += 1
        entities = [player]

        self.tiles = self.initialize_tiles()
        self.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'], constants['map_width'], constants['map_height'], player, entities)

        player.fighter.heal(player.fighter.max_hp // 15)
        player.fighter.heal(player.fighter.head_hp // 15)
        player.fighter.heal(player.fighter.chest_hp // 15)
        player.fighter.heal(player.fighter.right_arm_hp // 15)
        player.fighter.heal(player.fighter.left_arm_hp // 15)
        player.fighter.heal(player.fighter.right_leg_hp // 15)
        player.fighter.heal(player.fighter.left_leg_hp // 15)

        message_log.add_message(Message('You take a moment to rest, and recover your strength.', tc.light_violet))

        return entities

    def previous_floor(self, player, message_log, constants):

        if self.dungeon_level == "Town":
            entities = [player]
            self.tiles = self.initialize_tiles()
            self.make_overworld(constants['map_width'], constants['map_height'], player, entities)
            self.dungeon_level = "Overworld"

            return entities

        if self.dungeon_level == 0:

            entities = [player]
            self.tiles = self.initialize_tiles()
            self.make_overworld(constants['map_width'], constants['map_height'], player, entities)
            self.dungeon_level = "Overworld"

            return entities

        else:
            self.dungeon_level -= 1
            entities = [player]

            self.tiles = self.initialize_tiles()
            self.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'], constants['map_width'], constants['map_height'], player, entities)

            return entities

    def load_area(self, player, message_log, constants):

        entities = [player]
        self.tiles = self.initialize_tiles()
        self.make_town(10, 5, 12 ,constants['map_width'], constants['map_height'], player, entities)
        self.dungeon_level = "Town"

        return entities
