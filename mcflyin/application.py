# -*- coding: utf-8 -*-
'''

McFlyin App: A RESTish API for transforming time series data

'''
import json
import pandas as pd
import numpy as np
from flask import Flask, Response, request
import requests
import transformations as tr


@tr.jsonify
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

app = Flask(__name__)


@app.route('/github/<username>', methods=['GET'])
def github(username):
    '''Return the last 30 github event timestamps'''
    if request.method == 'GET':
        resp = Response(json.dumps(get_github(username)), status=200,
                        mimetype='application/json')
        return resp


@app.route('/resample', methods=['POST'])
def resample():
    '''Return a JSON of resampled event data'''
    if request.method == 'POST':
        data = json.loads(request.form['data'])
        freq = json.loads(request.form['freq'])
        df = tr.to_df(data)
        json_return = tr.resample(df=df, freq=freq)
        resp = Response(json.dumps(json_return), status=200,
                        mimetype='application/json')
        return resp


@app.route('/rolling_sum', methods=['POST'])
def rolling_sum():
    '''Return a JSON of rolling summed event data'''
    if request.method == 'POST':
        data = json.loads(request.form['data'])
        freq = json.loads(request.form['freq'])
        window = int(request.form['window'])
        df = tr.to_df(data)
        json_return = tr.rolling_sum(df=df, window=window, freq=freq)
        resp = Response(json.dumps(json_return), status=200,
                        mimetype='application/json')
        return resp


@app.route('/daily', methods=['POST'])
def daily():
    '''Return a JSON of daily summed event data'''
    if request.method == 'POST':
        data = json.loads(request.form['data'])
        how = json.loads(request.form['how'])
        df = tr.to_df(data)
        json_return = tr.daily(df=df, how=how)
        resp = Response(json.dumps(json_return), status=200,
                        mimetype='application/json')
        return resp


@app.route('/hourly', methods=['POST'])
def hourly():
    '''Return a JSON of hourly summed data'''
    if request.method == 'POST':
        data = json.loads(request.form['data'])
        how = json.loads(request.form['how'])
        df = tr.to_df(data)
        json_return = tr.hourly(df=df, how=how)
        resp = Response(json.dumps(json_return), status=200,
                        mimetype='application/json')
        return resp


@app.route('/daily_hours', methods=['POST'])
def daily_hours():
    '''Return a JSON of weekly event data by hour'''
    if request.method == 'POST':
        data = json.loads(request.form['data'])
        df = tr.to_df(data)
        json_return = tr.daily_hours(df=df, to_json=True)
        resp = Response(json.dumps(json_return), status=200,
                        mimetype='application/json')
        return resp


@app.route('/forward', methods=['POST'])
def forward():
    '''Return a JSON of a given number of hourly events'''
    if request.method == 'POST':
        data = json.loads(request.form['data'])
        periods = json.loads(request.form['periods'])
        df = tr.to_df(data)
        json_return = tr.forward(df=df, periods=periods)
        resp = Response(json.dumps(json_return), status=200,
                        mimetype='application/json')
        return resp


def run():
    '''Run the McFlyin API'''
    app.run()

if __name__ == '__main__':
    app.run()
