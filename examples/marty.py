# -*- coding: utf-8 -*-
'''

Marty: An example of a Python front-end for the McFlyin API

'''
import json
import requests


def forward(data=None, periods=180, to_df=False):
    '''Given a list of timestamps, generate the next `periods` of hourly data,
    via daily averaging.

    Parameters
    ----------
    data: list, default None
        list of timestamp strings
    periods: int, default None
        Number of periods to predict forward. Ex: periods=180 will provide the next
        week of data
    to_df: boolean, default False
        Convert dict response into a Pandas DataFrame

    Returns
    -------
    Dict or Pandas DataFrame of resampled values

    Example
    -------
    >>>forward = forward(data=mylist, periods=180, to_df=True)

    '''

    send = {'periods': json.dumps(periods), 'data': json.dumps(data)}
    r = requests.post('http://127.0.0.1:5000/forward', data=send)
    response = r.json

    if to_df:
        import pandas as pd
        key = response.keys()[0]
        index = pd.to_datetime(response[key]['time'])
        df = pd.DataFrame({key: response[key]['data']}, index=index)
        return df

    return response


def daily_hours(data=None, to_df=False):
    '''Given a list of timestamps, find the number of events by hour on a daily
    basis.

    Parameters
    ----------
    data: list, default None
        list of timestamp strings
    to_df: boolean, default False
        Convert dict response into a Pandas DataFrame

    Returns
    -------
    Dict or Pandas DataFrame of daily hourly events

    Example
    -------
    >>>daily = daily_hours(data=mylist, to_df=True)

    '''

    send = {'data': json.dumps(data)}
    r = requests.post('http://127.0.0.1:5000/daily_hours', data=send)
    response = r.json

    if to_df:
        import pandas as pd
        concat = []
        for day, data in response.iteritems():
            concat.append(pd.DataFrame({day: data['data']}, index=data['time']))
        df = pd.concat(concat, axis=1)
        return df

    return response


def resample(data=None, freq=None, to_df=False):
    '''Generate Timeseries of given sampling rate from list of
    timestamp strings.

    Must use one of the Pandas offset aliases:
    http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases

    Parameters
    ----------
    data: list, default None
        list of timestamp strings
    freq: dict, default None
        Frequency to sample by. Ex: {'D', 'Daily'}
    to_df: boolean, default False
        Convert dict response into a Pandas DataFrame

    Returns
    -------
    Dict or Pandas DataFrame of resampled values

    Example
    -------
    >>>sampled = resample(data=mylist, freq={'H': 'Hourly'})

    '''

    send = {'freq': json.dumps(freq), 'data': json.dumps(data)}
    r = requests.post('http://127.0.0.1:5000/resample', data=send)
    response = r.json

    if to_df:
        import pandas as pd
        key = response.keys()[0]
        index = pd.to_datetime(response[key]['time'])
        df = pd.DataFrame({key: response[key]['data']}, index=index)
        return df

    return response


def rolling_sum(data=None, window=None, freq=None, to_df=False):
    '''Generate Rolling sum for a timeseries of a given sampling rate from list of
    timestamp strings.

    Must use one of the Pandas offset aliases for the key of freq:
    http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases

    Parameters
    ----------
    data: list, default None
        list of timestamp strings
    window: int, default None
        Sampling window. Ex: If you pass {'T', 'Minutely'} as the freq, a window
        of 60 will create an hourly rolling mean.
    freq: dict, default None
        Frequency to sample by. Ex: {'D', 'Daily'}
    to_df: boolean, default False
        Convert dict response into a Pandas DataFrame

    Returns
    -------
    Dict or Pandas DataFrame of resampled values

    Example
    -------
    >>>rolling = rolling_sum(data=mylist, window=60, freq={'T': 'Minutely'})

    '''
    if not freq or not window:
        raise ValueError('Please include all required parameters.')

    send = {'freq': json.dumps(freq), 'data': json.dumps(data), 'window': window}
    r = requests.post('http://127.0.0.1:5000/rolling_sum', data=send)
    response = r.json

    if to_df:
        import pandas as pd
        key = response.keys()[0]
        index = pd.to_datetime(response[key]['time'])
        df = pd.DataFrame({key: response[key]['data']}, index=index)
        return df

    return response


def combined_resample(data=None, freq=None):
    '''Generate dict of Pandas DataFrames with multiple time series
    averaging schemes

    Parameters
    ----------
    data: list, default None
        list of timestamp strings
    freq: iter of dicts, default None
        Frequency(ies) to resample by. Ex: [{'D': 'Daily'}] for daily,
        [{'D': 'Daily'}, {'W': 'Weekly'}] for daily and weekly, etc.
        The key dictates the resampling, the value the column header.

    Returns
    -------
    Dict of DataFrames resampled for each passed freq, plus a combined
    DataFrame with a DateTimeIndex that defaults to the first freq passed

    Example
    -------
    >>>sampled = resample(data=mylist, freq=[{'H': 'Hourly'}, {'D':'Daily'}])
    '''

    if not freq or not window:
        raise ValueError('Please include all required parameters.')

    send = {'freq': json.dumps(freq), 'data': json.dumps(data)}
    r = requests.post('http://127.0.0.1:5000/resample', data=send)
    return r.json()
