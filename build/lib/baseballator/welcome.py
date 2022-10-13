import baseballator as bs

def quick_game(matchup_string):
	home_team, away_team = bs.string_to_teams(matchup_string)
	teams = bs.data.load_current()
	game = bs.Game(teams[home_team], teams[away_team], 1, 1)
	game.play()
	print(game.box_pbp())