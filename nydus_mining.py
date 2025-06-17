# The Nydus can unload one unit every 8 game frames. Here, with game_step = 2, that means it will unload one unit every 4 iterations.
# The maximum throughput for a single mining base is likely around 16 drones continuously entering and exiting

import os
import sys

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


class Test_bot(BotAI):

    def __init__(self):
        self.worker_has_resource = dict()

    async def on_start(self):
        self.client.game_step = 2    

    async def on_step(self, iteration):

        # spawn nyduses
        if iteration == 0:
            far_expansion = max(self.expansion_locations_list, key=lambda p: p.distance_to(self.start_location) + p.distance_to(self.enemy_start_locations[0]))
            pos = far_expansion.towards(self.mineral_field.closer_than(8, far_expansion).center, 4) 
            await self.client.debug_create_unit([[UnitTypeId.NYDUSCANAL, 1, pos, 1]])                
            await self.client.debug_create_unit([[UnitTypeId.NYDUSNETWORK, 1, self.start_location + Point2((4, 0)), 1]])
            await self.client.debug_create_unit([[UnitTypeId.DRONE, 4, self.start_location, 1]])
            return

        # set rally and queue rally back to nydus, this avoids needing to manually command drones later
        if iteration == 1:
            nydus_network = self.structures(UnitTypeId.NYDUSNETWORK).first
            nydus_network(AbilityId.RALLY_BUILDING, self.townhalls.closest_to(nydus_network))
            nydus_network(AbilityId.RALLY_BUILDING, nydus_network, queue=True)
            for worker in self.workers:
                worker.smart(nydus_network)

            nydus_canal = self.structures(UnitTypeId.NYDUSCANAL).first     
            nydus_canal(AbilityId.RALLY_BUILDING, self.mineral_field.closest_to(nydus_canal))
            nydus_canal(AbilityId.RALLY_BUILDING, nydus_canal, queue=True)                       

        # nydus mining: basically unload drones from appropriate nydus

        # workers outside nydus 
        # mark if worker has resource, we will not see it when it's inside nydus
        for worker in self.workers:     
            # when nydus is close to townhal, after unload, workers jump back to nydus so fast, that there is no frame where can mark worker as without minerals                     
            if not worker.is_carrying_resource or worker.orders and worker.orders[0].target in self.townhalls.tags:
                self.worker_has_resource[worker.tag] = False

            else: # elif worker.is_carrying_resource:
                self.worker_has_resource[worker.tag] = True      

        nydus_network = self.structures(UnitTypeId.NYDUSNETWORK).first
        nydus_canal = self.structures(UnitTypeId.NYDUSCANAL).first # aka nydus worm        
                      
        # workers inside nydus 
        # all nyduses share same passengers
        # unload NYDUSNETWORK
        for worker in nydus_network.passengers:              
            if self.worker_has_resource[worker.tag]:
                # custom unload method, based on: https://github.com/BurnySc2/python-sc2/blob/2e5d29671cf6ebcf78b1764c8153916b01c096ca/examples/protoss/single_unit_unload_test.py
                # we can't use ability unload_all because we need to unload specific passenger
                await self.client.unload_unit(transporter_unit=nydus_network, cargo_unit=worker)
                break

        # unload NYDUSCANAL
        for worker in nydus_network.passengers:
            if not self.worker_has_resource[worker.tag]:
                await self.client.unload_unit(transporter_unit=nydus_canal, cargo_unit=worker)
                break

     


def main():
    run_game(
        maps.get("BlackburnAIE"),
        [Bot(Race.Zerg, Test_bot()),
         Computer(Race.Terran, Difficulty.CheatInsane)],
        realtime=False,
    )


if __name__ == "__main__":
    main()
