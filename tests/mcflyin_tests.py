# -*- coding: utf-8 -*-
'''
McFlyin Tests

'''
from __future__ import print_function, division
import json
import numpy as np
import pandas as pd
import pandas.util.testing as pdtest
import mcflyin


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


class testMcflyin(object):

    @classmethod
    def setup_class(cls):
        '''Setup data'''
        rng = pd.date_range('6/16/2013', periods=10080, freq='T')
        iso = []
        for date in rng:
            iso.append(date.isoformat())
        cls.data = iso

    def setup(self):
        '''Setup App for testing'''
        mcflyin.application.app.config['TESTING'] = True
        self.app = mcflyin.application.app.test_client()

    def test_resample(self):
        '''Test Resampling'''
        send = {'freq': json.dumps({'H': 'Hourly'}),
                'data': json.dumps(self.data)}
        rv = self.app.post('resample', data=send)
        df = single_df(json.loads(rv.data))
        all_60 = df['Hourly'] == 60
        assert all_60.all()

    def test_rolling(self):
        '''Test Rolling Sum'''
        truthy = to_df(self.data)
        truthy = truthy.resample('T', how='sum')
        truthy = truthy.rename(columns={'Events': 'Minutely'})
        rolling = pd.rolling_sum(truthy, 60, min_periods=0)

        send = {'freq': json.dumps({'T': 'Minutely'}),
                'data': json.dumps(self.data),
                'window': 60}
        rv = self.app.post('rolling_sum', data=send)
        df = single_df(json.loads(rv.data))

        pdtest.assert_frame_equal(df, rolling)

    def test_daily(self):
        '''Test daily summing'''
        send = {'data': json.dumps(self.data), 'how': json.dumps('sum')}
        rv = self.app.post('daily', data=send)
        df = single_df(json.loads(rv.data))
        all_1440 = df['Events'] == 1440
        assert all_1440.all()

    def test_hourly(self):
        '''Test hourly summing'''
        send = {'data': json.dumps(self.data), 'how': json.dumps('sum')}
        rv = self.app.post('hourly', data=send)
        rv_dict = json.loads(rv.data)
        df = pd.DataFrame({'Events': rv_dict['Events']['data']},
                          index=rv_dict['Events']['time'])
        all_420 = df['Events'] == 420
        assert all_420.all()

    def test_daily_hours(self):
        '''Test daily hour summing'''

        index = range(0, 24, 1)
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                'Saturday', 'Sunday']
        truthy = pd.DataFrame(60.0, columns=days, index=index)

        send = {'data': json.dumps(self.data), 'how': json.dumps('sum')}
        rv = self.app.post('daily_hours', data=send)
        df = multi_df(json.loads(rv.data))
        df = df.reindex(columns=days)

        pdtest.assert_frame_equal(df, truthy)

    def test_forward(self):
        '''Test forward predicting'''

        rng = pd.date_range('6/23/2013', periods=180, freq='H')
        truthy = pd.DataFrame({'Events': 60.0}, index=rng)

        send = {'data': json.dumps(self.data), 'periods': json.dumps(180),
                'how': json.dumps('sum')}
        rv = self.app.post('forward', data=send)
        df = single_df(json.loads(rv.data))

        pdtest.assert_frame_equal(df, truthy)








