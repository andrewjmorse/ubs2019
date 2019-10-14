import pandas as pd
import numpy as np
import datetime
import requests
import json
import os


def get_data_request(url, requestData):
    dResp = requests.get(url, headers={'X-api-key': access_token}, params=requestData);

    if dResp.status_code != 200:
        print("Unable to get data. Code %s, Message: %s" % (dResp.status_code, dResp.text));
    else:
        print("Data access successful")
        jResp = json.loads(dResp.text);
        return jResp

sp500 = pd.read_csv('SP500.csv')['Symbol'] # get stock tickers

comm = sp500[:27] # communications
comm.name = 'comm' # set column name for all
cd = sp500[27:90] # consumer discretionary
cd.name = 'cd'
cs = sp500[90:123] # consumer staples
cs.name = 'cs'
en = sp500[123:151] # energy
en.name = 'en'
fin = sp500[151:218] # financials
fin.name = 'fin'
hc = sp500[218:280] # healthcare
hc.name = 'hc'
ind = sp500[280:349] # industrials
ind.name = 'ind'
it = sp500[349:417] # information technology
it.name = 'it'
mat = sp500[417:445] # materials
mat.name = 'mat'
re = sp500[445:477] # real estate
re.name = 're'
util = sp500[477:] # utilities
util.name = 'util'

# make folder for stocks if not exists
if not os.path.exists(os.path.dirname('Stocks/')):
    os.makedirs(os.path.dirname('Stocks/'))

# get all stock data
for ric in sp500:
    RESOURCE_ENDPOINT = "https://dsa-stg-edp-api.fr-nonprod.aws.thomsonreuters.com/data/historical-pricing/beta1/views/summaries/" + ric
    access_token = 'REDACTED' # replace with a valid token

    if os.path.exists('Stocks/{}.csv'.format(ric)) or os.path.exists('Stocks/{}.O.csv'.format(ric)):
        continue
    # try without .O, then with .O; idk, database quirk
    try:
        start_date = '2016-11-01'
        end_date = '2018-05-01'

        requestData = {
            "interval": "P1D",
            "start": start_date,
            "end": end_date,
            "fields": 'TRDPRC_1' #BID,ASK,OPEN_PRC,HIGH_1,LOW_1,TRDPRC_1,NUM_MOVES,TRNOVR_UNS
        };

        jResp = get_data_request(RESOURCE_ENDPOINT, requestData)

        if jResp is not None:
            data = jResp[0]['data']
            headers = jResp[0]['headers']
            names = [headers[x]['name'] for x in range(len(headers))]
            close_price = pd.DataFrame(data, columns=names)

            close_price.columns = ['DATE', 'CLOSE']
            close_price.set_index(pd.to_datetime(close_price.DATE), inplace=True)  # set the index to be the DATE
            close_price.sort_index(inplace=True)  # sort the dataframe by the newly created datetime index
            close_price.to_csv('Stocks/{}.csv'.format(ric),columns=['DATE','CLOSE']) # write
    except:
        0 # Skip
    try:
        ric = ric+".O"
        start_date = '2016-11-01'
        end_date = '2018-05-01'

        requestData = {
            "interval": "P1D",
            "start": start_date,
            "end": end_date,
            "fields": 'TRDPRC_1' #BID,ASK,OPEN_PRC,HIGH_1,LOW_1,TRDPRC_1,NUM_MOVES,TRNOVR_UNS
        };

        jResp = get_data_request(RESOURCE_ENDPOINT, requestData)

        if jResp is not None:
            data = jResp[0]['data']
            headers = jResp[0]['headers']
            names = [headers[x]['name'] for x in range(len(headers))]
            close_price = pd.DataFrame(data, columns=names)

            close_price.columns = ['DATE', 'CLOSE']
            close_price.set_index(pd.to_datetime(close_price.DATE), inplace=True)  # set the index to be the DATE
            close_price.sort_index(inplace=True)  # sort the dataframe by the newly created datetime index
            close_price.to_csv('Stocks/{}.csv'.format(ric),columns=['DATE','CLOSE']) # write
    except:
        0 # Skip

# create sector directory if not exists
if not os.path.exists(os.path.dirname('Sectors/')):
    os.makedirs(os.path.dirname('Sectors/'))

y = 0 # stupid counter because pandas is bad

# create sector files
for x in [comm,cd,cs,en,fin,hc,ind,it,mat,re,util]:
    x_dat = pd.DataFrame() # create a dataframe for this sector

    # add a date column
    try:
        if os.path.exists('Stocks/{}.csv'.format(x[y])):
            x_dat['date'] = pd.read_csv('Stocks/{}.csv'.format(x[y]))['DATE']
        else:
            x_dat['date'] = pd.read_csv('Stocks/{}.O.csv'.format(x[y]))['DATE']
    except:
        print("Sector read failed: {}".format(x.name))
        continue

    # add columns for all stocks
    for i in x:
        y += 1 # need to adjust starting index
        if os.path.exists('Stocks/{}.csv'.format(i)):
            x_dat[i] = pd.read_csv('Stocks/{}.csv'.format(i))['CLOSE']
        elif os.path.exists('Stocks/{}.O.csv'.format(i)):
            x_dat[i] = pd.read_csv('Stocks/{}.O.csv'.format(i))['CLOSE']
        else:
            print("Stock read failed: {}".format(i))
            continue

    x_dat['sum'] = np.zeros(len(x_dat['date']))  # initialize column for sum of all tickers in sector

    # sum columns
    for i in x_dat.columns:
        if x_dat[i].name == 'date':
            continue
        for j in range(len(x_dat[i])):
            x_dat['sum'][j] += x_dat[i][j]

        x_dat[i] = (x_dat[i] / x_dat[i][0]) - 1 # normalize columns to 0

    x_dat.to_csv('Sectors/{}.csv'.format(x.name),columns=x_dat.columns) # write a csv
