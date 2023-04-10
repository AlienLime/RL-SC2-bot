import gym
from gym import spaces
import numpy as np
import subprocess
import time
from threading import Thread
import asyncio
from queue import Queue
import os

from IncrediBot import IncrediBot

#API imports
from sc2.bot_ai import BotAI  # parent class we inherit from
from sc2.data import Difficulty, Race  # difficulty for bots, race for the 1 of 3 races
from sc2.main import run_game  # function that facilitates actually running the agents in games
from sc2.player import Bot, Computer  #wrapper for whether or not the agent is one of your bots, or a "computer" player
from sc2 import maps  # maps method for loading maps to play in.
from sc2.ids.unit_typeid import UnitTypeId

class AST(Thread):
    def __init__(self) -> None:
        super().__init__()
        self.action_in = Queue()
        self.result_out = Queue()

        # self.bot_in_box = asyncio.Queue()
        # self.loop = loop
        # self.bot = bot
    
    def run(self) -> None:
        # print("setting loop")
        #loop = asyncio.new_event_loop()
        #asyncio.set_event_loop(loop)
        # print("starting game.")
        self.bot = IncrediBot(action_in=self.action_in, result_out=self.result_out)
        print("starting gamem.")
        result = run_game(  # run_game is a function that runs the game.
			maps.get("WaterfallAIE"), # the map we are playing on
			[Bot(Race.Protoss, self.bot), # runs our coded bot, Terran race, and we pass our bot object 
            Computer(Race.Zerg, Difficulty.Hard)], # runs a pre-made computer agent, zerg race, with a hard difficulty.
            realtime=False, # When set to True, the agent is limited in how long each step can take to process.
        )
        if str(result) == "Result.Victory":
            rwd = 500
        else:
            rwd = -500
        
        map = np.zeros((144, 160, 3), dtype=np.uint8)
        self.result_out.put({"observation": map, "reward": rwd, "action": None, "done": True})

class Sc2Env(gym.Env):
	"""Custom Environment that follows gym interface"""
	def __init__(self):
		super(Sc2Env, self).__init__()
		# Define action and observation space
		# They must be gym.spaces objects
		# Example when using discrete actions:
		self.action_in = Queue()
		self.result_out = Queue()
		self.action_space = spaces.Discrete(6)
		self.observation_space = spaces.Box(low=0, high=255,
											shape=(144, 160, 3), dtype=np.uint8)

	def step(self, action):
		#wait_for_action = True
		# waits for action.
		#while wait_for_action:
		#	#print("waiting for action")
		#	try:
		#		with open('state_rwd_action.pkl', 'rb') as f:
		#			state_rwd_action = pickle.load(f)

		#			if state_rwd_action['action'] is not None:
		#				#print("No action yet")
		#				wait_for_action = True
		#			else:
		#				#print("Needs action")
		#				wait_for_action = False
		#				state_rwd_action['action'] = action
		#				with open('state_rwd_action.pkl', 'wb') as f:
		#					# now we've added the action.
		#					pickle.dump(state_rwd_action, f)
		#	except Exception as e:
		#		#print(str(e))
		#		pass

		self.pcom.action_in.put(f"A=action from step={action}")

		# waits for the new state to return (map and reward) (no new action yet. )
		#wait_for_state = True
		#while wait_for_state:
		#	try:
		#		if os.path.getsize('state_rwd_action.pkl') > 0:
		#			with open('state_rwd_action.pkl', 'rb') as f:
		#				state_rwd_action = pickle.load(f)
		#				if state_rwd_action['action'] is None:
		#					#print("No state yet")
		#					wait_for_state = True
		#				else:
		#					#print("Got state state")
		#					state = state_rwd_action['state']
		#					reward = state_rwd_action['reward']
		#					done = state_rwd_action['done']
		#					wait_for_state = False
#
		#	except Exception as e:
		#		wait_for_state = True   
		#		map = np.zeros((144, 160, 3), dtype=np.uint8)
		#		observation = map
		#		# if still failing, input an ACTION, 3 (scout)
		#		data = {"state": map, "reward": 0, "action": 3, "done": False}  # empty action waiting for the next one!
		#		with open('state_rwd_action.pkl', 'wb') as f:
		#			pickle.dump(data, f)

				#state = map
				#reward = 0
				#done = False
				#action = 3
		out = self.pcom.result_out.get()

		info ={}
		observation = out.get(observation)
		reward = out.get(reward)
		done = out.get(done)
		return observation, reward, done, info


	def reset(self):
		print("RESETTING ENVIRONMENT!!!!!!!!!!!!!")
		map = np.zeros((144, 160, 3), dtype=np.uint8)
		observation = map
		self.pcom = AST()
		self.pcom.start()

		# run incredibot-sct.py non-blocking:
		#print("Popen now!")
		#subprocess.Popen(['IncrediBot.py'], shell=True)
		#print("Popen gone through")
		return observation  # reward, done, info can't be included
