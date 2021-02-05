# I need to - provide team name
# get starting centers
# get if they are home or away
# get odds for the bets of the day
# get positive EV threshold
# get the center ratings
# calculate expected odds of tip win
# multiply expected tip win by tip winner scoring ratio to get expected score prob (include tip loss score case)
# OPTIONAL - Adjust for home court etc.
# see if expected score prob is higher than EV threshold (or below 1 - EV thresh)
# if bet should be done
# calculate kelly bet size
# reduce to kelly consumable size

# Format is https://www.basketball-reference.com/boxscores/pbp/201901220OKC.html
# Home team 3 letter symbol is used after a 0, i.e. YYYYMMDD0###.html
#
# URL for game https://www.basketball-reference.com/boxscores/pbp/201901220OKC.html
# Where YYYYMMDD0### (# = home team code)
#
# game schedule in order for seasons https://www.basketball-reference.com/leagues/NBA_2019_games.html
# Creating json/dictonary would probably be best
#
# Games played https://www.basketball-reference.com/leagues/NBA_2019_games-october.html
# Year is ending year (i.e. 2018-2019 is 2019)
# All relevant are October-June except 2019-2020 and 2020-21 (first bc covid, second is in progress)


# Steps to NBA check:
#
# Base requirements:
# -	Find the starters for each team/who does the tipoff:
# -	Player W/L %
#
# Additional variables
# -	Ref
# -	Is starter out
# -	Home/away
# -	Who they tip it to
# -	Matchup
# -	Height
# -	Offensive effectiveness
# -	Back-to-back games/overtime etc.
# -	Age decline
# -	Recent history weighting