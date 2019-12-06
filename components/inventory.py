import tcod as tc

from entity import Entity
from components.equipment import Equipment
from components.equippable import Equippable
from equipment_slots import EquipmentSlots 

from game_messages import Message

class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    def add_item(self, item):
        results = []

        if len(self.items) >= self.capacity:
            results.append({
                'item_added': None,
                'message': Message('You cannot carry any more, your inventory is full', tc.yellow)
            })
        else:
            results.append({
                'item_added': item,
                # 'message': Message('You pick up the {0}!'.format(item.name), tc.blue)
                'message': Message('You pick up the {0}!'.format(item.name), tc.white)
            })

            self.items.append(item)

        return results

    def use(self, item_entity, **kwargs):
        results = []

        item_component = item_entity.item

        if item_component.use_function is None:
            equippable_component = item_entity.equippable

            if equippable_component:
                results.append({'equip': item_entity})
            else:
                results.append({'message': Message('The {0} cannot be used'.format(item_entity.name), tc.yellow)})
        else:
            if item_component.targeting and not (kwargs.get('target_x') or kwargs.get('target_y')):
                results.append({'targeting': item_entity})
            else:
                kwargs = {**item_component.function_kwargs, **kwargs}
                item_use_results = item_component.use_function(self.owner, **kwargs)

                for item_use_result in item_use_results:
                    if item_use_result.get('consumed'):

                        if item_entity.item.uses == None or item_entity.item.uses == 0:
                            self.remove_item(item_entity)

                        elif item_entity.item.uses == 1:
                            
                            self.items.remove(item_entity)

                            equippable_component = Equippable(EquipmentSlots.BOTH_HAND, strength_bonus = 1)
                            staff = Entity(0, 0, 'W', tc.sky, 'Depleted Fire Staff', equippable = equippable_component)
                            self.items.append(staff)

                        else:
                            item_entity.item.uses = item_entity.item.uses - 1

                results.extend(item_use_results)

        return results

    def remove_item(self, item):
        self.items.remove(item)

    def drop_item(self, item):
        results = []

        # if self.owner.name == 'Player':
        if self.owner.name == 'You':
            if self.owner.equipment.main_hand == item or self.owner.equipment.off_hand == item or self.owner.equipment.head_armour == item or self.owner.equipment.both_hand == item or self.owner.equipment.chest_armour == item:
                self.owner.equipment.toggle_equip(item)

        item.x = self.owner.x
        item.y = self.owner.y

        self.remove_item(item)

        # if self.owner.name == 'Player':
        if self.owner.name == 'You':
            # results.append({'item_dropped': item, 'message': Message('You dropped the {0}'.format(item.name), tc.yellow)})
            results.append({'item_dropped': item, 'message': Message('You dropped the {0}'.format(item.name), tc.white)})

        else:
            # results.append({'item_dropped': item, 'message': Message('{0}'.format(item.name), tc.yellow)})
            results.append({'item_dropped': item, 'message': Message('{0}'.format(item.name), tc.white)})

        return results