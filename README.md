#Mcflyin

###A timeseries transformation API built on Pandas and Flask

This is a small demo of an API to do timeseries transformations build on Flask and Pandas.

Concept
-------

The idea is that you can make a POST request to the API with a simple list/array of timestamps, from any language, and get back some interesting transformations of that data.

Why
---

Partly to show how straightforward it is to build such a thing. Python is great because it has very powerful, intuitive, quick-to-learn tools for both building web applications and doing data analysis/statistics.

That puts Python in kind of a unique position: powerful web tools, powerful scientific/numerical/statistical data tools. This API is a very simple example of how you can take advantage of both. Go read the source code- it's short and easy to grok.

Getting Started
---------------

First we need to find some data. We're going to use some data that Wes McKinney provided in a recent ![blog post](http://wesmckinney.com/blog/?p=687), with some statistics on Python posts on Stack Overflow. This is something of a contrived example: I'm manipulating the data in Python, sending to a Python backend, and then getting a response to manipulate in Python. Just know that all you need is an array of timestamp strings, no matter your language.

```python
import pandas as pd

data = pd.read_csv('AllPandas.csv')
data = data['CreationDate'].tolist()
```

A simple array of timestamps:

```python
>>>data[:10]
['2011-04-01 14:50:44',
 '2012-01-18 19:41:27',
 '2012-01-23 03:21:00',
 '2012-01-24 17:59:53',
 '2012-03-04 16:58:45',
 '2012-03-09 22:36:52',
 '2012-03-10 15:35:26',
 '2012-03-18 12:53:06',
 '2012-03-30 13:58:29',
 '2012-04-04 23:17:23']
 ```

With mcflyin running on localhost, lets make a request to resample the data on an hourly basis, to get the number of posts per hour:

```python
import requests
import json

freq = {'M': 'Monthly'}
sends = {'freq': json.dumps(freq), 'data': json.dumps(data)}
r = requests.post('http://127.0.0.1:5000/resample', data=sends)
response = r.json
```

The response is simple JSON:
```json
{u'Monthly': {data': [1.0, 2.0, 1.0, 1.0,...
              time': [u'2011-03-31T00:00:00', '2011-04-30T00:00:00', '2011-05-31T00:00:00', '2011-06-30T00:00:00', '2011-07-31T00:00:00',...
```

Here's the distribution of daily questions on Stack Overflow for Pandas (monthly probably would have been a little more informative):

![Daily](http://farm6.staticflickr.com/5497/9062972730_aa34df95a2_o.jpg)

Let's call Mcflyin for a rolling sum on a seven-day window:

```python
freq = {'D': 'Daily'}
sends = {'freq': json.dumps(freq), 'data': json.dumps(data), 'window': 7}
r = requests.post('http://127.0.0.1:5000/rolling_sum', data=sends)
response = r.json
```

![Rolling](http://farm4.staticflickr.com/3682/9060743479_2962e61881_o.jpg)




