# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 17:03:41 2020

@author: base_
"""
# to-do:
# push to github new branch
# other ways to make charts prettier and cooler?

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def get_us_data():
    # import USA daily tracking data
    df = pd.read_csv("https://covidtracking.com/api/v1/us/daily.csv")
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
    # delete feb data - nothing really starts till march in USA
    df = df[:104]
    # create rolling average columns
    ra_cols = ['total_positives', 'new_positives', 'death', 'new_deaths',
               'total_test_results', 'new_test_results', 'hospitalized_currently']
    for col in ra_cols:
        colname = "ra_{}".format(col)
        df[colname] = df[col].rolling(window=7).mean()
    return df

def get_state_data():
    # import USA daily tracking data
    df = pd.read_csv("https://covidtracking.com/api/v1/states/daily.csv")
    # flip dataframe by rows for rolling averages
    df = df.sort_index(axis=1)
    df = df.iloc[::-1]
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
    # add pos rate
    df['pos_rate'] = df['new_positives'] / df['new_test_results']
    # change errant AZ pos rate
    df['pos_rate'][(df['state'] == 'AZ') & (df['date'] == '2020-06-12')] = 0.18
    # import state populations (taken from June 1, 2019 US census)
    pops = pd.read_csv("C:/Users/john/Anaconda3/Scripts/covid19/state_pops.csv")
    pd.to_numeric(pops['Population'])
    # add 'Population' column to df
    df = pd.merge(df, pops, left_on='state', right_on='State')
    # create per capita columns
    pc_cols = ['total_positives', 'new_positives', 'death', 'new_deaths',
               'total_test_results', 'new_test_results', 'hospitalized_currently']
    for col in pc_cols:
        colname = "pc_{}".format(col)
        df[colname] = (df[col] / (df['Population'] / 100000))
    # create rolling average columns
    ra_cols = ['total_positives', 'new_positives', 'death', 'new_deaths',
               'total_test_results', 'new_test_results', 'hospitalized_currently']
    for col in ra_cols:
        colname = "ra_{}".format(col)
        df[colname] = (df[col].rolling(window=7).mean()) / (df['Population'] / 100000)
    return df

def plot_state(*args, x='date', y='pc_new_positives', days=0, type='pc'):
    """*args are 2 letter state abbreviations"""
    # get data and create pc and ra columns
    df = get_state_data()
    # format dates
    if (days > 0) & (days < 32):
        locator, formatter = mdates.DayLocator(), mdates.DateFormatter('%d')
    else:
        locator, formatter = mdates.MonthLocator(), mdates.DateFormatter('%m-%d')
    # make plots and show
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    for state in args:
        plot_data = df[df['State'] == state]
        plot_data = plot_data[6:] # for rolling average
        if days > 0:
            plot_data = plot_data[days:]
        ax.plot(plot_data[x], plot_data[y][plot_data['State'] == state],
        linestyle='-', label=state)
    fig.text(0.15, 0.86, 'Data source: covidtracking.com', fontsize=11, color='gray')
    if(type == 'pc'):
        ax.set_title("{} per 100,000 people".format(y))
    elif (type == 'ra'):
        ax.set_title("7 day rolling average {} per 100,000 people".format(y))
    else:
        ax.set_title(y)
    ax.grid()
    ax.legend()
    plt.style.use('seaborn')
    plt.show()

def plot_us(*args, x='date'):
    """*args are column names from the USA COVID-19 dataframe (df).
    Each arg is plotted against x, which defaults to 'date'
    Use df.info() to see column names"""
    df = get_us_data()
    # unpack args (stored in tuple) to list form
    a = []
    a.append(x)
    for arg in args:
        a.append(arg)
    # subset df for our plots. dropna() ensures same date range for all plots
    plot_data = df[a].dropna()
    # format dates
    locator = mdates.MonthLocator()
    formatter = mdates.DateFormatter('%Y-%m-%d')
    # set up axes for subplots
    fig, ax = plt.subplots(nrows=len(args), ncols=1, figsize=(8, 8))
    # for space between plots
    fig.tight_layout()
    for i in range(len(args)):
        # format date on x-axis
        ax[i].xaxis.set_major_locator(locator)
        ax[i].xaxis.set_major_formatter(formatter)
        # make plot
        ax[i].plot(plot_data[x], plot_data[args[i]], color='b', linestyle='-')
        # set titles
        ax[i].set_title(args[i])
        ax[i].grid()
    # style
    plt.style.use('ggplot')
    # show plots
    plt.show()

#plot_state('NY', 'TX', 'AZ', 'FL', 'CA', y='ra_new_positives', type='ra')
#plot_state('NY', 'TX', 'AZ', 'FL', 'CA', y='ra_new_test_results', type='ra')
plot_us('ra_new_positives', 'ra_new_test_results')
