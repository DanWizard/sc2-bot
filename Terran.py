import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import COMMANDCENTER, BARRACKS, SUPPLYDEPOT, SCV, REFINERY, MARINE, FACTORY, HELLION
from sc2.position import Point2, Point3, Pointlike
import random

class Hestia(sc2.BotAI):

	def __init__(self):
		self.IPM = 165
		self.MW = 65

	async def on_step(self, iteration):
		self.iteration = iteration
		await self.distribute_workers()
		await self.build_workers()
		await self.build_supplydepot()
		await self.build_refinery()
		await self.expand()
		await self.offensive_force_buildings()
		await self.build_offensive_forces()
		await self.attack()
		depot_placement_positions = self.main_base_ramp.corner_depots
		# print(depot_placement_positions)
		# print(placement_grid)
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
		if self.units(COMMANDCENTER).amount < 4 and self.can_afford(COMMANDCENTER):
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
			if fact < ((self.iteration/ self.IPM)/2):
				await self.build(FACTORY, near = cc.position)

	async def build_offensive_forces(self):
		ratio = (self.units(MARINE).amount+1)/(self.units(HELLION).amount+1)
		print(ratio)
		current_amount = self.units(MARINE).amount + self.units(HELLION).amount
		max_units = 120
		for br in self.units(BARRACKS).ready.noqueue:
			if ratio <= 3 and current_amount != 120:
				if self.can_afford(MARINE) and self.supply_left > 0:
					await self.do(br.train(MARINE))
		for ft in self.units(FACTORY).ready.noqueue:
			if self.can_afford(HELLION) and self.supply_left > 0:
				await self.do(ft.train(HELLION))

	# def find_target(self, state):
	# 	if len(self.known_enemy_units) > 0:
	# 		return random.choice(self.known_enemy_units)
	# 	elif len(self.known_enemy_structures) > 0:
	# 		return random.choice(self.known_enemy_structures)
	# 	else: 
	# 		self.enemy_start_locations[0]

	async def attack(self):
		#{UNIT: [n to fight, n to defend]}
		aggressive_units = { 'm':  [50,5],
							 'hn': [15,3]}
		# print(aggressive_units['m'])
		
		total = self.units(MARINE).amount + self.units(HELLION).amount	

		if self.units(MARINE).amount >= aggressive_units['m'][0] and self.units(HELLION).amount >=aggressive_units['hn'][0]:
			for s in self.units(MARINE).idle:
				# if self.units(MARINE).amount == aggressive_units['MARINE'][0] and self.unitsHELLION).amount == aggressive_units['HELLION'][0]: 
					await self.do(s.attack(self.enemy_start_locations[0]))
			for m in self.units(HELLION).idle:
				# if self.units(MARINE).amount == aggressive_units['MARINE'][0] and self.unitsHELLION).amount == aggressive_units['HELLION'][0]: 
					await self.do(m.attack(self.enemy_start_locations[0]))

		if self.units(HELLION).amount > aggressive_units['hn'][1] and self.units(MARINE).amount >aggressive_units['m'][1]:
			if len(self.known_enemy_units) > 0:
				for s in self.units(HELLION).idle:
					await self.do(s.attack(random.choice(self.known_enemy_units)))
			if len(self.known_enemy_units) > 0:
				for m in self.units(MARINE).idle:
					await self.do(m.attack(random.choice(self.known_enemy_units)))
run_game(maps.get("CyberForestLE"), [
	Bot(Race.Terran, Hestia()),
	Computer(Race.Zerg, Difficulty.Hard)],
	realtime = False)