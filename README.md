#Mcflyin

###A timeseries transformation API built on Pandas and Flask

This is a small demo of an API to do timeseries transformations built on Flask and Pandas.

Concept
-------

The idea is that you can make a POST request to the API with a simple list/array of timestamps, from any language, and get back some interesting transformations of that data.

Why?
----

Partly to show how straightforward it is to build such a thing. Python is great because it has very powerful, intuitive, quick-to-learn tools for both building web applications and doing data analysis/statistics.

That puts Python in kind of a unique position: powerful web tools, powerful scientific/numerical/statistical data tools. This API is a very simple example of how you can take advantage of both. Go read the source code- it's short and easy to grok. Bug fixes and pull requests welcome. 

Getting Started
---------------

First we need to find some data. We're going to use some data that Wes McKinney provided in a recent [blog post](http://wesmckinney.com/blog/?p=687), with some statistics on Python posts on Stack Overflow. This is something of a contrived example: I'm manipulating the data in Python, sending to a Python backend, and then getting a response to manipulate in Python. Just know that all you need is an array of timestamp strings, no matter your language.

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

With the McFlyin application running on localhost, lets make a request to resample the data on an daily basis, to get the number of posts per day:

```python
import requests
import json

freq = {'D': 'Daily'}
sends = {'freq': json.dumps(freq), 'data': json.dumps(data)}
r = requests.post('http://127.0.0.1:5000/resample', data=sends)
response = r.json
```

The response is simple JSON:
```js
{'Monthly': {'data': [1.0, 2.0, 1.0, 1.0,...
             'time': ['2011-03-31T00:00:00', '2011-04-30T00:00:00', '2011-05-31T00:00:00', '2011-06-30T00:00:00', '2011-07-31T00:00:00',...
```

Here's the distribution of daily questions on Stack Overflow for Pandas (monthly probably would have been a little more informative):

![Daily](http://farm6.staticflickr.com/5497/9062972730_aa34df95a2_o.jpg)

Let's call Mcflyin for a rolling sum on a seven-day window. It will resample to the given ```freq```, then apply the window to the result:

```python
freq = {'D': 'Weekly Rolling'}
sends = {'freq': json.dumps(freq), 'data': json.dumps(data), 'window': 7}
r = requests.post('http://127.0.0.1:5000/rolling_sum', data=sends)
response = r.json
```

![Rolling](http://farm4.staticflickr.com/3682/9060743479_2962e61881_o.jpg)

Let's look at the total questions asked by day:

```python
sends = {'data': json.dumps(data), 'how': json.dumps('sum')}
r = requests.post('http://127.0.0.1:5000/daily', data=sends)
response = r.json
```
![dailysum](http://farm3.staticflickr.com/2838/9064294004_200b81b303_o.jpg)

and daily means:

```python
sends = {'data': json.dumps(data), 'how': json.dumps('mean')}
r = requests.post('http://127.0.0.1:5000/daily', data=sends)
response = r.json
```
![dailymean](http://farm4.staticflickr.com/3786/9064294028_c8bf17fa09_o.jpg)

The same for hourly:

```python
sends = {'data': json.dumps(data), 'how': json.dumps('sum')}
r = requests.post('http://127.0.0.1:5000/hourly', data=sends)
response = r.json
```
![dailymean](http://farm4.staticflickr.com/3814/9062065097_75d871a7bc_o.jpg)

Finally, we can look at hourly by day-of-week:

```python
sends = {'data': json.dumps(data), 'how': json.dumps('sum')}
r = requests.post('http://127.0.0.1:5000/daily_hours', data=sends)
response = r.json
```
![hourdow](http://farm3.staticflickr.com/2838/9064294126_6036e724ba_o.jpg)

Live demo [here](http://bl.ocks.org/wrobstory/5794343)

Dependencies
------------
Pandas, Numpy, Requests, Flask

How did you make those colorful graphs?
--------------------------------------
[Vincent](https://github.com/wrobstory/vincent) and [Bearcart](https://github.com/wrobstory/bearcart)

Status
------
Lots of stuff that could be better- error handling on the requests, probably better handling of weird timestamps,
etc. This is just a small demo of how powerful Python can be for building a statistics backend with relatively few lines of code.  

If I want to write a front-end in a different language, can I put it in the examples folder?
---------
Yes! PR's welcome. 


