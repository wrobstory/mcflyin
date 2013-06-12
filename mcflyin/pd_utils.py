  # -*- coding: utf-8 -*-
'''
Binificator
-------

Import and bin JSON timeseries data by various timescales

'''
import json
import pandas as pd
import numpy as np


def import_data(path=None):
    '''Import JSON into Pandas DataFrame

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


def resample(df=None, freq=None, fill='pad'):
    '''Generate dict of Pandas DataFrames with multiple time series
    averaging schemes

    Parameters
    ----------
    df: Pandas DataFrame, default None
        Pandas DataFrame with DateTimeIndex and single column of
        relevant data
    freq: iter of tuples, default None
        Frequency(ies) to resample by. Ex: [('D', 'Daily')] for daily,
        [('D', 'Daily'), ('W', 'Weekly')] for daily and weekly, etc.
    fill: string, default 'pad'
        Fill method for padding.

    Returns
    -------
    Dict of DataFrames resampled for each passed freq, plus a combined
    DataFrame with a DateTimeIndex that defaults to the first freq passed

    Example
    -------
    >>>resampled = resample(df=myframe, freq=[('H', 'Hourly'), ('D', 'Daily')])
    '''

    resampled = {}
    concat_list = []
    for astype in freq:
        resampled[astype[1]] = (df.resample(astype[0], how='sum')
                                .rename(columns={'Check-in': astype[1]}))
        concat_list.append(resampled[astype[1]]
                           .resample(freq[0][0], fill_method=fill, closed='right'))

    resampled['Combined'] = pd.concat(concat_list, axis=1)

    return resampled
