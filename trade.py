import numpy as np
import pandas as pd
import os

# lists of scores and stock ranks, by sector
score = []
stockrank = []

# write list of score data frames
for file in os.listdir('Scores/Scores/'):
    tmp = pd.read_csv('Scores/Scores/{}'.format(file)) # read all sectors in directory
    tmp.set_index(pd.to_datetime(tmp.date), inplace=True)  # index date
    tmp = tmp.drop(['date'], axis=1) # drop extraneous date column
    score.append(tmp) # add to list

# write list of rank data frames
for file in os.listdir('Scores/Ranks/'):
    tmp = pd.read_csv('Scores/Ranks/{}'.format(file))
    tmp.set_index(pd.to_datetime(tmp.date), inplace=True)
    tmp = tmp.drop(['date'], axis=1)
    stockrank.append(tmp)

# write data frame of sector scores
sectorrank = pd.read_csv('Scores/sectorranks.csv')
sectorrank.set_index(pd.to_datetime(sectorrank.date), inplace=True)
sectorrank = sectorrank.drop(['date'], axis=1)

# write data frame of sector names
sectorname = pd.read_csv('Scores/sectornames.csv')
sectorname = sectorname.drop(['Unnamed: 0'], axis=1) # remove bad column
