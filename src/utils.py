import json
import random
import time
import requests
import unicodedata
import unidecode

from bs4 import BeautifulSoup

import ENVIRONMENT

def customNbaSeasonFormatting(season):
    intAdd = season % 100 + 1
    return str(season) + '-' + str(intAdd)

def addSlugToNames():
    with open(ENVIRONMENT.TEAM_NAMES_PATH) as dat_file:
        team_dict = json.load(dat_file)

    for team in team_dict:
        slug = team['teamName']
        slug = slug.replace(" ", "-")
        slug = slug.lower()
        team['slug'] = slug

    with open(ENVIRONMENT.TEAM_NAMES_PATH, 'w') as w_file:
        json.dump(team_dict, w_file, indent=4)
    print('added slugs')

def checkForBadSuffix(suffix):
    if suffix == '/players/c/capelcl01.html':
        return '/players/c/capelca01.html'
    return suffix

def getPlayerSuffix(name: str):
    # copied from this repo https://github.com/vishaalagartha/basketball_reference_scraper/blob/master/basketball_reference_scraper
    normalized_name = unidecode.unidecode(unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode("utf-8"))
    nameSplit = normalized_name.lower().split(' ')
    initial = nameSplit[-1][0]
    suffix = '/players/' + initial +'/' + createSuffix(name)
    ogSuffix = suffix
    playerRequest = requests.get(f'https://www.basketball-reference.com{suffix}')
    
    while playerRequest.status_code == 200:
        player_soup = BeautifulSoup(playerRequest.content, 'html.parser')
        h1 = player_soup.find('h1', attrs={'itemprop': 'name'})
        
        if h1:
            page_name = h1.find('span').text
            """
                Test if the URL we constructed matches the name of the player on that page; if it does,
                return suffix, if not add 1 to the numbering and recheck.
            """
            if ((unidecode.unidecode(page_name)).lower() == normalized_name.lower()):
                suffix = checkForBadSuffix(suffix)
                return suffix
            else:
                suffix = suffix[:-6] + str(int(suffix[-6])+1) + suffix[-5:]
                playerRequest = requests.get(f'https://www.basketball-reference.com{suffix}')

    print('couldn\'t find match for player', ogSuffix, 'returning naive suffix')
    ogSuffix = checkForBadSuffix(ogSuffix)
    return ogSuffix

def createSuffix(name: str):
    # copied from this repo https://github.com/vishaalagartha/basketball_reference_scraper/blob/master/basketball_reference_scraper
    normalizedName = unicodedata.normalize('NFD', name.replace(".","")).encode('ascii', 'ignore').decode("utf-8")
    normalizedNameNoSpace = normalizedName.replace(' ', '')
    first = unidecode.unidecode(normalizedNameNoSpace[:2].lower())
    lasts = normalizedName.split(' ')[1:]
    names = ''.join(lasts)
    second = ""

    if len(names) <= 5:
        second += names[:].lower()
    else:
        second += names[:5].lower()

    return second + first

def getDashDateFromGameCode(gameCode: str):
    gameCode = str(gameCode)
    year = gameCode[:4]
    month = gameCode[4:6]
    day = gameCode[6:8]
    return year + '-' + month + '-' + day

def getTeamFullFromShort(shortCode):
    with open(ENVIRONMENT.TEAM_NAMES_PATH) as teamsJson:
        teamDict = json.load(teamsJson)
    for team in teamDict:
        if team["abbreviation"] == shortCode:
            return team["teamName"]
    raise ValueError('No team match found for code', shortCode)

def getHomeTeamFromGameCode(game_code: str):
    return game_code[-3:]

def getSoupFromUrl(url: str, headers=None, returnStatus: bool = False):
    if headers is not None:
        page = requests.get(url, headers=headers)
    else:
        page = requests.get(url)

    if returnStatus:
        return BeautifulSoup(page.content, 'html.parser'), page.status_code
    
    return BeautifulSoup(page.content, 'html.parser')

def getDashDateAndHomeCodeFromGameCode(game_code: str):
    return getDashDateFromGameCode(game_code), getHomeTeamFromGameCode(game_code)

def sleepChecker(iterations: int = 3, baseTime: int = 2, randomMultiplier: int = 3, printStop: bool = False):
    with open(ENVIRONMENT.SLEEP_CHECKER_PATH) as sc:
        SLEEP_COUNTER = json.load(sc)

    SLEEP_COUNTER['counter'] += 1
    if SLEEP_COUNTER['counter'] % iterations == 0:
        if printStop:
            print("sleeping for", str(baseTime), "+ random seconds")
        time.sleep(baseTime + random.random() * randomMultiplier)
        SLEEP_COUNTER['counter'] = 0

    with open(ENVIRONMENT.SLEEP_CHECKER_PATH, 'w') as sc:
        json.dump(SLEEP_COUNTER, sc, indent=4)

def removeAllNonLettersAndLowercase(name):
    playerLowered = name.replace(' ', '')
    playerLowered = playerLowered.replace('.', '')
    playerLowered = playerLowered.replace('-', '')
    playerLowered = playerLowered.replace('\'', '')
    playerLowered = playerLowered.replace('_', '')
    return playerLowered.lower()

def lowercaseNoSpace(str):
    return str.replace(' ', '').lower()

def removeNewLineChars(str):
    return str.replace('\n', '')

def determineBetterOdds(odds1Str, odds2Str):
    if odds1Str[0] != odds2Str[0]:
        oddsStr = odds1Str if odds1Str == '+' else odds2Str
    elif odds1Str[0] == '+':
        oddsStr = odds1Str if odds1Str[1:] >= odds2Str[1:] else odds2Str
    elif odds1Str[0] == '-':
        oddsStr = odds1Str if odds1Str[1:] <= odds2Str[1:] else odds2Str
    else:
        raise ValueError('shouldn\'t reach here, check odds formatting')
    return oddsStr
