from equipment_slots import EquipmentSlots

class Equipment:
    def __init__(self, main_hand = None, off_hand = None, both_hand = None, head_armour = None, chest_armour = None):
        self.main_hand = main_hand
        self.off_hand = off_hand
        self.both_hand = both_hand
        self.head_armour = head_armour
        self.chest_armour = chest_armour

    @property
    def max_hp_bonus(self):
        bonus = 0

        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.max_hp_bonus

        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.max_hp_bonus

        return bonus

    @property
    def strength_bonus(self):
        bonus = 0

        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.strength_bonus

        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.strength_bonus

        if self.both_hand and self.both_hand.equippable:
            bonus += self.both_hand.equippable.strength_bonus

        return bonus

    @property
    def defense_bonus(self):
        bonus = 0

        if self.main_hand and self.main_hand.equippable:
            bonus += self.main_hand.equippable.defense_bonus

        if self.off_hand and self.off_hand.equippable:
            bonus += self.off_hand.equippable.defense_bonus

        if self.head_armour and self.head_armour.equippable:
            bonus += self.head_armour.equippable.defense_bonus

        if self.chest_armour and self.chest_armour.equippable:
            bonus += self.chest_armour.equippable.defense_bonus

        return bonus

    @property
    def intelligence_bonus(self):
        bonus = 0

        if self.chest_armour and self.chest_armour.equippable:
            bonus += self.chest_armour.equippable.intelligence_bonus

        return bonus

    def toggle_equip(self, equippable_entity):
        results = []

        slot = equippable_entity.equippable.slot

        if slot == EquipmentSlots.MAIN_HAND:

            if self.owner.fighter.right_arm_hp <= 10 and self.owner.fighter.right_arm_broken == True:
                results.append({'unequipped': equippable_entity})
                self.main_hand = None

            if self.owner.fighter.right_arm_hp <= 10:
                results.append({'failed': equippable_entity})

            else:
                
                if self.main_hand == equippable_entity:
                    self.main_hand = None
                    results.append({'unequipped': equippable_entity})
                
                else:
                    if self.main_hand:
                        results.append({'unequipped': self.main_hand})

                    if self.both_hand:
                        results.append({'unequipped': self.both_hand})
                        self.both_hand = None

                    self.main_hand = equippable_entity
                    results.append({'equipped': equippable_entity})

        elif slot == EquipmentSlots.OFF_HAND:

            if self.owner.fighter.left_arm_hp <= 10 and self.owner.fighter.left_arm_broken == True:
                results.append({'unequipped': equippable_entity})
                self.off_hand = None

            if self.owner.fighter.left_arm_hp <= 10:
                results.append({'failed': equippable_entity})

                return results

            else:
                if self.off_hand == equippable_entity:
                    self.off_hand = None
                    results.append({'unequipped': equippable_entity})
                else:
                    if self.off_hand:
                        results.append({'unequipped': self.off_hand})

                    if self.both_hand:
                        results.append({'unequipped': self.both_hand})
                        self.both_hand = None

                    self.off_hand = equippable_entity
                    results.append({'equipped': equippable_entity})

        elif slot == EquipmentSlots.BOTH_HAND:

            if self.owner.fighter.left_arm_hp <= 10 or self.owner.fighter.right_arm_hp <= 10 \
                or self.owner.fighter.right_arm_broken == True or self.owner.fighter.left_arm_broken == True:
                results.append({'unequipped': equippable_entity})
                self.both_hand = None

            if self.owner.fighter.left_arm_hp <= 10 or self.owner.fighter.right_arm_hp <= 10:
                results.append({'failed': equippable_entity})

            else:

                if self.both_hand == equippable_entity:
                    self.both_hand = None
                    results.append({'unequipped': equippable_entity})

                else:
                    if self.both_hand:
                        results.append({'unequipped': self.both_hand})

                    if self.main_hand or self.off_hand:
                        results.append({'unequipped': self.main_hand})
                        self.main_hand = None
                        
                        results.append({'unequipped': self.off_hand})
                        self.off_hand = None

                    self.both_hand = equippable_entity
                    results.append({'equipped': equippable_entity})

        elif slot == EquipmentSlots.HEAD_ARMOUR:
            if self.head_armour == equippable_entity:
                self.head_armour = None
                results.append({'unequipped': equippable_entity})
            else:
                if self.head_armour:
                    results.append({'unequipped': self.head_armour})

                self.head_armour = equippable_entity
                results.append({'equipped': equippable_entity})

        elif slot == EquipmentSlots.CHEST_ARMOUR:
            if self.chest_armour == equippable_entity:
                self.chest_armour = None
                results.append({'unequipped': equippable_entity})
            else:
                if self.chest_armour:
                    results.append({'unequipped': self.chest_armour})

                self.chest_armour = equippable_entity
                results.append({'equipped': equippable_entity})

        return results