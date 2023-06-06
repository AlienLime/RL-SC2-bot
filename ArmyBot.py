from sc2.bot_ai import BotAI  # parent class we inherit from
#from sc2.data import Difficulty, Race  # difficulty for bots, race for the 1 of 3 races
#from sc2.main import run_game  # function that facilitates actually running the agents in games
#from sc2.player import Bot, Computer  #wrapper for whether or not the agent is one of your bots, or a "computer" player
#from sc2 import maps  # maps method for loading maps to play in.
from sc2.ids.unit_typeid import UnitTypeId

import sc2.main
import numpy as np
import random
import cv2
import math
import time
import sys
# import asyncio



class ArmyBot(BotAI): # inhereits from BotAI (part of BurnySC2)
    action = None
    output = {"observation" : map, "reward" : 0, "action" : None, "done" : False}
    def __init__(self, *args,bot_in_box=None, action_in=None, result_out=None, **kwargs, ):
        super().__init__(*args, **kwargs)
        self.action_in = action_in
        self.result_out = result_out

    async def on_end(self,game_result):
        print ("Game over!")
        reward = 0
        
        # Values: [MarineHealth, ZergDist, WeaponCD, MarineNr, SCVNr, Minerals]
        obs = np.zeros(6, dtype=np.uint8)
        obs[1] = 0
        obs[3] = self.army_count
        obs[4] = self.supply_workers
        obs[5] = self.minerals
        
        cv2.destroyAllWindows()
        #cv2.waitKey(1)
        
        if str(game_result) == "Result.Victory":
            for marine in self.units(UnitTypeId.MARINE):
                if marine.health_percentage < 1:
                    reward += marine.health
                    obs[0] = marine.health
                    obs[2] = int(marine.weapon_cooldown * 100)
                    
        else:
            reward = -100


        self.result_out.put({"observation" : obs, "reward" : reward, "action" : None, "done" : True, "truncated" : False, "info" : {}})
        
    
    async def on_step(self, iteration): # on_step is a method that is called every step of the game.
        self.action = self.action_in.get()
        '''
        0: Force Move
        1: Attack Move
        '''
        if iteration % 10 == 0:
            print("armybot at...", iteration)
        # if self.bot_in_box is not None:
        #     action = self.bot_in_box.get()
        #     print("action,", action)
        #     action = asyncio.run(action)
        #print("Got action from outside", self.action, "I will now execute that action.")
        # print("<updating...")
        # This gets an action and returns a state. You probably need to put logic here such as waiting a certain amount of in-game time before retuning etc. (you
        # don't want the states to be 'too close' if that makes sense)

        if self.action is None:
            # print("no action returning.")
            return None
        time.sleep(0.05)
        # 0: Force Move
        #print("Action is", self.action)
        if self.action == 0:
            try:
                for marine in self.units(UnitTypeId.MARINE):
                    for sd in self.structures(UnitTypeId.SUPPLYDEPOT):
                        marine.move(sd)
            except Exception as e:
                print(e)

        #1: Attack Move
        elif self.action == 1:
            try:
                for marine in self.units(UnitTypeId.MARINE):
                    marine.attack(random.choice(self.enemy_units))
            except Exception as e:
                print(e)

        #print("returning a result from army bot..")

        # Values: [MarineHealth, ZergDist, WeaponCD, MarineNr, SCVNr, Minerals]
        obs = np.zeros(6, dtype=np.uint8)
        obs[3] = self.army_count
        obs[4] = self.supply_workers
        obs[5] = self.minerals

        # Compute reward
        reward = -1

        try:
            # iterate through our marines:
            for marine in self.units(UnitTypeId.MARINE):
                obs[0] = marine.health
                obs[1] = int(marine.distance_to(random.choice(self.enemy_units)) * 10)
                if marine.weapon_cooldown > 0:
                    obs[2] = 1

                # if marine is attacking and is in range of enemy unit:
                if marine.is_attacking:
                    reward += 1
                    if self.enemy_units.closer_than(5, marine) and marine.weapon_cooldown == 0:
                        reward += 1
                else:
                    if marine.weapon_cooldown > 0:
                        reward += 2

        except Exception as e:
            print("reward",e)
            reward = 0

        truncated = False
        if iteration == 500:

            truncated = True

        self.result_out.put({"observation" : obs, "reward" : reward, "action" : None, "done" : False, "truncated" : truncated, "info" : {}})
        


#time.sleep(3)
#sys.exit()