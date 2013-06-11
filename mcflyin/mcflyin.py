# -*- coding: utf-8 -*-
'''

McFlyin API: A RESTish API for transforming time series data

'''
import functools
import pandas as pd
import numpy as np
from flask import Flask
import requests


def jsonify(func):
    '''Type checking kludge until Pandas 11.1 ships with JSON support'''
    @functools.wraps(func)
    def wrapper():

        pass

        df = func()
        if isinstance(obj, str):
            return obj
        elif hasattr(obj, 'timetuple'):
            return str(obj)
        elif hasattr(obj, 'item'):
            return obj.item()
        elif hasattr(obj, '__float__'):
            return float(obj)
        elif hasattr(obj, '__int__'):
            return int(obj)
        else:
            raise LoadError('cannot serialize index of type '
                            + type(obj).__name__)


@jsonify()
def get_github():
    r = requests.get('https://api.github.com/users/wrobstory/events')
    timestamps = []
    for event in r.json():
        timestamps.append(event['created_at'])

    index = pd.to_datetime(timestamps)
    ones = np.ones(len(index))
    df = pd.DataFrame({'Event': ones}, index=index)
    return df


app = Flask(__name__)


@app.route('/mcflyin/', methods=['GET'])
@jsonify()
def fifteen():
    '''Return fifteen days of prediction'''
    if request.method == 'GET':
        return get_github()
