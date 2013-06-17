# -*- coding: utf-8 -*-
'''
McFlyin API example.

Take data from Python to send to an API in Python to transform data in Python to receive in Python to transform in Python.

But you can take data from ___ to send to an API in Python to transform data in Python to recieve in ____ to transform in ____

'''

import pandas as pd
import requests
import json
import bearcart

#Some DataFrame transformations for convenience
def single_df(response):
    '''Convert single item response to DataFrame'''
    key = response.keys()[0]
    index = pd.to_datetime(response[key]['time'])
    df = pd.DataFrame({key: response[key]['data']}, index=index)
    return df


def multi_df(response):
    '''Convert multi-item response to DataFrame'''
    concat = []
    for day, data in response.iteritems():
        concat.append(pd.DataFrame({day: data['data']}, index=data['time']))
    df = pd.concat(concat, axis=1)
    return df

#Read data, turn into single list of timestamps
data = pd.read_csv('AllPandas.csv')
data = data['CreationDate'].tolist()

daily = {'D': 'Daily'}
monthly = {'M': 'Monthly'}
sends_1 = {'freq': json.dumps(daily), 'data': json.dumps(data)}
sends_2 = {'freq': json.dumps(monthly), 'data': json.dumps(data)}
rdaily = requests.post('http://127.0.0.1:5000/resample', data=sends_1)
rmonthly = requests.post('http://127.0.0.1:5000/resample', data=sends_2)

df_daily = single_df(rdaily.json)
df_monthly = single_df(rmonthly.json)

#Rolling sum
freq = {'D': 'Weekly Rolling'}
sends = {'freq': json.dumps(freq), 'data': json.dumps(data), 'window': 7}
r_rolling = requests.post('http://127.0.0.1:5000/rolling_sum', data=sends)
df_rolling = single_df(r_rolling.json)

#Daily mean
sends = {'data': json.dumps(data), 'how': json.dumps('mean')}
m_daily = requests.post('http://127.0.0.1:5000/daily', data=sends)
m_dailied = m_daily.json
df_mdaily = pd.DataFrame({'Events': m_dailied['Events']['data']},
                         index=m_dailied['Events']['time'])

#Daily overall sum
sends = {'data': json.dumps(data), 'how': json.dumps('sum')}
s_daily = requests.post('http://127.0.0.1:5000/daily', data=sends)
s_dailied = s_daily.json
df_sdaily = pd.DataFrame({'Events': s_dailied['Events']['data']},
                         index=s_dailied['Events']['time'])


