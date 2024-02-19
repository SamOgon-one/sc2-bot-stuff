import os
import sys

from typing import Union
from loguru import logger

# sc2 imports
from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.ids.unit_typeid import UnitTypeId
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.effect_id import EffectId


class Test_bot(BotAI):

    def __init__(self):
        self.spawn = True

    async def on_start(self):
        self.client.game_step = 2    

    async def on_step(self, iteration):

        # Spawn units
        if self.spawn:
            self.spawn = False
            point = self.enemy_start_locations[0]
            await self.client.move_camera(point)            
            await self.client.debug_kill_unit(self.workers)

            # await self.client.debug_create_unit([[UnitTypeId., quantity, spawn_point, owner 1: my 2: enemy]]) # 
            await self.client.debug_create_unit([[UnitTypeId.LURKERMPBURROWED, 1, point + Point2((3, 0)), 2]]) # enemy
            await self.client.debug_create_unit([[UnitTypeId.MARINE, 1, point + Point2((6, 0)), 1]]) # my

        for effect in self.state.effects:
            if effect.id == EffectId.LURKERMP:

                # https://liquipedia.net/starcraft2/Lurker_(Legacy_of_the_Void)
                # every time spine apears, we get all spine positions from API. We need to calculate which particular spine is it

                print()
                print('time:', self.time) # 0.089 second between spines, note that game speed is 'faster' which is 1.4 of normal speed, so in liquipedia it is 0.125 second between spines 
                print('effect:', effect) # eg. effect: EffectId.LURKERMP with radius 0.5 at {(42.5, 25.5), (42.5, 22.5), (42.5, 28.5), (42.5, 24.5), (42.5, 30.5), (42.5, 27.5), (42.5, 23.5), (42.5, 26.5), (42.5, 29.5)}               

                # print('type of effect.positions:', type(effect.positions)) # set
                # print(list(effect.positions)) # need sort
                # print('effect.radius:', effect.radius) # 0.5


def main():
    run_game(
        maps.get("BlackburnAIE"),
        [Bot(Race.Terran, Test_bot()),
         Computer(Race.Zerg, Difficulty.CheatInsane)],
        realtime=False,
    )

if __name__ == "__main__":
    main()
