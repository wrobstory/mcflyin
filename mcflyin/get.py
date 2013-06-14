# -*- coding: utf-8 -*-
'''

Get: A Python front end for the Mcflyin API that easily allows you to
access your data

'''
import json
import requests


def resample(data=None, freq=None, to_df=False):
    '''Generate Pandas DataFrame at given sampling rate from list of
    timestamp strings

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

    send = {'freq': json.dumps(freq), 'data': json.dumps(data)}
    r = requests.post('http://127.0.0.1:5000/resample', data=send)
    return r.json()


