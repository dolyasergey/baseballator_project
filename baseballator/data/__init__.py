'''Some player databases'''

import os
import pandas as pd
from baseballator import Team, Hitter, Pitcher

_cwd = '/Users/dolyasergey/My Files/Sport Stats/baseball/baseballator_project/baseballator/data/'
_current = 'DATABASE_2022'
print(os.getcwd())

def teams_from_df(folder, rotation_len=5):
	'''Creates a database of Team objects from folder with data

	The folder should contain following files:
	1) team_info.csv - contains team ids, team names, babip (level of defence),
	bullpen stats and relief pitchers
	2) ID_hitters.csv - contains batting order, positions and stats
	3) ID_pitchers.csv - contains rotation and pitchers' stats
	
	Parameters
	----------
	folder : str
		the name of the folder that contains all relevant files 

	rotation_len : int, optional
		number of pitchers in the rotation (default is 5)

	Returns
	-------
	dict
		dict with all the teams. Keys are team ids and values are Team objects
	'''
	path = folder + '/'
	info = pd.read_csv(path + 'team_info.csv', index_col='team_id')
	teams = {}

	for team_id in info.index:
		name = info.loc[team_id]['team_name']
		team = info.loc[team_id]
		babip = info.loc[team_id]['babip']
		
		#create lineup
		lineup = {}
		#get all the player's in table
		lineup_raw = pd.read_csv('{}{}_hitters.csv'.format(path, team_id))
		#create hitter objects
		for i in range(9):
			player = lineup_raw.loc[i]
			player_name = player[' first_name'][1:] + ' ' + player['last_name']
			lineup[i + 1] = Hitter(player['player_id'], player_name, player['POS'], team_id,
			 player['b_k_percent'] / 100, player['b_bb_percent'] / 100, list(player[9:15].values / 100), player['delta_ss'])

		#create pitching rotation
		rotation = []
		#get all data into table
		rotation_raw = pd.read_csv('{}{}_pitchers.csv'.format(path, team_id))
		#create Pitcher objects
		for i in range(rotation_len):
			player = rotation_raw.loc[i]
			player_name = player[' first_name'][1:] + ' ' + player['last_name']
			rotation.append(Pitcher(player['player_id'], player_name, 'SP', team_id,
			 player['p_k_percent'] / 100, player['p_bb_percent'] / 100, list(player[9:15].values / 100), babip, player['TP']))

		#create bullpen stats
		bullpen_stats = [team['k'], team['bb'], list(team.iloc[4:10][::-1].values / 100), babip]
		bullpen_names = team['RP'].split('/')

		#write a Team object in a dict
		teams[team_id] = Team(team_id, name, lineup, rotation, bullpen_stats, bullpen_names, babip)
	return teams

def load_current():
	'''Loads rosters from MLB 2022 season'''
	return teams_from_df(_cwd + _current)

def load_alltime():
	'''Loads rosters from MLB 2022 season'''
	return teams_from_df(_cwd + 'ALLTIME', rotation_len=3)
