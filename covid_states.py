# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 17:03:41 2020

@author: base_
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# import USA daily tracking data
df = pd.read_csv("https://covidtracking.com/api/v1/states/daily.csv")
# df.isna().any() some columns contain NaN
# df.date.head() date is an int 'YYYYmmdd'
# change date to datetime
df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
# rename some columns
df = df.rename(columns={'positive':'total_positives', 
                        'positiveIncrease':'new_positives',
                        'deathIncrease':'new_deaths',
                        'totalTestResults':'total_test_results',
                        'totalTestResultsIncrease':'new_test_results',
                        'hospitalizedCurrently':'hospitalized_currently',
                        'onVentilatorCurrently':'on_ventilator_currently'})

# import state populations (taken from June 1, 2019 US census)
pops = pd.read_csv("C:/Users/base_/python_projects/covid19/state_pops.csv")
pd.to_numeric(pops['Population'])
# add 'Population' column to df
df = pd.merge(df, pops, left_on='state', right_on='State')
    
# create per capita columns
# df['pc_new_positives'] = df['new_positives'] / df['Population']
pc_cols = ['total_positives', 'new_positives', 'death', 'new_deaths', 
           'total_test_results', 'new_test_results', 'hospitalized_currently']
for col in pc_cols:
    colname = "pc_{}".format(col)
    df[colname] = (df[col] / (df['Population'] / 100000))

# to-do:
# combine with national level script
# push to github new branch with state and per capita ability
    
def plot_pc(*args, x='date', y='pc_new_positives', days=0):
    """*args are 2 letter state abbreviations"""
    # unpack args (stored in tuple) to list form
    a = []
    a.append(x)
    a.append(y)
    for arg in args:
        a.append(arg)
    # format dates
    if (days > 0) & (days < 32):
        locator = mdates.DayLocator()
        formatter = mdates.DateFormatter('%d')
    else:
        locator = mdates.MonthLocator()
        formatter = mdates.DateFormatter('%m-%d')
    # set up axes for subplots
    fig, ax = plt.subplots(figsize=(8, 8))
    # format dates on x-axis
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    for state in args:
        # subset df for our plots. dropna() ensures same date range for all plots
        plot_data = df[df['State'] == state]
        # subset for number of days
        if days > 0:
            plot_data = plot_data[:days+1]
        # make plot
        ax.plot(plot_data[x], plot_data[y][plot_data['State'] == state], linestyle='-', label=state)
    # set titles
    ax.set_title("{} per 100,000 people".format(y))
    #show legend
    ax.legend()
    
    
def plot_state(*args, x='date', state='CA', color='b', days=0):
    """*args are column names from the USA COVID-19 dataframe (df). 
    Each arg is plotted against x, which defaults to 'date'.
    'state' takes 2 letter capital abbreviation.
    Use df.info() to see column names"""
    # unpack args (stored in tuple) to list form
    a = []
    a.append(x)
    for arg in args:
        a.append(arg)
    # subset df for our plots. dropna() ensures same date range for all plots
    plot_data = df[df['state'] == state][a].dropna()
    # subset for number of days
    if days > 0:
        plot_data = plot_data[:days+1]
    # format dates
    locator = mdates.MonthLocator()
    formatter = mdates.DateFormatter('%m-%d')
    # set up axes for subplots
    fig, ax = plt.subplots(nrows=len(args), ncols=1, figsize=(8, 8))
    # for space between plots
    fig.tight_layout()
    if len(args) == 1:
        # remove comma
        args = ''.join(args)
        # format date on x-axis
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        ax.set_xlim(plot_data[x].iloc[-1], plot_data[x].iloc[0])
        # make plot
        ax.plot(plot_data[x], plot_data[args], color=color, linestyle='-')
        # set titles
        ax.set_title(args)
    else:
        for i in range(len(args)):
            # format date on x-axis
            ax[i].xaxis.set_major_locator(locator)
            ax[i].xaxis.set_major_formatter(formatter)
            ax[i].set_xlim(plot_data[x].iloc[-1], plot_data[x].iloc[0])
            # make plot
            ax[i].plot(plot_data[x], plot_data[args[i]], color=color, linestyle='-')
            # set titles
            ax[i].set_title(args[i])
    # style
    plt.style.use('ggplot')
    # show plots
    plt.show()

    