from baseballator import *


def create_tournament(teams, kind, preset=None, rounds=None, series_lenght=7, names=None, alternate=True, part_names = ['AL', 'NL'], rounds_names=None, part_priority=0):
	if kind in ('knockout', 'playoff', 'elimination'):
		if rounds == None:
			rounds = int(log2(len(teams[0]))) + 1
		return Tournament_Knockout(teams, rounds, series_lenght, names, alternate, part_names, rounds_names, part_priority)
	if kind in ('round', 'round-robin'):
		return Tournament_Round(teams)

def add_pitchers(teams):
	new_teams = []
	for team in teams:
		new_teams.append([team, 1])
	return new_teams


def match_maker(field, match_type='series', name = '', series_lenght=7, alternate=True):
	matchups = []
	for i in range(len(field)//2):
		high_seed = i
		low_seed = -(i+1)
		if match_type == 'series':
			series_name = name + ': ' + field[high_seed][0].team_id + '-' + field[low_seed][0].team_id
			match = Series(series_name, field[high_seed][0], field[low_seed][0],
			 higher_pitcher=field[high_seed][1], lower_pitcher=field[low_seed][1],
			 alternate=alternate, games=series_lenght)
		if match_type == 'game':
			#add game
			pass
		matchups.append(match)
	return matchups


class Tournament_Knockout():
	
	def __init__(self, teams, rounds, series_lenght, names, alternate, part_names, rounds_names, part_priority):
		self.teams = teams
		self.rounds = rounds
		self.names = names
		if  not hasattr(series_lenght, '__iter__'):
			self.series_lenght = [series_lenght] * self.rounds
		else:
			self.series_lenght = series_lenght
		left_part = [self.teams[0], part_names[0]]
		right_part = [self.teams[1], part_names[1]]
		self.games_db = []
		self.series_list = {}
		finalists = []

		for part, name in [left_part, right_part]:
			for i in range(self.rounds - 1):
				winners = []
				part = add_pitchers(part)
				if rounds_names != None:
					round_name = name + rounds_names[i]
				else:
					round_name = name + str(i + 1)
				matchups = match_maker(part, name=round_name, alternate=alternate, series_lenght=series_lenght)
				for match in matchups:
					match.play()
					self.games_db.append(match.games_dataset())
					self.series_list[match.title] = match.description
					winners.append(match.winner)
					part = winners
			finalists.append(winners[0])
		self.final = Series(rounds_names[-1], finalists[part_priority], finalists[(part_priority - 1) ** 2])
		self.final.play()
		self.games_db.append(self.final.games_dataset())
		self.series_list[self.final.title] = self.final.description

	def games_dataset(self):
		return pd.concat(self.games_db)
	def series_dataset(self):
		return pd.DataFrame.from_dict(self.series_list, orient='index')
