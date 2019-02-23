import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import COMMANDCENTER, BARRACKS, SUPPLYDEPOT, SCV, REFINERY, MARINE
import random

class Hestia(sc2.BotAI):
	async def on_step(self, iteration):
		await self.distribute_workers()
		await self.build_workers()
		await self.build_supplydepot()
		await self.build_refinery()
		await self.expand()
		await self.offensive_force_buildings()
		await self.build_offensive_forces()
		await self.attack()

	async def build_workers(self):
		for cc in self.units(COMMANDCENTER).ready.noqueue:
			if self.can_afford(SCV) and self.units(SCV).amount <= 80:
				await self.do(cc.train(SCV))
	async def build_supplydepot(self):
		if self.supply_left < 5 and not self.already_pending(SUPPLYDEPOT):
			ccs = self.units(COMMANDCENTER).ready
			if ccs.exists:
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
			# if racks.first.exists:
			# 	await 
			if ccs != 3 and racks != 6:
				await self.build(BARRACKS, near = cc.position)

	async def build_offensive_forces(self):
		for sd in self.units(BARRACKS).ready.noqueue:
			if self.can_afford(MARINE) and self.supply_left > 0:
				await self.do(sd.train(MARINE))

	# def find_target(self, state):
	# 	if len(self.known_enemy_units) > 0:
	# 		return random.choice(self.known_enemy_units)
	# 	elif len(self.known_enemy_structures) > 0:
	# 		return random.choice(self.known_enemy_structures)
	# 	else: 
	# 		self.enemy_start_locations[0]

	async def attack(self):
		if self.units(MARINE).amount > 50:
			for s in self.units(MARINE).idle:
				await self.do(s.attack(self.enemy_start_locations[0]))

		if self.units(MARINE).amount > 20:
			if len(self.known_enemy_units) > 0:
				for s in self.units(MARINE).idle:
					await self.do(s.attack(random.choice(self.known_enemy_units)))
run_game(maps.get("CyberForestLE"), [
	Bot(Race.Terran, Hestia()),
	Computer(Race.Zerg, Difficulty.Hard)],
	realtime = False)