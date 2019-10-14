import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

startingcapital = 10000000
capital = startingcapital # initialize starting capital

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

capitaltrack = np.concatenate(([capital, capital, capital, capital, capital, capital, capital], np.empty(369)))

# run the simulation
for i in range(len(sectorrank)):
    if i < 7: # do not trade until our model has data
        continue

    # sell owned, then reinvest
    sell(i)

    capitaltrack[i] = capital
    for j in ownedstocks:
        capitaltrack[i] += j[2] * prices[j[1]][i]

    buy(i)

    if (i == len(sectorrank) - 1): # if it is the final period, sell all stock
        sell(i, force=True)

capitaltrack = pd.DataFrame(data=capitaltrack)
capitaltrack.set_index(pd.to_datetime(sectorrank.index), inplace=True)
capitaltrack.columns = ['value']

# store MSCI world index data
msci = pd.read_csv('historyIndex.csv')[562:581]
msci.set_index(pd.to_datetime(msci.Date), inplace=True) # index date
msci = msci.drop(['Date'], axis=1) # remove bad columns
msci.columns = ['close'] # rename value for simplicity
msci.close = pd.to_numeric(msci.close)

plt.plot(capitaltrack / startingcapital)
plt.plot(msci / msci['close'][0])
plt.legend(['Adjusted return', "Adjusted MSCI index"])
plt.ylabel('Relative value')
plt.title('Returns and MSCI Over Time')
plt.show()

print(capital / startingcapital)

from operator import itemgetter
import re

# converts values for read
def dataconverter(s):
    try:
        return float(s) / 100
    except Exception:
        return np.nan

def get_daily_10yr_treasury_data():
    """Download daily 10 year treasury rates from the Federal Reserve and
    return a pandas.Series."""
    url = "https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15"           "&series=bcb44e57fb57efbe90002369321bfb3f&lastObs=&from=&to="           "&filetype=csv&label=include&layout=seriescolumn"
    return pd.read_csv(url, header=5, index_col=0, names=['DATE', 'BC_10YEAR'],
                       parse_dates=True, converters={1: dataconverter},
                       squeeze=True)

# generate list of risk-free asset values (treasury bond)
riskfree = get_daily_10yr_treasury_data()
riskfree = riskfree['2016-11-01':'2018-05-01'] # get rows in range
riskfree.fillna(method='bfill', inplace=True) # impute backfill values
riskfree = pd.DataFrame(data=riskfree)
riskfree.columns = ['value'] # convert to dataframe and rename

# calculate sharpe ratio
annualreturn = (1 + ((capitaltrack.value[len(capitaltrack) - 1] / startingcapital) - (capitaltrack.value[0] / startingcapital)) / len(capitaltrack))**252.75 - 1
stdreturn = np.std(capitaltrack.value / startingcapital)
sharpe = (annualreturn - np.mean(riskfree)) / stdreturn
print(sharpe)