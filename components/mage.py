import tcod as tc

from game_messages import Message

class Mage:
    def __init__(self, intelligence = 0):
        self.base_intelligence = intelligence

    @property
    def intelligence(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.intelligence_bonus
        else:
            bonus = 0

        return self.base_intelligence + bonus

    def get_stats(self):

        if self.mage == None:
            stats = ""

        else:
            stats = ""
            stats = stats + "Intelligence:" + str(self.mage.intelligence)

        return stats
