# -*- coding: utf-8 -*-
'''

McFlyin API: A RESTish API for transforming time series data

'''
import json
import functools
import pandas as pd
import numpy as np
from flask import Flask, request
import requests
import pd_utils


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


@jsonify
def get_github(user='public'):
    '''Pull Github event data.

    Parameters
    ----------
    user: str, default Firehose
        Github username. Defaults to the global github stream

    Returns
    -------
    Pandas DataFrame of event timestamps

    '''

    if user == 'public':
        uri = 'https://api.github.com/events'
    else:
        uri = 'https://api.github.com/users/{0}/events'.format(user)
    response = requests.get(uri)

    timestamps = []
    for event in response.json:
        timestamps.append(event['created_at'])

    index = pd.to_datetime(timestamps)
    ones = np.ones(len(index))
    df = pd.DataFrame({'Event': ones}, index=index)
    return df


@jsonify
def minutes(data):
    '''Test for rolling minutes'''
    df = pd.DataFrame({'Check-in': np.ones(len(data))},
                      index=pd.to_datetime(data))
    minutes = pd_utils.resample(df, freq=[('T', 'Minutely')])['Minutely']
    rolling = pd.rolling_sum(minutes['Minutely'], 60, min_periods=0)
    resampled = rolling.resample('H', how='mean', closed='right')
    minutely = pd.DataFrame({'Rolling': resampled})
    return minutely

app = Flask(__name__)


@app.route('/')
def test():
    return 'test'


@app.route('/github/<username>', methods=['GET'])
def github(username):
    '''Return the last 30 github event timestamps'''
    if request.method == 'GET':
        return json.dumps(get_github(username))


@app.route('/minutes', methods=['POST'])
def minutes():
    '''Return rolling average of timestamps'''
    if request.method == 'POST':
        pass


if __name__ == '__main__':
    app.run(debug='True')
