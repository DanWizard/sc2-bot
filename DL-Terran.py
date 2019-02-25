import sc2
from sc2 import run_game, maps, Race, Difficulty, position, Result
from sc2.player import Bot, Computer
from sc2.constants import COMMANDCENTER, BARRACKS, SUPPLYDEPOT, SCV, REFINERY, MARINE, FACTORY, HELLION
from sc2.position import Point2, Point3, Pointlike
import random
import cv2 
import numpy as np
import time

def recur():
	run_game(maps.get("CyberForestLE"), [
	Bot(Race.Terran, Hestia()),
	Computer(Race.Zerg, Difficulty.VeryEasy)],
	realtime = False)
	print("end of the GAMMMe")
	print("end of the GAMMMe")
	print("end of the GAMMMe")
	print("end of the GAMMMe")
	print("end of the GAMMMe")
	print("end of the GAMMMe")
	print("end of the GAMMMe")
	recur()


class Hestia(sc2.BotAI):

	def __init__(self):
		self.IPM = 165
		self.MW = 65
		self.scouted = False
		self.do_something_after = 0
		self.train_data = []

	def on_end(self, game_result):
		print('--- on_end called ---')
		print(game_result)
		if game_result == Result.Victory:
			np.save("train_data/{}.npy".format(str(int(time.time()))), np.array(self.train_data))


	async def on_step(self, iteration):
		self.iteration = iteration
		await self.scout()
		await self.distribute_workers()
		await self.build_workers()
		await self.build_supplydepot()
		await self.build_refinery()
		await self.expand()
		await self.offensive_force_buildings()
		await self.build_offensive_forces()
		await self.attack()
		await self.intel()
		depot_placement_positions = self.main_base_ramp.corner_depots
		# print(depot_placement_positions)
		# print(placement_grid)
	def random_location_variance(self, enemy_start_location):
		x = enemy_start_location[0]
		y = enemy_start_location[1]
		
		x += ((random.randrange(-20, 20))/100) * enemy_start_location[0]
		y += ((random.randrange(-20, 20))/100) * enemy_start_location[1]
		
		if x < 0:
			x = 0
		
		if y < 0:
			y = 0
		
		if x > self.game_info.map_size[0]:
			x = self.game_info.map_size[0]
		
		if y > self.game_info.map_size[1]:
			y = self.game_info.map_size[1]

		go_to = position.Point2(position.Pointlike((x,y)))
		return go_to
	

	async def scout(self):
		if not self.scouted:
			scout = self.units(SCV).first
			print(self.units(SCV))
			# print(scout.tag)
			enemy_location = self.enemy_start_locations[0]
			move_to = self.random_location_variance(enemy_location)
			await self.do(scout.move(move_to))
			self.scouted = True




	async def intel(self):

		game_data = np.zeros((self.game_info.map_size[1], self.game_info.map_size[0], 3), np.uint8)
		draw_dict = {
					COMMANDCENTER: [15,(0, 255, 0)],
					SUPPLYDEPOT: [3, (20,235,0)],
					SCV: [1,(55,200,0)],
					BARRACKS: [5,(255,0,0)],
					MARINE: [2,(255,100,0)]

					}
		for unit_type in draw_dict:
			for unit in self.units(unit_type).ready:
				pos = unit.position
				cv2.circle(game_data, (int(pos[0]), int(pos[1])), draw_dict[unit_type][0], draw_dict[unit_type][1] )

		main_base_names = ["nexus", "supplydepot", "hatchery"]
		for enemy_building in self.known_enemy_structures:
			pos = enemy_building.position
			if enemy_building.name.lower() not in main_base_names:
				cv2.circle(game_data, (int(pos[0]), int(pos[1])), 5, (200, 50, 212), -1)
		for enemy_building in self.known_enemy_structures:
			pos = enemy_building.position
			if enemy_building.name.lower() in main_base_names:
				cv2.circle(game_data, (int(pos[0]), int(pos[1])), 15, (0, 0, 255), -1)

		for enemy_unit in self.known_enemy_units:
			if not enemy_unit.is_structure:
				worker_names = ["probe","scv","drone"]
				pos = enemy_unit.position
				if enemy_unit.name.lower() in worker_names:
					cv2.circle(game_data, (int(pos[0]), int(pos[1])), 1, (55, 0, 155), -1)
				else:
					cv2.circle(game_data, (int(pos[0]), int(pos[1])), 3, (50, 0, 215), -1)
		line_max = 50
		mineral_ratio = self.minerals / 1500
		if mineral_ratio > 1.0:
			mineral_ratio = 1.0
		vespene_ratio = self.vespene / 1500
		
		if vespene_ratio > 1.0:
			vespene_ratio = 1.0

		population_ratio = self.supply_left / self.supply_cap
		if population_ratio > 1.0:
			population_ratio = 1.0

		plausible_supply = self.supply_cap / 200.0

		military_weight = len(self.units(MARINE)) / (self.supply_cap-self.supply_left)
		if military_weight > 1.0:
			military_weight = 1.0
		cv2.line(game_data, (0, 19), (int(line_max*military_weight), 19), (250, 250, 200), 3)  # worker/supply ratio
		cv2.line(game_data, (0, 15), (int(line_max*plausible_supply), 15), (220, 200, 200), 3)  # plausible supply (supply/200.0)
		cv2.line(game_data, (0, 11), (int(line_max*population_ratio), 11), (150, 150, 150), 3)  # population ratio (supply_left/supply)
		cv2.line(game_data, (0, 7), (int(line_max*vespene_ratio), 7), (210, 200, 0), 3)  # gas / 1500
		cv2.line(game_data, (0, 3), (int(line_max*mineral_ratio), 3), (0, 255, 25), 3)  # minerals minerals/1500

		self.flipped = cv2.flip(game_data, 0)
		resized = cv2.resize(self.flipped, dsize=None, fx=2, fy=2)
		cv2.imshow('Intel', resized)
		cv2.waitKey(1)
		# for cc in self.units(COMMANDCENTER):
		# 	cc_pos = cc.position
		# 	cv2.circle(game_data, (int(cc_pos[0]), int(cc_pos[1])), 10, (0, 255, 0), -1)
		# flipped = cv2.flip(game_data, 0)
		# resized = cv2.resize(flipped, dsize=None, fx=2, fy=2)
		# cv2.imshow('Intel', resized)
		# cv2.waitKey(1)

	async def build_workers(self):
		if len(self.units(COMMANDCENTER))*20 > len(self.units(SCV)):
			if len(self.units(SCV)) < self.MW:
				for cc in self.units(COMMANDCENTER).ready.noqueue:
					if self.can_afford(SCV):
						await self.do(cc.train(SCV))
	async def build_supplydepot(self):
		if self.supply_left < 7 and not self.already_pending(SUPPLYDEPOT):
		# if self.supply_left < 7:
			ccs = self.units(COMMANDCENTER).ready
			
			if ccs.exists:
				# print(ccs.position)
				# print(ccs.position)
				# print(ccs.position)
				# print(ccs.position)
				if self.can_afford(SUPPLYDEPOT):
					await self.build(SUPPLYDEPOT, near=ccs.first)
	async def build_refinery(self):
		for cc in self.units(COMMANDCENTER).ready:
			vespenes = self.state.vespene_geyser.closer_than(15.0, cc)
			for vespene in vespenes:
				if not self.can_afford(REFINERY):
					break
				work = self.select_build_worker(vespene.position)
				if work is None:
					break
				if not self.units(REFINERY).closer_than(1.0, vespene).exists:
					await self.do(work.build(REFINERY, vespene))
	async def expand(self):
		if self.units(COMMANDCENTER).amount < 3 and self.can_afford(COMMANDCENTER):
			await self.expand_now()

	async def offensive_force_buildings(self):
		for cc in self.units(COMMANDCENTER):
			# print(cc)
			ccs = self.units(COMMANDCENTER).amount
			racks = self.units(BARRACKS).amount
			fact = self.units(FACTORY).amount
			# if racks.first.exists:
			# 	await 
			if racks < ((self.iteration/ self.IPM)/2):
				await self.build(BARRACKS, near = cc.position)

	async def build_offensive_forces(self):
		ratio = (self.units(MARINE).amount+1)/(self.units(COMMANDCENTER).amount+1)
		print(ratio)
		current_amount = self.units(MARINE).amount
		max_units = 120
		if ratio <= 20 and current_amount < max_units:
			for br in self.units(BARRACKS).ready.noqueue:
				if self.can_afford(MARINE) and self.supply_left > 0:
					await self.do(br.train(MARINE))
		

	# def find_target(self, state):
	# 	if len(self.known_enemy_units) > 0:
	# 		return random.choice(self.known_enemy_units)
	# 	elif len(self.known_enemy_structures) > 0:
	# 		return random.choice(self.known_enemy_structures)
	# 	else: 
	# 		self.enemy_start_locations[0]

	async def attack(self):
	       if len(self.units(MARINE).idle) > 0:
	           choice = random.randrange(0, 4)
	           target = False
	           if self.iteration > self.do_something_after:
	               if choice == 0:
	                   # no attack
	                   wait = random.randrange(20, 165)
	                   self.do_something_after = self.iteration + wait

	               elif choice == 1:
	                   #attack_unit_closest_nexus
	                   if len(self.known_enemy_units) > 0:
	                       target = self.known_enemy_units.closest_to(random.choice(self.units(COMMANDCENTER)))

	               elif choice == 2:
	                   #attack enemy structures
	                   if len(self.known_enemy_structures) > 0:
	                       target = random.choice(self.known_enemy_structures)

	               elif choice == 3:
	                   #attack_enemy_start
	                   target = self.enemy_start_locations[0]

	               if target:
	                   for vr in self.units(MARINE).idle:
	                       await self.do(vr.attack(target))
	               y = np.zeros(4)
	               y[choice] = 1
	               print(y)
	               self.train_data.append([y,self.flipped])
	# async def attack(self):
	# 	#{UNIT: [n to fight, n to defend]}
	# 	aggressive_units = { 'm':  [50,50]}
	# 	# print(aggressive_units['m'])
			

	# 	if self.units(MARINE).amount >= aggressive_units['m'][0]:
	# 		for s in self.units(MARINE).idle:
	# 				await self.do(s.attack(self.enemy_start_locations[0]))

	# 	if self.units(MARINE).amount > aggressive_units['m'][1]:
	# 		if len(self.known_enemy_units) > 0:
	# 			for m in self.units(MARINE).idle:
	# 				await self.do(m.attack(random.choice(self.known_enemy_units)))
recur()