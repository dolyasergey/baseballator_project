'''Helper functions'''

def rate_to_odd(rate):
	'''Converts probability from rate format into odd format
	
	Parameters
	----------
	rate : float
		the probability of an event in rate format

	Returns
	-------
	float
		the probability of an event in odd format
	'''
	return (rate/(1 - rate))

def odd_to_rate(odd):
	'''Converts probability from odd format into rate format
	
	Parameters
	----------
	odd : float
		the probability of an event in odd format

	Returns
	-------
	float
		the probability of an event in rate format
	'''
	return (odd/(1 + odd))

def transform_stats(pa, hits, double, triple, homer, bb, so, hbp, sac, goao):
	'''Infers probability of different contact types based on statistics

	This function uses Bayes rule to infer contact rates (barell, solid
	contact) from observed statistical results. Knowing the probability
	of hitting for a certain result, probability of a certain contact
	and probability of a certain result after a certain contact (e.g. 
	probability of hitting a home run, probability of hitting a barell 
	and probability of getting home run after hitting a barell) we can 
	infer the probability of a certain result to represent a certain
	contact type (e.g. the probability that a home run was a barell).
	Having done all these calculations the funtion transforms hitter's 
	stats into his contact mix.
	
	Parameters
	----------
	pa : int
		number of plate appearances

	hits : int
		number of base hits

	double : int
		number of doubles

	triple : int
		number of triples

	homer : int
		number of home runs

	bb : int
		number of walks

	so : int
		number of strikeouts

	hbp : int
		number of hit by pitches

	sac : int
		number of sacrifice flyes

	goao : float
		ratio of ground outs to air outs 

	Returns
	-------
	list
		hitter's probability of hitting for a certain contact type:
		barell, solid, flare/burner, poorly/under, poorly/topped, poorly/weak
	'''
	contact_made = pa - so - bb - hbp
	#calculating probabilities of a single, double, triple and a home run
	h1 = (hits - double - triple - homer)/contact_made
	h2, h3, hr = double/contact_made, triple/contact_made, homer/contact_made
	#estimating number of different outs on balls in play
	outs = contact_made - hits
	fo = (outs / (1 + goao))/contact_made
	go = goao * fo

	contact = [
	.008 * h1 + .188 * h2 + .239 * h3 + .816 * hr + .054 * fo,
	.027 * h1 + .223 * h2 + .231 * h3 + .129 * hr + .109 * fo,
	.641 * h1 + .400 * h2 + .339 * h3 + .001 * hr + .237 * go,
	.030 * h1 + .108 * h2 + .143 * h3 + .054 * hr + .837 * fo,
	.266 * h1 + .077 * h2 + .047 * h3 + .000 * hr + .680 * go,
	.028 * h1 + .004 * h2 + .001 * h3 + .000 * hr + .083 * go
	]
	return contact


def string_to_teams(string):
	away, home = tuple(string.split('@'))
	return home, away


