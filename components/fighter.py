import tcod as tc 

from random import randint
from game_messages import Message
from loader_functions.data_loaders import load_json

class Fighter:
    def __init__(self, hp, head_hp, chest_hp, right_arm_hp, left_arm_hp, right_leg_hp, left_leg_hp, toughness, strength, xp = 0):
        self.base_max_hp = hp
        self.hp = hp

        self.head_max_hp = head_hp
        self.head_hp = head_hp

        self.chest_hp_max = chest_hp
        self.chest_hp = chest_hp

        self.right_arm_max_hp = right_arm_hp
        self.right_arm_hp = right_arm_hp
        self.left_arm_max_hp = left_arm_hp
        self.left_arm_hp = left_arm_hp
        
        self.left_leg_max_hp = left_leg_hp
        self.left_leg_hp = left_leg_hp

        self.right_leg_max_hp = right_leg_hp
        self.right_leg_hp = right_leg_hp

        self.base_defense = toughness
        self.base_strength = strength
        self.xp = xp

        self.head_broken = False
        self.chest_broken = False
        self.right_arm_broken = False
        self.left_arm_broken = False
        self.right_leg_broken = False
        self.left_leg_broken = False

        self.hunger = 100
        self.thirst = 100

        self.is_burning = False
        self.is_poisoned = False

        self.turns_since_special = 0
        self.poison_turns_remaining = 0

    @property
    def max_hp(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.max_hp_bonus
        else:
            bonus = 0

        return self.base_max_hp + bonus

    @property
    def attack_damage(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.strength_bonus
        else:
            bonus = 0

        return self.base_strength + bonus

    @property
    def strength(self):
        return self.base_strength

    @property
    def defense(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.defense_bonus
        else:
            bonus = 0

        return self.base_defense + bonus 

    @property
    def burning(self):
        if self.owner.is_burning != False:
            burning = True
        else:
            burning = False

        return burning

    @property
    def poisoned(self):
        if self.owner.is_poisoned != False:
            poisoned = True
        else:
            poisoned = False

        return poisoned

    @property
    def hunger_level(self):
        return self.owner.fighter.hunger

    @property
    def thirst_level(self):
        return self.owner.fighter.thirst
    
    @property
    def toughness(self):
        return self.base_defense

    def take_damage(self, amount):
        results = []

        random__limb = randint(0, 100) - 1
        
        #HEAD DAMAGE
        if random__limb >= 0 and random__limb <= 9:
            self.head_hp -= amount * 2
        
        #CHEST DAMAGE
        if random__limb >= 10 and random__limb <= 29:
            self.chest_hp -= amount * 2

        #LEFT ARM
        if random__limb >= 30 and random__limb <= 49:
            self.left_arm_hp -= amount * 2

            if self.left_arm_hp <= 10 and self.left_arm_broken == False:
                self.left_arm_broken = True
                results.append({'message': Message('Your left arm has been broken!.'.format(), tc.red)})
                results.append({'message': Message('Flee. Heal or Fight!.'.format(), tc.red)})
                if self.owner.equipment.off_hand != None:
                    results.append({'message': Message('Dequipped {0}'.format(self.owner.equipment.off_hand.name), tc.red)})
                elif self.owner.equipment.both_hand != None:
                    results.append({'message': Message('Dequipped {0}'.format(self.owner.equipment.both_hand.name), tc.red)})
                self.owner.equipment.off_hand = None
                self.owner.equipment.both_hand = None

        #RIGHT ARM
        if random__limb >= 50 and random__limb <= 69:
            self.right_arm_hp -= amount * 2

            if self.right_arm_hp <= 10 and self.right_arm_broken == False:
                self.right_arm_broken = True
                results.append({'message': Message('Your right arm has been broken!.'.format(), tc.red)})
                results.append({'message': Message('Flee. Heal or Fight!.'.format(), tc.red)})
                if self.owner.equipment.main_hand != None:
                    results.append({'message': Message('Dequipped {0}'.format(self.owner.equipment.main_hand.name), tc.red)})
                elif self.owner.equipment.both_hand != None:
                    results.append({'message': Message('Dequipped {0}'.format(self.owner.equipment.both_hand.name), tc.red)})
                self.owner.equipment.main_hand = None
                self.owner.equipment.both_hand = None
               
        #LEFT LEG
        if random__limb >= 70 and random__limb <= 84:
            self.left_leg_hp -= amount * 2

        #RIGHT LEG
        if random__limb >= 85 and random__limb <= 100:
            self.right_leg_hp -= amount * 2
        
        self.hp -= amount

        if self.hp <= 0:
            results.append({'dead': self.owner, 'xp': self.xp})
            return results

        return results

    def heal(self, amount):
        self.hp += amount

        self.head_hp += (amount / 5)
        self.chest_hp += (amount / 5)
        self.right_arm_hp += (amount / 5)
        self.left_arm_hp += (amount / 5)
        self.right_leg_hp += (amount / 5)
        self.left_leg_hp += (amount / 5)

        if self.hp > self.max_hp:
            self.hp = self.max_hp

        if self.head_hp > 100:
            self.head_hp = 100

        if self.chest_hp > 100:
            self.chest_hp = 100

        if self.right_arm_hp > 100:
            self.right_arm_hp = 100

        if self.left_arm_hp > 100:
            self.left_arm_hp = 100

        if self.right_leg_hp > 100:
            self.right_leg_hp = 100

        if self.left_leg_hp > 100:
            self.left_leg_hp = 100

    def attack(self, target):
        results = []

        random_special_chance = randint(1, 100)
        if random_special_chance >= 1 and random_special_chance <= 10 and self.owner.fighter.turns_since_special == 6:
            data = load_json()

            if self.owner.name.capitalize() != "You":

                enemy_name = self.owner.name.capitalize()
                if ' ' in enemy_name:
                    enemy_name_split =  enemy_name.split(' ')
                    enemy_name = enemy_name_split[1]
                    special_info = data["enemy_list"]["enemy_name"][enemy_name.capitalize()]["fighter"]["special_attacks"]

                else:
                    special_info = data["enemy_list"]["enemy_name"][self.owner.name]["fighter"]["special_attacks"]

                special_info_length = len(special_info)
                random_special_index = randint(0, special_info_length - 1)
                atack_description = special_info[random_special_index][1]
                attack_type = special_info[random_special_index][2]
                atack_damage = special_info[random_special_index][3]
                
                if attack_type == "Damage": 
                    total_damage = self.attack_damage + atack_damage - target.fighter.defense
                    results.append({'message': Message('{0} {1} for {2} damage'.format(self.owner.name.capitalize(), atack_description, str(total_damage)), tc.red)})
                    results.extend(target.fighter.take_damage(total_damage))
                    
                    self.owner.fighter.turns_since_special = 0
                    return results

                elif attack_type == "Effect":
                    attack_effect = special_info[random_special_index][3]

                    if attack_effect == "poisoned":
                        results.append({'message': Message('{0} {1},you got {2}'.format(self.owner.name.capitalize(), atack_description, attack_effect), tc.red)})
                        target.fighter.is_poisoned = True
                        target.fighter.poison_turns_remaining = 5

                        self.owner.fighter.turns_since_special = 0
                        return results

                    elif attack_effect == "burning":
                        results.append({'message': Message('{0} {1},you are {2}'.format(self.owner.name.capitalize(), atack_description, attack_effect), tc.red)})
                        target.fighter.is_burning = True
                        target.fighter.burning_turns_remaining = 5

                        self.owner.fighter.turns_since_special = 0
                        return results

                    elif attack_effect == "drain":
                        results.append({'message': Message('{0} {1}, you lost {3} life points'.format(self.owner.name.capitalize(), atack_description, attack_effect, self.owner.fighter.strength), tc.red)})
                        if self.owner.fighter.hp + self.owner.fighter.strength > self.owner.fighter.base_max_hp:
                            self.owner.fighter.hp = self.owner.fighter.base_max_hp
                        else:
                            self.owner.fighter.hp += self.owner.fighter.strength
                            target.fighter.hp -= self.owner.fighter.strength

                        self.owner.fighter.turns_since_special = 0
                        return results

                    else:
                        results.append({'message': Message('{0} got hit by an unknown attack, you lost 5 life points'.format(self.owner.name.capitalize()), tc.red)})
                        target.fighter.hp -= 5  

                        self.owner.fighter.turns_since_special = 0
                        return results


            if self.owner.name.capitalize() == "You":

                if self.owner.equipment.main_hand != None:

                    weapon_name = self.owner.equipment.main_hand.name  
                    if ' ' in weapon_name:
                        weapon_name_split =  weapon_name.split(' ')
                        weapon_name = weapon_name_split[1]
                        
                    if weapon_name in data["items"]["special_attacks"].keys():
                        mainhand_special_info = data["items"]["special_attacks"][weapon_name]
                        mainhand_special_info_length = len(mainhand_special_info)
                        mainhand_random_special_index = randint(0, mainhand_special_info_length - 1)
                        mainhand_atack_description = mainhand_special_info[mainhand_random_special_index][1]
                        mainhand_attack_type = mainhand_special_info[mainhand_random_special_index][2]
                        
                        if mainhand_attack_type == "Damage": 
                            mainhand_atack_damage = mainhand_special_info[mainhand_random_special_index][3]
                            total_damage = self.attack_damage + mainhand_atack_damage - target.fighter.defense
                            # tc.blue
                            results.append({'message': Message('{0} for {1} damage'.format(mainhand_atack_description, str(total_damage)), tc.yellow)})
                            results.extend(target.fighter.take_damage(total_damage))
                            
                            self.owner.fighter.turns_since_special = 0
                            return results

                        elif mainhand_attack_type == "Effect":
                            mainhand_atack_effect = mainhand_special_info[mainhand_random_special_index][3]

                            if mainhand_atack_effect == "poisoned":
                                # tc.blue
                                results.append({'message': Message('{0}, you {1} {2}'.format(mainhand_atack_description, mainhand_atack_effect, target.name), tc.yellow)})
                                target.fighter.is_poisoned = True
                                target.fighter.poison_turns_remaining = 5

                                self.owner.fighter.turns_since_special = 0
                                return results

                            elif mainhand_atack_effect == "burning":
                                results.append({'message': Message('{0} {1},you are {2}'.format(self.owner.name.capitalize(), mainhand_atack_description, mainhand_atack_effect), tc.red)})
                                target.fighter.is_burning = True
                                target.fighter.burning_turns_remaining = 5

                                self.owner.fighter.turns_since_special = 0
                                return results

                            elif mainhand_atack_effect == "drain":
                                results.append({'message': Message('{0} {1}, you lost {3} life points'.format(self.owner.name.capitalize(), mainhand_atack_description, mainhand_atack_effect, self.owner.fighter.strength), tc.red)})
                                if self.owner.fighter.hp + self.owner.fighter.strength > self.owner.fighter.base_max_hp:
                                    self.owner.fighter.hp = self.owner.fighter.base_max_hp
                                else:
                                    self.owner.fighter.hp += self.owner.fighter.strength
                                    target.fighter.hp -= self.owner.fighter.strength

                                self.owner.fighter.turns_since_special = 0
                                return results

                            else:
                                results.append({'message': Message('{0} did an attack but you dont know how.'.format(self.owner.name.capitalize()), tc.red)})
                                target.fighter.hp -= 5  

                                self.owner.fighter.turns_since_special = 0
                                return results

                elif self.owner.equipment.both_hand != None:

                    weapon_name = self.owner.equipment.both_hand.name
                    if ' ' in weapon_name:
                        weapon_name_split =  weapon_name.split(' ')
                        weapon_name = weapon_name_split[1]

                    if weapon_name in data["items"]["special_attacks"].keys(): 
                        twohand_special_info = data["items"]["special_attacks"][weapon_name]
                        twohand_special_info_length = len(twohand_special_info)
                        twohand_random_special_index = randint(0, twohand_special_info_length - 1)
                        twohand_atack_description = twohand_special_info[twohand_random_special_index][1]
                        twohand_attack_type = twohand_special_info[twohand_random_special_index][2]

                        if twohand_attack_type == "Damage": 
                            twohand_atack_damage = twohand_special_info[twohand_random_special_index][3]
                            total_damage = self.attack_damage + twohand_atack_damage - target.fighter.defense
                            # tc.blue
                            results.append({'message': Message('{0} for {1} damage'.format(twohand_atack_description, str(total_damage)), tc.yellow)})
                            results.extend(target.fighter.take_damage(total_damage))
                            
                            self.owner.fighter.turns_since_special = 0
                            return results

                        elif twohand_attack_type == "Effect":
                            twohand_atack_effect = twohand_special_info[twohand_random_special_index][3]

                            if twohand_atack_effect == "poisoned":
                                # tc.blue
                                results.append({'message': Message('{0}, you {1} {2}'.format(twohand_atack_description, twohand_atack_effect, target.name), tc.yellow)})   
                                self.owner.turns_since_special = 0
                                target.fighter.is_poisoned = True
                                target.fighter.poison_turns_remaining = 5

                                self.owner.fighter.turns_since_special = 0
                                return results

                            elif twohand_atack_effect == "burning":
                                results.append({'message': Message('{0} {1},you are {2}'.format(self.owner.name.capitalize(), twohand_atack_description, twohand_atack_effect), tc.red)})
                                target.fighter.is_burning = True
                                target.fighter.burning_turns_remaining = 5

                                self.owner.fighter.turns_since_special = 0
                                return results

                            elif twohand_atack_effect == "drain":
                                results.append({'message': Message('{0} {1}, you lost {3} life points'.format(self.owner.name.capitalize(), twohand_atack_description, twohand_atack_effect, self.owner.fighter.strength), tc.red)})
                                if self.owner.fighter.hp + self.owner.fighter.strength > self.owner.fighter.base_max_hp:
                                    self.owner.fighter.hp = self.owner.fighter.base_max_hp
                                else:
                                    self.owner.fighter.hp += self.owner.fighter.strength
                                    target.fighter.hp -= self.owner.fighter.strength

                                self.owner.fighter.turns_since_special = 0
                                return results

                            else:
                                results.append({'message': Message('{0} did an attack but you dont know how.'.format(self.owner.name.capitalize()), tc.red)})
                                target.fighter.hp -= 5  

                                self.owner.fighter.turns_since_special = 0
                                return results

                elif self.owner.equipment.both_hand == None and self.owner.equipment.main_hand == None:

                    barehanded_special_info = data["items"]["special_attacks"]["Barehanded"]
                    barehanded_special_info_length = len(barehanded_special_info)
                    barehanded_random_special_index = randint(0, barehanded_special_info_length - 1)
                    barehanded_atack_description = barehanded_special_info[barehanded_random_special_index][1]
                    barehanded_atack_damage = barehanded_special_info[barehanded_random_special_index][3]

                    damage = self.attack_damage + barehanded_atack_damage - target.fighter.defense
                    
                    # results.append({'message': Message('{0} for {1} damage'.format(barehanded_atack_description, str(damage)), tc.blue)})
                    results.append({'message': Message('{0} for {1} damage'.format(barehanded_atack_description, str(damage)), tc.yellow)})
                    results.extend(target.fighter.take_damage(damage))

                    self.owner.fighter.turns_since_special = 0
                    return results

        else:

            damage = self.attack_damage - target.fighter.defense

            if self.owner.name != "You":
                if damage > 0:
                    results.append({'message': Message('{0} attacks {1} for {2} hit points'.format(self.owner.name, target.name, str(damage)), tc.white)})
                    results.extend(target.fighter.take_damage(damage))

                else:
                    results.append({'message': Message('{0} attacks {1} but does no damage'.format(self.owner.name, target.name), tc.white)})

            else:
                if damage > 0:
                    results.append({'message': Message('{0} attack {1} for {2} hit points'.format(self.owner.name.capitalize(), target.name, str(damage)), tc.white)})
                    results.extend(target.fighter.take_damage(damage))

                else:
                    results.append({'message': Message('{0} attack {1} but does no damage'.format(self.owner.name.capitalize(), target.name), tc.white)})

            if self.owner.fighter.turns_since_special <= 5:
                self.turns_since_special += 1

            return results

    def get_stats(self):

        if self.fighter == None:
            stats = ""

        else:
            stats = ""
            stats = stats + " Attack:" + str(self.fighter.attack_damage) + " Defence:" + str(self.fighter.defense) + " Max HP:" + str(self.fighter.max_hp) + " Current HP:" + str(self.fighter.hp) + " XP:" + str(self.fighter.xp)

        return stats

    def take_poison_damage(self):

        if self.owner.name == "You":

            if self.owner.fighter.poison_turns_remaining == 1:
                poison_damage = int(self.owner.fighter.hp / 25)
                self.owner.fighter.hp -= poison_damage
                poison_message = Message('{0} have filtered the last of the poison!'.format(self.owner.name), tc.blue)
                self.owner.fighter.poison_turns_remaining = 0
                self.owner.fighter.is_poisoned = False
                self.owner.color = tc.white

                return poison_message

            else:
                self.owner.color = tc.green
                poison_damage = int(self.owner.fighter.hp / 25)
                self.owner.fighter.hp -= poison_damage
                poison_message = Message('The poison courses through {0}, it inflicts {1} damage'.format(self.owner.name, str(poison_damage)), tc.red)
                self.owner.fighter.poison_turns_remaining -= 1

                return poison_message

        else:

            if self.owner.fighter.poison_turns_remaining == 1:
                poison_damage = int(self.owner.fighter.hp / 10)
                self.owner.fighter.hp -= poison_damage
                poison_message = Message('{0} have filtered the last of the poison!'.format(self.owner.name), tc.red)
                self.owner.fighter.poison_turns_remaining = 0
                self.owner.fighter.is_poisoned = False
                self.owner.color = tc.white

                return poison_message

            else:
                self.owner.color = tc.green
                poison_damage = int(self.owner.fighter.hp / 10)
                self.owner.fighter.hp -= poison_damage
                poison_message = Message('The poison courses through {0}, it inflicts {1} damage'.format(self.owner.name, str(poison_damage)), tc.blue)
                self.owner.fighter.poison_turns_remaining -= 1

                return poison_message

    def take_burning_damage(self):

        if self.owner.name == "You":

            if self.owner.fighter.burning_turns_remaining == 1:
                burning_damage = int(self.owner.fighter.hp / 25)
                self.owner.fighter.hp -= burning_damage
                burning_message = Message('{0} were able to extinguish the flames!'.format(self.owner.name), tc.blue)
                self.owner.fighter.burning_turns_remaining = 0
                self.owner.fighter.is_burning = False
                self.owner.color = tc.white

                return burning_message

            else:
                self.owner.color = tc.red
                burning_damage = int(self.owner.fighter.hp / 25)
                self.owner.fighter.hp -= burning_damage
                burning_message = Message('{0} are engulfed in flames, it inflicts {1} damage'.format(self.owner.name, str(burning_damage)), tc.red)
                self.owner.fighter.burning_turns_remaining -= 1

                return burning_message

        else:
            if self.owner.fighter.burning_turns_remaining == 1:
                burning_damage = int(self.owner.fighter.hp / 10)
                self.owner.fighter.hp -= burning_damage
                burning_message = Message('{0} were able to extinguish the flames!'.format(self.owner.name), tc.red)
                self.owner.fighter.burning_turns_remaining = 0
                self.owner.fighter.is_burning = False
                self.owner.color = tc.white

                return burning_message

            else:
                self.owner.color = tc.red
                burning_damage = int(self.owner.fighter.hp / 10)
                self.owner.fighter.hp -= burning_damage
                burning_message = Message('{0} are engulfed in flames, it inflicts {1} damage'.format(self.owner.name, str(burning_damage)), tc.blue)
                self.owner.fighter.burning_turns_remaining -= 1

                return burning_message