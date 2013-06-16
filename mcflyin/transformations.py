  # -*- coding: utf-8 -*-
'''
Transformations
-------

Pandas Data Transformations

'''
import json
import functools
import pandas as pd
import pandas.tseries.offsets as offsets
import numpy as np
import statsmodels.api as sm


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

    df = pd.DataFrame({'Events': np.ones(len(data))},
                      index=pd.to_datetime(data))

    return df


@jsonify
def resample(df=None, freq=None):
    '''Pandas resampling convenience function'''
    key, value = freq.keys()[0], freq.values()[0]
    return df.resample(key, how='sum').rename(columns={'Events': value})


@jsonify
def rolling_sum(df=None, window=None, freq=None):
    '''Pandas rolling_sum convenience function'''
    key, value = freq.keys()[0], freq.values()[0]
    sampled = df.resample(key, how='sum').rename(columns={'Events': value})
    rolling = pd.rolling_sum(sampled, window, min_periods=0)
    return rolling


def day_hours(df):
    '''Get Hourly and Daily columns from DataFrame timestamps'''
    df['DoW'] = df['Hour'] = df.index
    weekdays = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday',
                5: 'Friday', 6: 'Saturday', 7: 'Sunday'}
    order = [y for x, y in weekdays.iteritems()]
    df['DoW'] = df['DoW'].apply(lambda x: (x.hour, weekdays[x.isoweekday()]))
    df['Hour'] = df['Hour'].apply(lambda x: x.hour)
    return df, order


@jsonify
def daily(df=None):
    '''Calculate daily sum statistics'''
    key = lambda x: x.isoweekday()
    weekdays = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday',
                5: 'Friday', 6: 'Saturday', 7: 'Sunday'}
    daily = df.groupby(key).sum()['Events']
    daily = pd.DataFrame(daily.rename(weekdays))
    return daily


@jsonify
def hourly(df=None):
    '''Calculate hourly sum statistics'''
    key = lambda x: x.hour
    hourly = pd.DataFrame(df.groupby(key).sum())
    return hourly


def daily_hours(df=None, to_json=False):
    '''Hourly distribution by day of week'''
    weekdays = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday',
                5: 'Friday', 6: 'Saturday', 7: 'Sunday'}
    key1 = lambda x: x.isoweekday()
    key2 = lambda x: x.hour
    weekly = df.groupby([key1, key2]).sum().unstack(0)['Events']
    weekly.index.name = 'Hour'
    weekly = weekly.rename(columns=weekdays)
    if to_json:
        jsonified = jsonify(lambda frame: frame)
        weekly_hours = {}
        for day in weekly.iterkv():
            weekly_hours.update(jsonified(pd.DataFrame(day[1])))
        return weekly_hours
    else:
        return weekly


@jsonify
def forward(df=None, periods=180):
    '''Generate hourly distribution of events for the next `periods`'''
    weekdays = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday',
                5: 'Friday', 6: 'Saturday', 7: 'Sunday'}
    dist = daily_hours(df, to_json=False)
    hourly = df.resample('H', how='sum')
    h_range = pd.date_range(hourly.index[-1] + offsets.Hour(),
                            periods=periods, freq='H')
    forward = pd.DataFrame({'Events': h_range}, index=h_range)
    to_tuple = lambda x: (x.hour, weekdays[x.isoweekday()])
    forward['Events'] = forward['Events'].apply(to_tuple)
    index_dist = lambda x: dist[x[1]][x[0]]
    forward['Events'] = forward['Events'].apply(index_dist)
    return forward


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
                            .rename(columns={'Events': value}))
        concat_list.append(resampled[value]
                           .resample(freq[0][0], fill_method=fill, closed='right'))

    resampled['Combined'] = pd.concat(concat_list, axis=1)

    return resampled
