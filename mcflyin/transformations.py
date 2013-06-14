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
                raise TypeError('cannot serialize index of type '
                                + type(obj).__name__)

        jsonified = {}
        for x in df.iterkv():
            jsonified[x[0]] = {'time': [], 'data': []}
            for y in x[1].iteritems():
                jsonified[x[0]]['time'].append(typeit(y[0]))
                jsonified[x[0]]['data'].append(typeit(y[1]))

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
def resample(df=None, freq=None):
    '''Pandas resampling convenience function'''
    key, value = freq.keys()[0], freq.values()[0]
    return df.resample(key, how='sum').rename(columns={'Check-in': value})


@jsonify
def rolling_sum(df=None, window=None, freq=None):
    '''Pandas rolling_sum convenience function'''
    key, value = freq.keys()[0], freq.values()[0]
    sampled = df.resample(key, how='sum').rename(columns={'Check-in': value})
    rolling = pd.rolling_sum(sampled, window, min_periods=0)
    return rolling


@jsonify
def day_of_week(df=None, freq=None):
    '''Calculate daily statistics, given a sampling frequency'''
    df = df.resample('T', how='sum')
    df['DoW'] = df['Hour'] = df.index
    weekdays = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday',
                5: 'Friday', 6: 'Saturday', 7: 'Sunday', }
    df['DoW'] = df['DoW'].apply(lambda x: weekdays[x.isoweekday()])
    df['Hour'] = df['Hour'].apply(lambda x: x.hour)


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
