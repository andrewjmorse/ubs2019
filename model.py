import numpy as np
import pandas as pd
import datetime
import matplotlib
import matplotlib.pyplot as plt
import os
import statsmodels.regression.linear_model as sm

# create a list for the sector dataframes
sectors = []

# store MSCI world index data
msci = pd.read_csv('historyIndex.csv')[550:581]
msci.set_index(pd.to_datetime(msci.Date), inplace=True)
msci = msci.drop(['Date'], axis=1) # remove bad columns
msci.columns = ['close'] # rename value for simplicity

# read and format sector dataframes
for file in os.listdir('Sectors/'):
    tmp = pd.read_csv('Sectors/{}'.format(file))
    tmp = tmp.drop(['Unnamed: 0'], axis=1) # remove bad columns
    tmp.set_index(pd.to_datetime(tmp.date), inplace=True)
    tmp = tmp.drop(['date'], axis=1)
    sectors.append(tmp)

# create lists of moving average dataframes
moving7 = []
moving14 = []
moving30 = []
moving60 = []

movingsd7 = []
movingsd14 = []
movingsd30 = []
movingsd60 = []

movingdd7 = []
movingdd14 = []
movingdd30 = []
movingdd60 = []

movingdif7 = []
movingdif14 = []
movingdif30 = []
movingdif60 = []

dist = [7, 14, 30, 60] # define sizes of moving averages
i = 0 # iterator across sizes

# build moving average dataframes
for x in [moving7, moving14, moving30, moving60]:
    for y in sectors:
        df = y.diff(periods=1).rolling(window=dist[i]).mean() # create moving average
        # make dates consistent
        x.append(df)
    i += 1 # move to next window

i = 0 # reset counter

for x in [movingsd7, movingsd14, movingsd30, movingsd60]:
    for y in sectors:
        df = y.diff(periods=1).rolling(window=dist[i]).std() # create moving standard deviation
        # make dates consistent
        x.append(df)
    i += 1 # move to next window

i = 0

for x in [movingdd7, movingdd14, movingdd30, movingdd60]:
    for y in sectors:
        df = y.rolling(window=dist[i]).max() - y.rolling(window=dist[i]).min() # create moving drawdown
        # make dates consistent
        x.append(df)
    i += 1 # move to next window

i = 0

for x in [movingdif7, movingdif14, movingdif30, movingdif60]:
    for y in sectors:
        df = y.diff(periods=dist[i]) # create differences
        # make dates consistent
        x.append(df)
    i += 1 # move to next window

# ric = 'AAP' # stock ticker to display

# # plot
# plt.plot(sectors[0][ric])
# plt.plot(moving7[0][ric])
# plt.plot(moving14[0][ric])
# plt.plot(moving30[0][ric])
# plt.plot(moving60[0][ric])
# plt.legend([ric,'{} days'.format(dist[0]),'{} days'.format(dist[1]),'{} days'.format(dist[2]),'{} days'.format(dist[3])])
# plt.show()
#
# plt.plot(sectors[0][ric])
# plt.plot(movingsd7[0][ric])
# plt.plot(movingsd14[0][ric])
# plt.plot(movingsd30[0][ric])
# plt.plot(movingsd60[0][ric])
# plt.legend([ric,'{} days'.format(dist[0]),'{} days'.format(dist[1]),'{} days'.format(dist[2]),'{} days'.format(dist[3])])
# plt.show()
#
# plt.plot(sectors[0][ric])
# plt.plot(movingdd7[0][ric])
# plt.plot(movingdd14[0][ric])
# plt.plot(movingdd30[0][ric])
# plt.plot(movingdd60[0][ric])
# plt.legend([ric,'{} days'.format(dist[0]),'{} days'.format(dist[1]),'{} days'.format(dist[2]),'{} days'.format(dist[3])])
# plt.show()
#
# plt.plot(sectors[0][ric])
# plt.plot(movingdif7[0][ric])
# plt.plot(movingdif14[0][ric])
# plt.plot(movingdif30[0][ric])
# plt.plot(movingdif60[0][ric])
# plt.legend([ric,'{} days'.format(dist[0]),'{} days'.format(dist[1]),'{} days'.format(dist[2]),'{} days'.format(dist[3])])
# plt.show()

r2 = [] # list of lists of Pearson's r**2, separated by predictor and then by sector

for x in [moving7, moving14, moving30, moving60, movingsd7, movingsd14, movingsd30, movingsd60]:
    sectorr2 = [] # list of r**2 for each sector
    for i in range(len(x)):
        stockr2 = [] # list of r**2 for each stock
        for col in x[i]:
            # model = sm.GLS(sectors[i][col],x[i][col],missing='drop') # predict stock value from predictor, using GLS
            # result = model.fit()
            model2 = sm.GLS(movingdif7[i][col].shift(periods=7), x[i][col], missing='drop') # predict again, shifted a week ahead
            result2 = model2.fit()
            # stockr2.append((result.rsquared_adj + result2.rsquared_adj) / 2)  # extract model r**2
            stockr2.append(result2.rsquared_adj)  # extract model r**2
        stockr2 = np.array(stockr2)
        sectorr2.append(np.mean(stockr2))
    r2.append(sectorr2)

score = [] # list of dataframes of day-to-day score by date

for i in range(len(sectors)):
    # use fitted weights to score each stock
    df = 10 * (r2[0][i]*moving7[i].fillna(0) + r2[1][i]*moving14[i].fillna(0) + r2[2][i]*moving30[i].fillna(0) + r2[3][i]*moving60[i].fillna(0) - r2[4][i]*movingsd7[i].fillna(0) \
         - r2[5][i]*movingsd14[i].fillna(0) - r2[6][i]*movingsd30[i].fillna(0) - r2[7][i]*movingsd60[i].fillna(0))
    score.append(df)

ric = 'AMZN' # stock ticker to display

# plot
plt.plot(sectors[0][ric])
plt.plot(score[0][ric])
plt.hlines(0, xmin='2016-11', xmax='2018-05')
plt.show()
# scores have no inherent meaning, but have meaning relative to each other