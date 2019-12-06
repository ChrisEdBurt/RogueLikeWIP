import tcod as tc

from random import randint
from math import atan2, degrees, cos, sin, tan
# from entity import get_blocking_entities_at_location
from game_messages import Message

class BasicMonster:
    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        monster = self.owner
        
        if tc.map_is_in_fov(fov_map, monster.x, monster.y):

            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)

                if monster.fighter.turns_since_special <= 5:
                    monster.fighter.turns_since_special += 1

            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)

        else:
            if monster.fighter.turns_since_special <= 5:
                monster.fighter.turns_since_special += 1

        return results

class ConfusedMonster:
    def __init__(self, previous_ai, number_of_turns=5):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns

    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        if self.number_of_turns > 0:
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1

            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, game_map, entities)

            self.number_of_turns -= 1
        else:
            self.owner.ai = self.previous_ai
            # results.append({'message': Message('The {0} is no longer confused!'.format(self.owner.name), tc.red)})
            results.append({'message': Message('The {0} is no longer confused!'.format(self.owner.name), tc.white)})


        return results

class RetreatingMonster:
    def take_turn(self, target, fov_map, game_map, entities):

        results = []
        monster = self.owner
        valid_dir = []

        health_remaining_percent = ((monster.fighter.hp / monster.fighter.base_max_hp) * 100)

        if tc.map_is_in_fov(fov_map, monster.x, monster.y) and health_remaining_percent >= 25:
            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)

            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)

            return results

        elif tc.map_is_in_fov(fov_map, monster.x, monster.y) and health_remaining_percent <= 25:

            if monster.distance_to(target) <= 3:

                for r in range(8):

                    if r == 0:
                        if not (game_map.is_blocked(monster.x, monster.y - 1) or get_blocking_entities_at_location(entities, monster.x, monster.y - 1)):
                            valid_dir.append("N")

                    elif r == 1:
                        if not (game_map.is_blocked(monster.x + 1, monster.y - 1) or get_blocking_entities_at_location(entities, monster.x + 1, monster.y - 1)):
                            valid_dir.append("NE")

                    elif r == 2:
                        if not (game_map.is_blocked(monster.x + 1, monster.y) or get_blocking_entities_at_location(entities, monster.x + 1, monster.y)):
                            valid_dir.append("E")

                    elif r == 3:
                        if not (game_map.is_blocked(monster.x + 1, monster.y + 1) or get_blocking_entities_at_location(entities, monster.x + 1, monster.y + 1)):
                            valid_dir.append("SE")

                    elif r == 4:
                        if not (game_map.is_blocked(monster.x, monster.y + 1) or get_blocking_entities_at_location(entities, monster.x, monster.y + 1)):
                            valid_dir.append("S")

                    elif r == 5:
                        if not (game_map.is_blocked(monster.x - 1, monster.y + 1) or get_blocking_entities_at_location(entities, monster.x - 1, monster.y + 1)):
                            valid_dir.append("SW")

                    elif r == 6:
                        if not (game_map.is_blocked(monster.x - 1, monster.y) or get_blocking_entities_at_location(entities, monster.x - 1, monster.y)):
                            valid_dir.append("W")

                    elif r == 7:
                        if not (game_map.is_blocked(monster.x - 1, monster.y - 1) or get_blocking_entities_at_location(entities, monster.x - 1, monster.y - 1)):
                            valid_dir.append("NW")

                rand_choice = randint(0,len(valid_dir) - 1)

                if valid_dir[rand_choice] == "N":
                    monster.move(0, -1)

                elif valid_dir[rand_choice] == "NE":
                    monster.move(1, -1) 

                elif valid_dir[rand_choice] == "E":
                    monster.move(1,0)
                    
                elif valid_dir[rand_choice] == "SE":
                    monster.move(1,1)

                elif valid_dir[rand_choice] == "S":
                    monster.move(0, 1) 

                elif valid_dir[rand_choice] == "SW":
                    monster.move(-1,1) 

                elif valid_dir[rand_choice] == "W":
                    monster.move(-1,0)

                elif valid_dir[rand_choice] == "NW":
                    monster.move(-1,-1)

                else:
                    results.append({'message': Message('The {0} is paralysed with fear!'.format(self.owner.name), tc.red)})

            return results    

        else:
            return results

def get_blocking_entities_at_location(entities, destination_x, destination_y):
    for entity in entities:
        if entity.blocks and entity.x == destination_x and entity.y == destination_y:
            return entity

    return None