import tcod as tc
import math

from game_messages import Message
from components.item import Item
from render_functions import RenderOrder

from random import randint
from random_utils import from_dungeon_level, random_choice_from_dict
from loader_functions.data_loaders import load_json

from components.fighter import Fighter
from components.ai import BasicMonster
# from components.equippable import Equippable

class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(self, x, y, char, color, name, blocks=False, render_order=RenderOrder.CORPSE, fighter=None, mage=None, ai=None,
                 item=None, inventory=None, stairs=None, level=None, equipment=None, equippable=None, ranged=None, uses = None, area = None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.render_order = render_order
        self.fighter = fighter
        self.mage = mage
        self.ai = ai
        self.item = item
        self.inventory = inventory
        self.stairs = stairs
        self.level = level
        self.equipment = equipment
        self.equippable = equippable
        self.ranged = ranged
        self.uses = uses
        self.area = area

        if self.fighter:
            self.fighter.owner = self

        if self.mage:
            self.mage.owner = self

        if self.ai:
            self.ai.owner = self

        if self.item:
            self.item.owner = self

        if self.inventory:
            self.inventory.owner = self

        if self.stairs:
            self.stairs.owner = self

        if self.level:
            self.level.owner = self

        if self.equipment:
            self.equipment.owner = self

        if self.equippable:
            self.equippable.owner = self

            if not self.item:
                item = Item()
                self.item = item
                self.item.owner = self

        if self.ranged:
            self.ranged.owner = self

        if self.uses:
            self.uses.owner = self

        if self.area:
            self.area.owner = self

    def move(self, dx, dy):
        # Move the entity by a given amount
        self.x += dx
        self.y += dy

    def move_towards(self, target_x, target_y, game_map, entities):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if not (game_map.is_blocked(self.x + dx, self.y + dy) or get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)):
            self.move(dx, dy)

    def move_away(self, target_x, target_y, game_map, entities):
        dx = target_x + self.x
        dy = target_y + self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if not (game_map.is_blocked(self.x + dx, self.y + dy) or get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)):
            self.move(dx, dy)

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def move_astar(self, target, entities, game_map):
        # Create a FOV map that has the dimensions of the map
        fov = tc.map_new(game_map.width, game_map.height)

        # Scan the current map each turn and set all the walls as unwalkable
        for y1 in range(game_map.height):
            for x1 in range(game_map.width):
                tc.map_set_properties(fov, x1, y1, not game_map.tiles[x1][y1].block_sight, not game_map.tiles[x1][y1].blocked)

        # Scan all the objects to see if there are objects that must be navigated around
        # Check also that the object isn't self or the target (so that the start and the end points are free)
        # The AI class handles the situation if self is next to the target so it will not use this A* function anyway
        for entity in entities:
            if entity.blocks and entity != self and entity != target:
                # Set the tile as a wall so it must be navigated around
                tc.map_set_properties(fov, entity.x, entity.y, True, False)

        # Allocate a A* path
        # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
        my_path = tc.path_new_using_map(fov, 1.41)

        # Compute the path between self's coordinates and the target's coordinates
        tc.path_compute(my_path, self.x, self.y, target.x, target.y)

        # Check if the path exists, and in this case, also the path is shorter than 25 tiles
        # The path size matters if you want the monster to use alternative longer paths (for example through other rooms) if for example the player is in a corridor
        # It makes sense to keep path size relatively low to keep the monsters from running around the map if there's an alternative path really far away
        if not tc.path_is_empty(my_path) and tc.path_size(my_path) < 25:
            # Find the next coordinates in the computed full path
            x, y = tc.path_walk(my_path, True)
            if x or y:
                # Set self's coordinates to the next path tile
                self.x = x
                self.y = y
        else:
            # Keep the old move function as a backup so that if there are no paths (for example another monster blocks a corridor)
            # it will still try to move towards the player (closer to the corridor opening)
            self.move_towards(target.x, target.y, game_map, entities)

            # Delete the path to free memory
        tc.path_delete(my_path)

def get_blocking_entities_at_location(entities, destination_x, destination_y):
    for entity in entities:
        if entity.blocks and entity.x == destination_x and entity.y == destination_y:
            return entity

    return None

def remove_item(self, item):
        self.items.remove(item)

def drop_inventory(self, game_map):

    results = []

    if len(self.inventory.items) == 0:
        results = ['Inventory is empty.']

    else:
        results = []

        for item in self.inventory.items:

            item.x = self.x
            item.y = self.y

            results.append({'{0}'.format(item.name)})
            self.inventory.items.remove(item)
            
        return results

def spawn_enemy(mouse_x, mouse_y, entities, dungeon_level):
    data = load_json()
    
    x = mouse_x
    y = mouse_y

    new_dict = {}
    monster_chance_dict = data["monster_chances"]
    for k, v in monster_chance_dict.items():
        new_dict.update({k: from_dungeon_level([[v[0][0], v[0][1]]], dungeon_level)})

    if not any([entity for entity in entities if entity.x == x and entity.y == y]):

        monster_choice = random_choice_from_dict(new_dict)
        random_monster_index = 0
        for i, v in enumerate(monster_chance_dict):
            if v == monster_choice:
                random_monster_index = i

        enemy_list = data["enemy_list"]["enemy_name"]
        
        ####ONLY ONE MONSTER
        #choices = list(enemy_list.keys())
        #enemy_index = choices[0]
        
        choices = list(enemy_list.keys())
        enemy_index = choices[random_monster_index]
        # enemy_index = choices[18]
        # enemy_index = choices[23]

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

        enemy_hp =  from_dungeon_level(enemy_figher["hp"], dungeon_level)
        enemy_toughness = from_dungeon_level(enemy_figher["toughness"], dungeon_level)
        enemy_strength = from_dungeon_level(enemy_figher["strength"], dungeon_level)
        enemy_xp = from_dungeon_level(enemy_figher["xp"], dungeon_level)
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
        
        random_mutation_chance = randint(1, 100)
        buff_or_debuff_chance = randint(1, 20)

        fighter_component = Fighter(hp = enemy_hp, head_hp = enemy_head_hp, chest_hp = enemy_chest_hp, right_arm_hp = enemy_right_arm_hp, left_arm_hp = enemy_left_arm_hp, right_leg_hp = enemy_right_leg_hp, left_leg_hp = enemy_left_leg_hp, toughness = enemy_toughness, strength = enemy_strength, xp = enemy_xp)            
        ai_component = BasicMonster()
    
        if random_mutation_chance >= 1 and random_mutation_chance <= 10:

            if buff_or_debuff_chance >= 1 and buff_or_debuff_chance <= 10:
                # Get Enemy name length, randomise name and apply it to enemy
                enemy_debuff_adjectives = data["enemies"]["negative_adjectives"]
                max_enemy_name_index = len(enemy_debuff_adjectives)

                random_debuff_adjective_index = randint(0, max_enemy_name_index - 1)
                monster_debuff_adjective = enemy_debuff_adjectives[random_debuff_adjective_index]

                fighter_component = Fighter(hp = (enemy_hp - randint(0, 4)), head_hp = (enemy_head_hp - randint(0, 15 - 5)), chest_hp = (enemy_chest_hp - randint(0, 15 - 5)), right_arm_hp = (enemy_right_arm_hp - randint(0, 15 - 5)), left_arm_hp = (enemy_left_arm_hp - randint(0, 15 - 5)), right_leg_hp = (enemy_right_leg_hp - randint(0, 15 - 5)), left_leg_hp = enemy_left_leg_hp - randint(0, 15 - 5), toughness = (enemy_toughness + randint(0, 2 - 1)), strength = (enemy_strength - randint(0, 2 - 1)), xp = (enemy_xp - randint(0, 5)))
                monster = Entity(x, y, enemy_char, tc.desaturated_green, monster_debuff_adjective + " " + enemy_name, blocks = enemy_blocks, render_order=RenderOrder.ACTOR, fighter = fighter_component, ai = ai_component)

                # print("enemy_hp: " + str(enemy_hp) + '\n' +  \
                #     "enemy_toughness: " + str(enemy_toughness) + '\n' +  \
                #     "enemy_strength: " + str(enemy_strength) + '\n' +  \
                #     "enemy_xp: " + str(enemy_xp) + '\n' +  \
                #     "enemy_head_hp: " + str(enemy_head_hp) + '\n' +  \
                #     "enemy_chest_hp: " + str(enemy_chest_hp) + '\n' +  \
                #     "enemy_right_arm_hp: " + str(enemy_right_arm_hp) + '\n' +  \
                #     "enemy_left_arm_hp: " + str(enemy_left_arm_hp) + '\n' +  \
                #     "enemy_right_leg_hp: " + str(enemy_right_leg_hp) + '\n' +  \
                #     "enemy_left_leg_hp: " + str(enemy_left_leg_hp) + '\n') 

            elif buff_or_debuff_chance >= 11 and buff_or_debuff_chance <= 20:
                # Get Enemy name length, randomise name and apply it to enemy
                enemy_buff_adjectives = data["enemies"]["positive_adjectives"]
                max_enemy_name_index = len(enemy_buff_adjectives)

                random_buff_adjective_index = randint(0, max_enemy_name_index - 1)
                monster_buff_adjective = enemy_buff_adjectives[random_buff_adjective_index]

                fighter_component = Fighter(hp = (enemy_hp + randint(0, 4)), head_hp = (enemy_head_hp + randint(0, 15 - 5)), chest_hp = (enemy_chest_hp + randint(0, 15 - 5)), right_arm_hp = (enemy_right_arm_hp + randint(0, 15 - 5)), left_arm_hp = (enemy_left_arm_hp + randint(0, 15 - 5)), right_leg_hp = (enemy_right_leg_hp + randint(0, 15 - 5)), left_leg_hp = enemy_left_leg_hp + randint(0, 15 - 5), toughness = (enemy_toughness + randint(0, 2 - 1)), strength = (enemy_strength + randint(0, 2 - 1)), xp = (enemy_xp + randint(0, 10 - 5)))
                monster = Entity(x, y, enemy_char, tc.desaturated_green, monster_buff_adjective + " " + enemy_name, blocks = enemy_blocks, render_order=RenderOrder.ACTOR, fighter = fighter_component, ai = ai_component)

        else:
            monster = Entity(x, y, enemy_char, tc.desaturated_green, enemy_name, blocks = enemy_blocks, render_order=RenderOrder.ACTOR, fighter = fighter_component, ai = ai_component)

        entities.append(monster)

        # equippable_component = Equippable("MAIN_HAND", strength_bonus = 5)
        # item = Entity(monster.x - 1, monster.y - 1, 'W' , tc.sky, "Morning-Star", equippable=equippable_component)
        # entities.append(item)

def cycle_target_distance_to(self, other):
    dx = other.x - self.x
    dy = other.y - self.y
    return math.sqrt(dx ** 2 + dy ** 2)