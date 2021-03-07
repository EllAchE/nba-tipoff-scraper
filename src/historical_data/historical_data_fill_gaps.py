import json
import csv
import pandas as pd
import re
import ENVIRONMENT
import nba_public
import time

def fillGapsLooper(startYear, endYear):
    for year in range(startYear, endYear+1):
        pathIn = '../../Data/CSV/season_data/tipoff_and_first_score_details_{}_season.csv'.format(year) #ENVIRONMENT.SEASON_DATA_GAPS
        pathOut = '../../Data/CSV/gaps_filled/tipoff_and_fist_score_details_{}_season.csv'.format(year) #ENVIRONMENT.SEASON_DATA_GAPS_FILLED
        print(year, pathIn, pathOut)
        fillGaps(year, pathIn, pathOut)


def fillGaps(year, pathIn, pathOut):
    fin = open(pathIn, 'r', encoding='utf8')
    #fout = open(pathOut, 'w')
    fout = open('test.txt', 'w', encoding='utf8')
    count = 0
    for line in fin:
        if re.search(',,,,,,,,,,,,', line) is not None:
            tokenized = line.split(',')
            gameCode = tokenized[0]
            #fout.write(str(count) + ', ' + str(tokenized[0]) + ', ' + str(year) + ', ' + str(tokenized[4]) + ', ' + str(tokenized[5]))
            fout.write(str(count) + ': ' + line)
            try:
                tipOffContent = nba_public.getTipoffLineFromBballRefId(gameCode)
                fout.write(tipOffContent.HOMEDESCRIPTION)
            except IndexError:
                fout.write("failed to retrieve for " + gameCode)
            count += 1
            print(count)
            time.sleep(1.5)
            #print(nba_public.getParticipatingTeamsFromId(nba_public.getGameIdFromBballRef(gameCode)))
        #else:
            #fout.write(line)
            #print(line)
    fin.close()
    fout.close()


fillGapsLooper(1998, 1998)
