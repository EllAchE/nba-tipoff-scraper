# Finding Games
# https://github.com/swar/nba_api/blob/master/docs/examples/Finding%20Games.ipynb

# Pulling play by play
# https://github.com/swar/nba_api/blob/master/docs/examples/PlayByPlay.ipynb

'''
1. Individual player scoring percent on first shot
2. player score percent overall
3. Team score percent first shot
4. Team score percent overall
5. The above but for defense (opponents)
6. Percentage of first shots taken by particular player
7. Percentage of first shots made by player overall
8. Above two extended up until first basket made/for first X shots
9. Above for opponents
10. Team FT rate, two point vs. 3 point etc.
11. Number of shots until first made
12. First tip performance
13. Non standard tip
14. Low appearance tip

To fetch here
Individual player scoring percent on first shot
Team score percent first shot
Percentage of first shots made by player overall
Percentage of first shots taken by particular player

'''

from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.endpoints import gamerotation, playbyplayv2
from typing import Any

from .utils import getDashDateAndHomeCodeFromGameCode

# TODO: Writing type stubs for pandas' DataFrame is too cumbersome, so we use this instead.
# Eventually, we should replace that with real type stubs for DataFrame.
DataFrame = Any

def convertBballRefTeamShortCodeToNBA(short_code: str):
    if short_code == 'PHO':
        return 'PHX'
    
    if short_code == 'BRK':
        return 'BKN'
    
    return short_code

def getTeamDictionaryFromShortCode(short_code: str):
    short_code = convertBballRefTeamShortCodeToNBA(short_code)
    nba_teams = teams.get_teams()
    team_dict = [team for team in nba_teams if team['abbreviation'] == short_code][0]
    return team_dict['id']

def getAllGamesForTeam(team_id: str):
    gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id)
    return gamefinder.get_data_frames()[0]

def getAllGamesInSeason(season: int, short_code: str):
    season -= 1
    team_id = getTeamDictionaryFromShortCode(short_code)
    games_df = getAllGamesForTeam(team_id)
    
    return games_df[games_df.SEASON_ID.str[-4:] == str(season)]

# game date format is YYYY-MM-DD
def _getGameObjFromDateAndTeam(date_str: str, short_code: str):
    team_id = getTeamDictionaryFromShortCode(short_code)
    all_games = getAllGamesForTeam(team_id)
    return all_games[all_games.GAME_DATE == str(date_str)]

def getGameIdFromTeamAndDate(date_str: str, short_code: str):
    game_obj = _getGameObjFromDateAndTeam(date_str, short_code)
    return game_obj.GAME_ID.iloc[0]

def getGamePlayByPlay(game_id: str):
    return playbyplayv2.PlayByPlayV2(game_id).get_data_frames()[0]

def getPlayerFromShotDescription(description: str): # if this need to be fully generic then fetch the playerlast names and do a match on that
    isMiss = "MISS" in description
    splitDescription = description.split(' ')
    
    if isMiss:
        return splitDescription[1]
    else:
        return splitDescription[0]

def getShotTypeFromEventDescription(description: str):
    isMiss = "MISS" if "MISS" in description or "BLOCK" in description else "MAKE"
    
    if "3PT" in description:
        return "3PT " + isMiss
    
    if "Free Throw" in description:
        return "FREE THROW " + isMiss
    
    return "2PT " + isMiss

def getFirstShotStatistics(shotsBeforeFirstScore: DataFrame):
    shotIndex = 0
    dataList = list[Any]()
    teamDict = getParticipatingTeamsFromId(shotsBeforeFirstScore.iloc[0].GAME_ID)
    homeTeam = teamDict['home']
    awayTeam = teamDict['away']

    dfLen = len(shotsBeforeFirstScore.index)
    while shotIndex < dfLen:
        row = shotsBeforeFirstScore.iloc[shotIndex]
        description = row.HOMEDESCRIPTION if row.HOMEDESCRIPTION is not None else row.VISITORDESCRIPTION
        team = awayTeam if row.HOMEDESCRIPTION is None else homeTeam
        player = getPlayerFromShotDescription(description)
        shotType = getShotTypeFromEventDescription(description)
        dataList.append({"shotIndex": shotIndex, "team": team, "player": player, "shotType": shotType})      # free throws should be considered a collective shot, not individual
        shotIndex += 1
    return dataList

def _getAllShotsBeforeFirstScore(playsBeforeFirstFgDf: DataFrame):
    shootingPlays = playsBeforeFirstFgDf[playsBeforeFirstFgDf['EVENTMSGTYPE'].isin([1, 2, 3])]
    return shootingPlays

def getAllEventsBeforeFirstScore(pbpDf: DataFrame):
    i = 0
    for item in pbpDf.SCORE:
        if item is not None:
            return pbpDf[:(i + 1)]
        i += 1

def gameIdToFirstShotList(id: str):
    pbpDf = playbyplayv2.PlayByPlayV2(game_id=id).get_data_frames()[0]
    plays = getAllEventsBeforeFirstScore(pbpDf)
    shots = _getAllShotsBeforeFirstScore(plays)
    return shots

def getParticipatingTeamsFromId(id: str) -> dict[str, str]:
    response = gamerotation.GameRotation(game_id=id)
    awayTeamCity = response.away_team.get_dict()['data'][0][2]
    awayTeamName = response.away_team.get_dict()['data'][0][3]
    awayTeamId = response.away_team.get_dict()['data'][0][4]
    homeTeamCity = response.home_team.get_dict()['data'][0][2]
    homeTeamName = response.home_team.get_dict()['data'][0][3]
    homeTeamId = response.home_team.get_dict()['data'][0][4]
    
    return {"home": homeTeamCity + ' ' + homeTeamName, "homeId": homeTeamId, "away": awayTeamCity + ' ' + awayTeamName, "awayId": awayTeamId}

def getTipoffLine(pbpDf: DataFrame, returnIndex: bool = False):
    try:
        tipoffSeries = pbpDf[pbpDf.EVENTMSGTYPE == 10]
        tipoffContent = tipoffSeries.iloc[0]
        type = 10
    except:
        tipoffSeries = pbpDf[pbpDf.EVENTMSGTYPE == 7]
        tipoffContent = tipoffSeries.iloc[0]
        type = 7

    print('Home Desc', tipoffContent.HOMEDESCRIPTION, 'Vis Desc', tipoffContent.VISITORDESCRIPTION, 'Neut Desc', tipoffContent.NEUTRALDESCRIPTION)

    if tipoffContent.HOMEDESCRIPTION is not None:
        content = tipoffContent.HOMEDESCRIPTION
        isHome = True
    elif tipoffContent.VISITORDESCRIPTION is not None:
        content = tipoffContent.VISITORDESCRIPTION
        isHome = False
    else:
        raise ValueError('nothing for home or away, neutral said', tipoffContent.NEUTRALDESCRIPTION)

    if returnIndex:
        return content, type, isHome, tipoffContent.index
    return content, type, isHome


def getTipoffLineFromGameId(gameId: str):
    pbpDf = getGamePlayByPlay(gameId)
    tipoffContent = getTipoffLine(pbpDf)
    return tipoffContent


test_bad_data_games = [['199711110MIN', 'MIN', 'SAS'],
                        ['199711190LAL', 'LAL', 'MIN'],
                        ['201911200TOR', 'TOR', 'ORL'],
                        ['201911260DAL', 'DAL', 'LAC'],
                        ['199711240TOR'], ['199711270IND'], ['201911040PHO']]


a, b = getDashDateAndHomeCodeFromGameCode('199711190LAL')
id = getGameIdFromTeamAndDate(a, b)

x = gameIdToFirstShotList(id)
y = getFirstShotStatistics(x)
print()

# class EventMsgType(Enum):
#     FIELD_GOAL_MADE = 1 #todo replace above uses of numbers with ENUM values for readability
#     FIELD_GOAL_MISSED = 2
#     FREE_THROWfree_throw_attempt = 3
#     REBOUND = 4
#     TURNOVER = 5
#     FOUL = 6
#     VIOLATION = 7
#     SUBSTITUTION = 8
#     TIMEOUT = 9
#     JUMP_BALL = 10
#     EJECTION = 11
#     PERIOD_BEGIN = 12
#     PERIOD_END = 13

# def getNbaComResultsFromBballReferenceCode(bballCode):
#     date, team_code = getDashDateAndHomeCodeFromGameCode(bballCode)
#     test = getGameIdFromTeamAndDate(date, team_code)
#     deb = getTipoffResults(test)
#     print(deb)


# for item in test_bad_data_games:
#     getNbaComResultsFromBballReferenceCode(item[0])

# todo use this work (specifically the getTipoffLine) to fill in the blanks on the missing games in the csv