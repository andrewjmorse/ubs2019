import numpy as np
import pandas as pd
import os

capital = 10000000 # initialize starting capital

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

prices = pd.DataFrame(index=range(0,376))
prices.set_index(sectorrank.index, inplace=True)

# read all original stock prices
for file in os.listdir('Sectors-orig/'):
    tmp = pd.read_csv('Sectors-orig/{}'.format(file))
    tmp.set_index(pd.to_datetime(tmp.date), inplace=True)
    tmp = tmp.drop(['date'], axis=1) # drop unneeded cols
    tmp = tmp.drop(['Unnamed: 0'], axis=1)
    tmp = tmp.drop(['sum'], axis=1)
    prices = prices.join(tmp)

# create list of owned stocks
ownedstocks = []

# function run daily to buy
# day = day of analysis, nsectors = number of sectors to buy from, nstocks = number of stocks to buy per sector,
# tcost = transaction cost, as a percentage above 1, agg = proportion of capital to invest each period
def buy(day, nsectors=3, nstocks=3, tcost=1.0, agg=1.0):
    global capital # declare capital to pass value
    bestsectors = [] # list of best performing sectors
    beststocks = [] # list of best performing stocks within sectors
    scorelist = [] # list of scores of best stocks
    for i in range(nsectors):
        bestsectors.append(sectorrank[str(i)][day])
    for i in bestsectors:
        for j in range(nstocks):
            beststocks.append([i, stockrank[i][str(j)][day]])
    for i in beststocks:
        scorelist.append(score[i[0]][score[i[0]].columns[i[1]]][day])

    j = 0 # initialize counter or number of stocks deleted

    # ensure we only buy stocks with positive score
    for i in range(len(scorelist)):
        if scorelist[i-j] <= 0:
            del scorelist[i-j]
            del beststocks[i-j]
            j += 1

    prop = [] # proportion of capital to invest in each stock
    investval = [] # amount of capital to invest in each stock
    ninvest = [] # quantity of each stock to buy

    # calculate above figures
    for i in range(len(scorelist)):
        prop.append(scorelist[i] / np.sum(scorelist))
        investval.append(capital*agg*prop[i])
        ninvest.append(int(np.floor(investval[i] / (tcost * prices[score[beststocks[i][0]].columns[beststocks[i][1]]][day]))))

    # decrement capital after purchase, add stocks to list of owned stocks
    for i in range(len(beststocks)):
        ownedstocks.append([beststocks[i][0], score[beststocks[i][0]].columns[beststocks[i][1]], ninvest[i]])
        capital -= ninvest[i] * tcost * prices[score[beststocks[i][0]].columns[beststocks[i][1]]][day]

    return

buy(7)

# function run daily to sell
# day = day of analysis, nsectors = number of sectors to buy from, force = logical operator: must sell all if true
def sell(day, nsectors=3, force=False):
    if not ownedstocks: # if there is nothing to sell, sell nothing
        return

    global capital # declare capital to pass value
    bestsectors = [] # list of best performing sectors

    # generate list of best sectors
    for i in range(nsectors):
        bestsectors.append(sectorrank[str(i)][day])

    j = 0 # count number of tickers sold

    # if a stock is not in the best sectors, sell it
    for i in range(len(ownedstocks)):
        if not ownedstocks[i-j][0] in bestsectors or force:
            capital += ownedstocks[i-j][2] * prices[ownedstocks[i-j][1]][day]
            del ownedstocks[i-j]
            j += 1

# run the simulation
for i in range(len(sectorrank)):
    if i < 7: # do not trade until our model has data
        continue

    # sell owned, then reinvest
    sell(i)
    buy(i)

    if (i == len(sectorrank) - 1): # if it is the final period, sell all stock
        sell(i, force=True)
