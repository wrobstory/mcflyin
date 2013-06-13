  # -*- coding: utf-8 -*-
'''
Transformations
-------

Pandas Data Transformations

'''
import json
import functools
import pandas as pd
import numpy as np


def jsonify(func):
    '''Type checking kludge until Pandas 11.1 ships with JSON support'''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        df = func(*args, **kwargs)

        def typeit(obj):
            if isinstance(obj, str):
                return obj
            elif hasattr(obj, 'timetuple'):
                return obj.isoformat()
            elif hasattr(obj, 'item'):
                return obj.item()
            elif hasattr(obj, '__float__'):
                return float(obj)
            elif hasattr(obj, '__int__'):
                return int(obj)
            else:
                raise LoadError('cannot serialize index of type '
                                + type(obj).__name__)

        jsonified = {x[0]: [{typeit(y[0]):typeit(y[1])} for y in x[1].iteritems()]
                     for x in df.iterkv()}

        return jsonified

    return wrapper


def to_df(data):
    '''Import JSON into Pandas DataFrame.

    Assumes JSON is an array of timestamps.

    Parameters
    ----------
    data: list, default None
        List of timestamp strings

    '''

    df = pd.DataFrame({'Check-in': np.ones(len(data))},
                      index=pd.to_datetime(data))

    return df


@jsonify
def resample(df=None, freq=None, fill='pad'):
    '''Pandas resampling convenience function'''
    key, value = freq.keys()[0], freq.values()[0]
    return df.resample(key, how='sum').rename(columns={'Check-in': value})


def combined_resample(df=None, freq=None, fill='pad'):
    '''Generate dict of Pandas DataFrames with multiple time series
    averaging schemes

    Parameters
    ----------
    df: Pandas DataFrame, default None
        Pandas DataFrame with DateTimeIndex and single column of
        relevant data
    freq: iter of tuples, default None
        Frequency(ies) to resample by. Ex: [{'D': 'Daily'}] for daily,
        [{'D': 'Daily'}, {'W': 'Weekly'}] for daily and weekly, etc.
    fill: string, default 'pad'
        Fill method for padding.

    Returns
    -------
    Dict of DataFrames resampled for each passed freq, plus a combined
    DataFrame with a DateTimeIndex that defaults to the first freq passed

    Example
    -------
    >>>resampled = resample(df=myframe, freq=[{'H': 'Hourly'}, {'D': 'Daily'}])
    '''

    resampled = {}
    concat_list = []
    for astype in freq:
        key, value = astype.keys()[0], astype.values()[0]
        resampled[value] = (df.resample(key, how='sum')
                          .rename(columns={'Check-in': value}))
        concat_list.append(resampled[value]
                           .resample(freq[0][0], fill_method=fill, closed='right'))

    resampled['Combined'] = pd.concat(concat_list, axis=1)

    return resampled


@jsonify
def minutes(data):
    '''Test for rolling minutes'''
    df = pd.DataFrame({'Check-in': np.ones(len(data))},
                      index=pd.to_datetime(data))
    minutes = resample(df=df, freq=[('T', 'Minutely')])['Minutely']
    rolling = pd.rolling_sum(minutes['Minutely'], 60, min_periods=0)
    resampled = rolling.resample('H', how='mean', closed='right')
    minutely = pd.DataFrame({'Rolling': resampled})
    return minutely
