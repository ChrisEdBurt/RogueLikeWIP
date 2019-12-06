from enum import Enum

class GameStates(Enum):
    PLAYERS_TURN = 1
    ENEMY_TURN = 2
    PLAYER_DEAD = 3
    SHOW_INVENTORY = 4
    DROP_INVENTORY = 5
    TARGETING = 6
    LEVEL_UP = 7
    CHARACTER_SCREEN = 8
    RANGED = 9
    CYCLE_TARGET = 10
    SHOW_TUTORIAL = 11
    SHOW_HELP_MENU = 12