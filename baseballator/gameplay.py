from numpy.random import random, randint
from numpy import log2
from tabulate import tabulate
from baseballator.utils import * 

class Team():
	'''
	A class used to represent a team

	Attributes
	----------
	team_id : str
		id of a team (three letters)

	name : str
		full name of a team

	lineup : dict
		team's batting order with Hitter objects

	rotation : list
		team's pitching rotation with Pitcher objects

	bullpen : tuple
		list with relief pitchers and a list of bullpen pitchers' stats

	babip : float
		batting average on balls in play (represents the level of defence)
	'''

	def __init__(self, team_id, name, lineup, rotation, bullpen_stats, bullpen_names, babip):
		'''
		Parameters
		----------
		team_id : str
			id of a team (three letters)

		name : str
			full name of a team

		lineup : dict
			team's batting order with Hitter objects

		rotation : list
			team's pitching rotation with Pitcher objects

		bullpen_stats : list
			list with stats of a bullpen

		bullpen_names : list
			list with relief pitchers' names

		babip : float
			batting average on balls in play (represents the level of defence)
		'''
		self.team_id = team_id
		self.name = name
		self.lineup = lineup
		self.rotation = rotation
		self.bullpen = (bullpen_names, bullpen_stats)
		self.babip = babip

	def __str__ (self):
		return 'Team({})'.format(self.name)
	def __repr__(self):
		return 'Team({})'.format(self.name)



class Stats:
	def __init__(self):
		pass

	def update(self, game_stats):
		current_stats = self.__dict__
		new_stats = game_stats.__dict__

		for idx in current_stats:
			current_stats[idx] += new_stats[idx]

	def show(self):
		return self.__dict__


class Stats_Hitter(Stats):
	def __init__(self):
		self.PA = 0
		self.K = 0
		self.BB = 0
		self.H1 = 0 
		self.H2 = 0 
		self.H3 = 0 
		self.HR = 0
		self.RBI = 0
		self.SF = 0
		self.R = 0 

	@property
	def AB(self):
		return self.PA - self.BB - self.SF
	@property
	def TB(self):
		return self.H1 + 2 * self.H2 + 3 * self.H3 + 4 * self.HR
	@property
	def H(self):
		return (self.H1 + self.H2 + self.H3 + self.HR)
	@property
	def AVG(self):
		return (self.H)/(self.PA - self.BB)
	@property
	def OBP(self):
		return (self.H + self.BB)/self.PA
	@property
	def SLG(self):
		return (self.TB)/(self.PA - self.BB)
	@property
	def OPS(self):
		return self.OBP + self.SLG
	@property
	def slash_line(self):
		return '{:.3f}/{:.3f}/{:.3f}'.format(self.AVG, self.OBP, self.SLG)
		


class Stats_Pitcher(Stats):
	def __init__(self):
		self.TP = 0
		self.IP = 0
		self.ER = 0
		self.WH = 0
		self.BB = 0
		self.K = 0

	@property
	def ERA(self):
		if self.IP > 0:
			return self.ER/self.IP * 9
		return 0

	@property
	def WHIP(self):
		if self.IP > 0:
			return self.WH/self.IP
		return 0

	@property
	def IP_display(self):
			whole = int(self.IP // 1)
			decimal = self.IP - whole
			if decimal == 0:
				decimal_disp = '0'
			elif decimal < 0.35:
				decimal_disp = '1'
			elif decimal < 0.7:
				decimal_disp = '2'
			else:
				decimal_disp = '0'
				whole += 1

			return (str(whole)+ '.' + decimal_disp)


class Player:

	def __init__(self, player_id, name, position, team, k_rate, bb_rate, contact):
		self.player_id = player_id
		self.name = name
		self.position = position
		self.team = team
		self.k_rate = k_rate
		self.bb_rate = bb_rate
		self.k_odds = rate_to_odd(k_rate)
		self.bb_odds = rate_to_odd(bb_rate)
		self.contact = contact

	def __str__ (self):
		return 'Player({}-{}: K%:{}, BB%:{}, Brl%:{})'.format(self.name, self.position,
		 round(self.k_rate * 100, 1), round(self.bb_rate * 100, 1), round(self.contact[0] * 100, 1))
	def __repr__(self):
		return 'Player({})'.format(self.name)


class Hitter(Player):

	def __init__(self, player_id, name, position, team, k_rate, bb_rate, contact, speed):
		super().__init__(player_id, name, position, team, k_rate, bb_rate, contact)
		self.speed = speed
		self.stats = Stats_Hitter()
		self.career_stats = Stats_Hitter()


class Pitcher(Player):

	league_babip = .297

	def __init__(self, player_id, name, position, team, k_rate, bb_rate, contact, babip, pitch_count):
		super().__init__(player_id, name, position, team, k_rate, bb_rate, contact)
		#self.babip = teams[self.team].babip - self.league_babip
		#self.babip = self.team.babip - self.league_babip
		self.babip = babip - self.league_babip
		self.stats = Stats_Pitcher()
		self.career_stats = Stats_Pitcher()
		self.pitch_count = pitch_count



class AB:

	k_odds_league = rate_to_odd(.223)
	bb_odds_league = rate_to_odd(.080)
	contact_mix = [.069, .058, .248, .249, .337, .039]
	contact_params = {
	0: [.554, .511, .888, .110, 'FO', 'Barell'],
	1: [.103, .417, .739, .091, 'FO', 'Solid'],
	2: [.0002, .654, .175, .077, 'GO', 'Flare/Burner'],
	3: [.010, .058, .561, .113, 'PO', 'Poorly/Under'],
	4: [.000, .181, .087, .056, 'GO', 'Poorly/Topped'],
	5: [.000, .168, .045, .017, 'GO', 'Poorly/Weak']
	} #HR, BABIP, XBH, triple, out-type, name


	def __init__(self, pitcher, hitter):
		self.pitcher = pitcher
		self.hitter = hitter

		self.k_prob = odd_to_rate((self.pitcher.k_odds * self.hitter.k_odds)/AB.k_odds_league)
		self.bb_prob = odd_to_rate((self.pitcher.bb_odds * self.hitter.bb_odds)/AB.bb_odds_league)
		self.contact_probs = AB.contact_mix_transform(self.pitcher.contact, self.hitter.contact, self.contact_mix)

		self.outcome = None
		self.out = False
		self.contact_type = None

	def play(self):

		self.random_vals = random(6)
		if self.random_vals[0] <= self.k_prob:
			self.outcome = 'K'
			self.out = True
		elif self.random_vals[0] <= self.k_prob + self.bb_prob:
			self.outcome = 'BB'
		else:
			#contact made
			self.contact_type = AB.contact_result(self.random_vals[1], self.contact_probs)
			if self.random_vals[2] <= self.contact_params[self.contact_type][0]:
				self.outcome = 'HR'
			elif self.random_vals[3] > self.contact_params[self.contact_type][1] + self.pitcher.babip:
				self.outcome = self.contact_params[self.contact_type][4]
				self.out = True
			elif self.random_vals[4] <= self.contact_params[self.contact_type][2]:
				if self.random_vals[5] <= self.contact_params[self.contact_type][3]:
					self.outcome = '3B'
				else:
					self.outcome = '2B'
			else:
				self.outcome = '1B'

	@staticmethod
	def contact_result(random_val, probs):
		probs = [0] + probs
		for i in range(6):
			if probs[i] <= random_val < sum(probs[:i+2]):
				return i
		return i

	@staticmethod
	def contact_mix_transform(c_pitcher, c_hitter, c_league):
		barell_diff = c_pitcher[0] - c_league[0]
		poor_diff = sum(c_pitcher[3:6]) - sum(c_league[3:6])
		result = list(c_hitter)
		result[0] += 1/2 * barell_diff
		result[1] -= 1/4 * barell_diff
		result[2] -= 1/4 * barell_diff
		result[3] += 1/6 * poor_diff
		result[4] += 1/6 * poor_diff
		result[5] += 1/6 * poor_diff
		result[2] -= 1/3 * poor_diff
		return result


class Score:
	def __init__(self):
		self.runs = 0
		self.hits = 0



class Inning:	

	def __init__(self, pitcher, lineup, number, game_info, is_bullpen = False, replacement = None, is_extra = False, printout = True):
		self.pitcher = pitcher
		self.lineup = lineup
		self.number = number
		self.g_score, self.pitchers_num = game_info
		self.is_bullpen = is_bullpen
		self.replacement = replacement
		self.is_extra = is_extra
		self.printout = printout
		self.description = ''



		self.outs = 0
		self.score = Score()



		if self.is_extra:
			if self.number == 1:
				self.base_runners = [(2, self.lineup[9])]
			else:
				self.base_runners = [(2, self.lineup[self.number - 1])]
		else:
			self.base_runners = []

	def play(self):

		#params

		GIDP = 0.317
		round_bases = .413
		from_scoring = .591

		if (self.is_bullpen) and (self.pitcher.stats.IP > 0):
			k_rate, bb_rate, contact, babip = self.replacement[1]
			if self.pitchers_num <= len(self.replacement[0]):
				new_name = self.replacement[0][self.pitchers_num - 1]
			else:
				new_name = 'Bullpen Pitcher ' + str(self.pitchers_num)
			self.description += '{} replaces {} | '.format(new_name, self.pitcher.name).upper()

			if self.printout:
				print('{} replaces {} | '.format(new_name, self.pitcher.name).upper(), end='')

			self.pitcher = Pitcher('R', new_name, 'RP', self.pitcher.team, k_rate, bb_rate, contact, babip, 200)

		while self.outs < 3:
			self.hitter = self.lineup[self.number]
			self.ab = AB(self.pitcher, self.hitter)
			self.ab.play()

			if self.ab.contact_type != None:
				contact_name = self.ab.contact_params[self.ab.contact_type][-1]
			else:
				contact_name = None

			self.hitter.stats.PA += 1

			#possible outcomes = ['K', 'BB', 'HR', '1B', '2B', '3B', 'GO', 'FO', 'PO']
			if self.ab.outcome == 'K':

				description = self.hitter.name + ' strikes out. '

				self.outs += 1

				self.hitter.stats.K += 1
				self.pitcher.stats.K += 1
				self.pitcher.stats.IP += 1/3

			if self.ab.outcome == 'BB':

				description = self.hitter.name + ' walks. '

				self.pitcher.stats.WH += 1
				self.pitcher.stats.BB += 1
				self.hitter.stats.BB += 1

				new_base_runners = []
				occupied = [base[0] for base in self.base_runners]

				for runner in self.base_runners:
					move = False
					if (runner[0] - 1 in occupied) or (runner[0] == 1):
						new_base = runner[0] + 1

						if new_base == 4:
							self.score.runs += 1

							runner[1].stats.R += 1
							self.pitcher.stats.ER += 1
							self.hitter.stats.RBI += 1

							description += runner[1].name + ' scores. '
						else:
							new_base_runners.append((new_base, runner[1]))
							description += runner[1].name + ' to ' + str(new_base) + '. '
					else:
						new_base_runners.append(runner)				

				new_base_runners.append((1, self.hitter))
				self.base_runners = new_base_runners

				
			if self.ab.outcome == 'HR':

				description = self.hitter.name + ' homers. '

				self.score.runs += 1 + len(self.base_runners)
				self.score.hits += 1
				self.hitter.stats.R += 1
				self.hitter.stats.HR += 1
				self.hitter.stats.RBI += 1 + len(self.base_runners)

				self.pitcher.stats.ER += 1 + len(self.base_runners)
				self.pitcher.stats.WH += 1

				for runner in self.base_runners:
					runner[1].stats.R += 1
					description += runner[1].name + ' scores. '

				self.base_runners = []

			if self.ab.outcome == '3B':

				description = self.hitter.name + ' triples. '

				self.score.runs += len(self.base_runners)
				self.score.hits += 1

				self.hitter.stats.H3 += 1
				self.hitter.stats.RBI += len(self.base_runners)

				self.pitcher.stats.WH += 1
				self.pitcher.stats.ER += len(self.base_runners)


				for runner in self.base_runners:
					runner[1].stats.R += 1
					description += runner[1].name + ' scores. '
				self.base_runners = [(3, self.hitter)]

			if self.ab.outcome == '2B':

				description = self.hitter.name + ' doubles. '

				self.score.hits += 1

				self.hitter.stats.H2 += 1

				self.pitcher.stats.WH += 1
				new_base_runners = []

				for runner in self.base_runners:
					if (runner[0] > 1) or ((runner[0] == 1) and (random() <= round_bases * runner[1].speed)):
						self.score.runs += 1

						runner[1].stats.R += 1
						self.pitcher.stats.ER += 1
						self.hitter.stats.RBI += 1
						description += runner[1].name + ' scores. '
					else:
						new_base_runners.append((3, runner[1]))
						description += runner[1].name + ' to 3. '

				new_base_runners.append((2, self.hitter))
				self.base_runners = new_base_runners

			if self.ab.outcome == '1B':

				description = self.hitter.name + ' singles. '

				self.score.hits += 1

				self.hitter.stats.H1 += 1

				self.pitcher.stats.WH += 1

				new_base_runners = []
				advance = False
				occupied = [base[0] for base in self.base_runners]

				for runner in self.base_runners:
					if (runner[0] > 2):
						self.score.runs += 1

						runner[1].stats.R += 1
						self.pitcher.stats.ER += 1
						self.hitter.stats.RBI += 1
						description += runner[1].name + ' scores. '

					else:
						if 2 in occupied:

							if (runner[0] == 2) and (random() <= from_scoring * runner[1].speed):
								self.score.runs += 1
								advance = True

								runner[1].stats.R += 1
								self.pitcher.stats.ER += 1
								self.hitter.stats.RBI += 1
								description += runner[1].name + ' scores. '
							elif runner[0] == 2:
								new_base_runners.append((3, runner[1]))
								description += runner[1].name + ' to 3. '
							
							if (runner[0] == 1) and (advance):
								new_base_runners.append((3, runner[1]))
								description += runner[1].name + ' to 3. '
							elif runner[0] == 1:
								new_base_runners.append((2, runner[1]))
								description += runner[1].name + ' to 2. '
						else:
							if (runner[0] == 1) and (random() <= round_bases * runner[1].speed):
								new_base_runners.append((3, runner[1]))
								description += runner[1].name + ' to 3. '
							elif runner[0] == 1:
								new_base_runners.append((2, runner[1]))
								description += runner[1].name + ' to 2. '

				new_base_runners.append((1, self.hitter))
				self.base_runners = new_base_runners

			if self.ab.outcome == 'FO': 
				self.outs += 1
				occupied = [base[0] for base in self.base_runners]
				if (3 in occupied) and (self.outs < 3):
					self.score.runs += 1

					self.base_runners[0][1].stats.R += 1
					self.pitcher.stats.ER += 1
					self.hitter.stats.SF += 1
					self.hitter.stats.RBI += 1

					description = self.hitter.name + ' out on sac fly. ' + self.base_runners[0][1].name + ' scores. '
					self.base_runners = self.base_runners[1:]
				else:
					description = self.hitter.name + ' flies out. '

				self.pitcher.stats.IP += 1/3


			if self.ab.outcome == 'GO':
				self.outs += 1
				self.pitcher.stats.IP += 1/3
				occupied = [base[0] for base in self.base_runners]
				hitter_on_first = False
				new_base_runners = []

				if 1 in occupied:
					if (random() < GIDP - self.pitcher.babip) and (self.outs < 3):
						self.outs += 1
						self.pitcher.stats.IP += 1/3
						description = self.hitter.name + ' grounds into a double play. ' + self.base_runners[-1][1].name + ' out at 2. ' + self.hitter.name + ' out at 1.'
						self.base_runners = self.base_runners[:-1]

					else:
						hitter_on_first = True
						description = self.hitter.name + ' grounds into a force out. ' + self.base_runners[-1][1].name + ' out at 2. ' + self.hitter.name + ' to 1.'
						self.base_runners = self.base_runners[:-1]
				else:
					description = self.hitter.name + ' grounds out. '

				if self.outs < 3:
					for runner in self.base_runners:
						if runner[0] == 2:
							new_base_runners.append((3, runner[1]))
							description += runner[1].name + ' to 3. '
						if runner[0] == 3:
							self.score.runs += 1

							runner[1].stats.R += 1
							self.pitcher.stats.ER += 1
							self.hitter.stats.RBI += 1
							description += runner[1].name + ' scores. '

					if hitter_on_first:
						new_base_runners.append((1, self.hitter))

					self.base_runners = new_base_runners


			if self.ab.outcome == 'PO':
				description = self.hitter.name + ' pops out. '
				self.outs += 1

				self.pitcher.stats.IP += 1/3

			if self.number == 9:
				self.number = 1
			else:
				self.number += 1

			if self.printout:
				print(description, end='| ')
				


		
			#pitch count
			if self.ab.outcome == 'BB':
				pitches = int(5.5 + (-1) ** randint(1,3)/2)
			elif self.ab.outcome == 'K':
				pitches = int(4.5 + (-1) ** randint(1,3)/2)
			else:
				pitches = 3 + (-1) ** randint(1,4)

			hitter_skill_detect = lambda x, y: 1 if 2.5 * x < y else -1
			self.pitcher.stats.TP += pitches + hitter_skill_detect(self.hitter.contact[0], self.hitter.contact[2])

			if not self.is_bullpen:
				if ((self.pitcher.stats.TP >= self.pitcher.pitch_count) and (self.g_score.hits > 2)) or (self.score.runs > 5):
					self.is_bullpen = True
					k_rate, bb_rate, contact, babip = self.replacement[1]
					new_name = self.replacement[0][0]
					description += '| {} replaces {} '.format(new_name, self.pitcher.name).upper()

					if self.printout:
						print('{} replaces {} | '.format(new_name, self.pitcher.name).upper(), end='')

					self.pitcher = Pitcher('R', self.replacement[0][0], 'RP', self.pitcher.team, k_rate, bb_rate, contact, babip, 200)

					


			self.description += description + '| '


		if self.printout:
			print()
			print(self.score.runs, ' R, ', self.score.hits, ' H', sep='')

		self.description += '\n' + str(self.score.runs) + ' R, ' + str(self.score.hits) + ' H'

class Game:

	def __init__(self, home, away, home_pitcher, away_pitcher):
		self.home = home
		self.away = away
		self.home_pitcher = home.rotation[home_pitcher - 1]
		self.away_pitcher = away.rotation[away_pitcher - 1]
		self.home_pitchers = [self.home_pitcher]
		self.away_pitchers = [self.away_pitcher]
		self.home_bp = False
		self.away_bp = False

		self.home_number = 1
		self.away_number = 1

		self.home_score = Score()
		self.away_score = Score()
		self.desc = ''
		self.home_innings = []
		self.away_innings = []

	def play(self, printout = False):
		self.printout = printout

		for i in range(9):

			title = '\nInning ' + str(i + 1) + '\n'
			self.desc += title + '\n'
			if self.printout:
				print(title)

			away_inn = Inning(self.home_pitcher, self.away.lineup, self.away_number, (self.away_score, len(self.home_pitchers)),
			 printout = self.printout, replacement=self.home.bullpen, is_bullpen=self.home_bp)
			away_inn.play()
			self.away_number = away_inn.number
			self.away_innings.append(away_inn)
			self.desc += away_inn.description + '\n'
			self.away_score.runs += away_inn.score.runs
			self.away_score.hits += away_inn.score.hits

			if away_inn.is_bullpen:
				if away_inn.pitcher not in self.home_pitchers:
					self.home_pitchers.append(away_inn.pitcher)
				self.home_pitcher = away_inn.pitcher
				self.home_bp = True

			home_inn = Inning(self.away_pitcher, self.home.lineup, self.home_number, (self.home_score, len(self.away_pitchers)),
				printout = self.printout, replacement=self.away.bullpen, is_bullpen=self.away_bp)
			home_inn.play()
			self.home_number = home_inn.number
			self.home_innings.append(home_inn)
			self.desc += home_inn.description + '\n'
			self.home_score.runs += home_inn.score.runs
			self.home_score.hits += home_inn.score.hits

			if home_inn.is_bullpen:
				if home_inn.pitcher not in self.away_pitchers:
					self.away_pitchers.append(home_inn.pitcher)
				self.away_pitcher = home_inn.pitcher
				self.away_bp = True

			inter_score = self.away.team_id + ' ' + str(self.away_score.runs) + ', ' + self.home.team_id + ' ' + str(self.home_score.runs)
			self.desc += inter_score + '\n'
			if printout:
				print(inter_score)

		while self.home_score.runs == self.away_score.runs:

			title = '\nInning ' + str(i + 1) + '\n'
			self.desc += title + '\n'
			if self.printout:
				print(title)

			away_inn = Inning(self.home_pitcher, self.away.lineup, self.away_number, (self.away_score, len(self.home_pitchers)),
			 printout = self.printout, replacement=self.home.bullpen, is_bullpen=self.home_bp, is_extra=True)
			away_inn.play()
			self.away_number = away_inn.number
			self.away_innings.append(away_inn)
			self.desc += away_inn.description + '\n'
			self.away_score.runs += away_inn.score.runs
			self.away_score.hits += away_inn.score.hits

			if away_inn.is_bullpen:
				self.home_pitchers.append(away_inn.pitcher)
				self.home_pitcher = away_inn.pitcher
				self.home_bp = True

			home_inn = Inning(self.away_pitcher, self.home.lineup, self.home_number, (self.home_score, len(self.away_pitchers)),
				printout = self.printout, replacement=self.away.bullpen, is_bullpen=self.away_bp, is_extra=True)
			home_inn.play()
			self.home_number = home_inn.number
			self.home_innings.append(home_inn)
			self.desc += home_inn.description + '\n'
			self.home_score.runs += home_inn.score.runs
			self.home_score.hits += home_inn.score.hits

			if home_inn.is_bullpen:
				self.away_pitchers.append(home_inn.pitcher)
				self.away_pitcher = home_inn.pitcher
				self.away_bp = True

			inter_score = self.away.team_id + ' ' + str(self.away_score.runs) + ', ' + self.home.team_id + ' ' + str(self.home_score.runs)
			self.desc += inter_score + '\n'
			if printout:
				print(inter_score)


		if self.home_score.runs > self.away_score.runs:
			self.result = 1
		else:
			self.result = 0


		#setting stats
		self.game_stats = {}
		for key in [self.home, self.away]:
			self.game_stats[key.name] = {}
			for idx in key.lineup:
				player = key.lineup[idx]
				self.game_stats[key.name][player] = Stats_Hitter()
				self.game_stats[key.name][player].update(player.stats)
				player.career_stats.update(player.stats)
				player.stats = Stats_Hitter()

		home_starter_stats = Stats_Pitcher()
		home_starter_stats.update(self.home_pitchers[0].stats)
		self.home_pitchers[0].career_stats.update(self.home_pitchers[0].stats)
		self.home_pitchers[0].stats = Stats_Pitcher()
		away_starter_stats = Stats_Pitcher()
		away_starter_stats.update(self.away_pitchers[0].stats)
		self.away_pitchers[0].career_stats.update(self.away_pitchers[0].stats)
		self.away_pitchers[0].stats = Stats_Pitcher()
		self.starters_stats = {self.home.name: (self.home_pitchers[0].name, home_starter_stats),
		 self.away.name: (self.away_pitchers[0].name, away_starter_stats)}


	def score_line(self):

		inning_numbers = ['Team', '|'] + list(range(1, len(self.home_innings) + 1)) + ['|', 'R', 'H']

		away_data = [self.away.name, '|'] + [inn.score.runs for inn in self.away_innings] + ['|'] + [self.away_score.runs, self.away_score.hits]
		home_data = [self.home.name, '|'] + [inn.score.runs for inn in self.home_innings] + ['|'] + [self.home_score.runs, self.home_score.hits]
		data = [away_data, home_data]

		return tabulate(data, headers=inning_numbers)

	def box(self, team, side='A'):

		self.side = side

		if team == 'home':
			self.team = self.home
			pitchers = self.home_pitchers
		else:
			self.team = self.away
			pitchers = self.away_pitchers

		team_stats = self.game_stats[self.team.name]
		starter_stats = self.starters_stats[self.team.name]

		text = ''
		if self.side != 'P':
			text += 'BATTING \n'

			headers = [self.team.name, 'H-AB', 'R', 'RBI', '2B', '3B', 'HR', 'TB', 'BB', 'SO']
			data = []
			in_game_stats = {}

			for idx in self.team.lineup:
				player = self.team.lineup[idx]
				player_stats = team_stats[player]

				stat_line = [
				player.name + ', ' + player.position,
				'{}-{}'.format(player_stats.H, player_stats.AB),
				player_stats.R,
				player_stats.RBI,
				player_stats.H2,
				player_stats.H3,
				player_stats.HR,
				player_stats.TB,
				player_stats.BB,
				player_stats.K]
				data.append(stat_line)



			text += tabulate(data, headers=headers)

			text += '\n\n'

		if self.side != 'B':
			text += 'PITCHING\n'

			headers = [self.team.name, 'IP', 'TP', 'R', 'ERA', 'WHIP', 'BB', 'SO']

			data = []
			is_starter = True

			for pitcher in pitchers:
				if is_starter:
					pitcher_stats = starter_stats[1]
					is_starter = False
				else:
					pitcher_stats = pitcher.stats
				line = [
					pitcher.name + ', ' + pitcher.position,
					pitcher_stats.IP_display,
					pitcher_stats.TP,
					pitcher_stats.ER,
					pitcher_stats.ERA,
					pitcher_stats.WHIP,
					pitcher_stats.BB,
					pitcher_stats.K]
				data.append(line)

			text += tabulate(data, headers=headers)

		return text

	def box_pbp(self):
		text = self.away.name + ' @ ' + self.home.name + '\n\n'

		text += 'Starters: ' + self.away_pitchers[0].name + ' vs. ' + self.home_pitchers[0].name

		if self.result == 1:
			text += '\nWinner: ' + self.home.name
		else:
			text += '\nWinner: ' + self.away.name

		text += '\n\n' + self.score_line() + '\n\nSTATISTICS' 
		text += '\n\n' + self.away.name.upper() + '\n\n' + self.box('away')
		text += '\n\n' + self.home.name.upper() + '\n\n' + self.box('home')
		text += '\n\n' + 'PLAY-BY-PLAY' + '\n ' + self.desc

		return text

	def game_line(self):
		if self.result == 1:
			winner = self.home.name
		else:
			winner = self.away.name
		WP = self.starters_stats[winner]
		line_blueprint = ' - {}IP, {}ER, {}Hits, {}BBs, {}Ks'
		stats_for_line = line_blueprint.format(WP[1].IP_display, WP[1].ER, WP[1].WH - WP[1].BB, WP[1].BB, WP[1].K)
		WP_line = WP[0] + stats_for_line
		if self.home_score.hits == 0 or self.away_score.hits == 0:
			ho_hitter = 1
		else:
			no_hitter = 0
		line = [self.away.name, self.home.name, self.away_score.runs, self.home_score.runs, winner, WP_line, no_hitter]
		return line


class Series():

	def __init__(self, title, higher_seed, lower_seed, games=7, alternate=True,
	 higher_pitcher=1, lower_pitcher=1):
		self.title = title
		self.higher_seed = [higher_seed, 0, higher_pitcher]
		self.lower_seed = [lower_seed, 0, lower_pitcher]
		self.games = games
		self.alternate = alternate
		self.pitchers_in_rotation = min((len(higher_seed.rotation), len(lower_seed.rotation)))

		self.outcome = None #[0 - draw, 1 - win for higher, -1 win for lower]

		if games % 2 == 0:
			self.min_games = int(games // 2 + 1)
		else:
			self.min_games = int(games // 2 + 1)

		self.game_list = []
		self.scores = []
		self.lines = []


	def play(self, printout=False):

		game_number = 0
		games_at_home = 0
		home_team = self.higher_seed
		away_team = self.lower_seed

		while ((self.higher_seed[1] < self.min_games) and (self.lower_seed[1] < self.min_games)) and (game_number < self.games):

			game_number += 1

			game = Game(home_team[0], away_team[0], home_team[2], away_team[2])
			game.play()
			self.game_list.append(game)
			self.scores.append(str(game.away_score.runs) + ':' + str(game.home_score.runs))
			self.lines.append([self.title, 'Game ' + str(game_number)] + game.game_line())

			if printout:
				print('-----Game ' + str(game_number) + '-----\n')
				print(game.box_pbp())


			if game.result == 1:
				home_team[1] += 1
			else:
				away_team[1] += 1

			
			if home_team[2] == self.pitchers_in_rotation:
				home_team[2] = 0
			if home_team[2] < self.pitchers_in_rotation:
				home_team[2] += 1

			if away_team[2] == self.pitchers_in_rotation:
				away_team[2] = 0
			if away_team[2] < self.pitchers_in_rotation:
				away_team[2] += 1

			if self.alternate:
				if self.games - game_number <= 3:
					home_team, away_team = away_team, home_team
				else:
					games_at_home += 1
					if games_at_home == 2:
						home_team, away_team = away_team, home_team
						games_at_home = 0

		desc_blueprint = '{} won a series against {} in {} games.'
		self.games_played = len(self.game_list)
		if self.higher_seed[1] > self.lower_seed[1]:
			self.outcome = 1
			self.winner = self.higher_seed[0]
			self.description = desc_blueprint.format(self.higher_seed[0].name, self.lower_seed[0].name, self.games_played)
		elif self.higher_seed[1] < self.lower_seed[1]:
			self.outcome = -1
			self.winner = self.lower_seed[0]
			self.description = desc_blueprint.format(self.lower_seed[0].name, self.higher_seed[0].name, self.games_played)
		else:
			self.outcome = 0
			self.description = 'Series between {} and {} ended in draw.'.format(self.higher_seed[0].name, self.lower_seed[0].name)

	def games_dataset(self):
		return pd.DataFrame(data=self.lines, columns=['series', 'game', 'away_team', 'home_team', 'away_runs', 'home_runs', 'winner', 'WP', 'no_hitter'])

	def get_game(self, number):
		return self.game_list[number - 1]

	def MVP(self):
		all_players = list(self.higher_seed[0].lineup.values()) + list(self.lower_seed[0].lineup.values())
		players_sorted = sorted(all_players, key=lambda x: x.career_stats.OPS, reverse=True)
		return (players_sorted[0].name, players_sorted[0].career_stats.slash_line)


#delete internal
