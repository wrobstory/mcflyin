# -*- coding: utf-8 -*-
'''

Get: A Python front end for the Mcflyin API that easily allows you to
access your data

'''
import json
import pandas as pd
import numpy as np
import requests


def import_data(path=None):
    '''Import JSON into Pandas DataFrame.

    Assumes JSON is an array of timestamps.

    Parameters
    ----------
    path: string, default None
        Path to JSON file

    '''

    with open(path, 'r') as f:
        data = json.load(f)

    df = pd.DataFrame({'Check-in': np.ones(len(data))},
                      index=pd.to_datetime(data))

    return df


def resample(data=None, freq=None):
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


