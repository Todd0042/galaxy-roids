import pygame
from entities.powerups import Powerup

class PowerupSpawner:
    """
    Creates powerups at a given position and inserts them into the correct groups.
    This is required because collision_misc.py calls .spawn(), not .add().
    """

    def __init__(self, powerup_group, all_sprites):
        self.powerup_group = powerup_group
        self.all_sprites = all_sprites

    def spawn(self, pos):
        # pos is a tuple (x, y)
        p = Powerup(pos[0], pos[1])

        # Add to the correct groups
        self.powerup_group.add(p)
        self.all_sprites.add(p)

        return p
