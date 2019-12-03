class Item:
    def __init__(self, use_function=None, targeting=False, targeting_message=None, ranged=None, uses=None, maxUses=None, **kwargs):
        self.use_function = use_function
        self.targeting = targeting
        self.targeting_message = targeting_message
        self.function_kwargs = kwargs
        self.ranged = ranged
        self.uses = uses
        self.maxUses = maxUses