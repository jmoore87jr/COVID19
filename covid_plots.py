# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 17:03:41 2020

@author: base_
"""
# to-do:
# function to create a snapshot table:
#  daily positive cases per capita
#  daily positive cases
#  hospitalized currently
#  hospital bed capacity
#  daily deaths
# factor in daily tests given for daily positives for states
# automatically generate list of 5 states with fastest growing daily positives last 10 days
# automatically generate list of 5 states with most daily positives per capita
# why won't matrix flip work on us df?
# break up into modules for getting data and plotting
# other ways to make charts prettier and cooler?

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def get_fastest_growing():
    """returns a DataFrame of raw daily positives, per 100,000 daily positives,
    and 7 day growth rate for each state"""
    # sort by % change in the rolling average for the last 7 days
    df = get_state_data()
    df = df[['date', 'state', 'raw_ra_daily_positives', 'ra_daily_positives',
             'ra_pos_rate', 'ra_daily_test_results']]
    # separate by state and calculate rate of growth of cases
    states = [state for state in df['state'].unique()]
    rates, pc_pos, raw_pos, pos_rate, tests = [], [], [], [], []
    for state in states:
        temp = df[df['state'] == state]
        rates.append((temp['ra_daily_positives'].iloc[-1] /
                      temp['ra_daily_positives'].iloc[-7]) - 1)
        pc_pos.append(temp['ra_daily_positives'].iloc[-1])
        raw_pos.append(temp['raw_ra_daily_positives'].iloc[-1])
        pos_rate.append(temp['ra_pos_rate'].iloc[-1])
        tests.append(temp['ra_daily_test_results'].iloc[-1])
    fg = pd.DataFrame({'state': states, 'raw_positives': raw_pos,
                       'positives/100k': pc_pos, 'tests/100k': tests,
                       'pos_rate': pos_rate, 'pos_rate_7d_growth': rates})
    return fg.sort_values('positives/100k', ascending=False)
def get_pc_most_positives():
    """returns a list of 5 states with the most cases"""
    pass

def get_us_data():
    # import USA daily tracking data
    df = pd.read_csv("https://covidtracking.com/api/v1/us/daily.csv")
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    df = df.rename(columns={'positive':'total_positives',
                            'positiveIncrease':'daily_positives',
                            'deathIncrease':'daily_deaths',
                            'totalTestResults':'total_test_results',
                            'totalTestResultsIncrease':'daily_test_results',
                            'hospitalizedCurrently':'hospitalized_currently',
                            'onVentilatorCurrently':'on_ventilator_currently'})
    # delete feb data - nothing really starts till march in USA
    df = df[:104]
    # create pos_rate and rolling average columns
    df['pos_rate'] = (df['daily_positives'] / df['daily_test_results']) * 100
    ra_cols = ['total_positives', 'daily_positives', 'death', 'daily_deaths',
               'total_test_results', 'daily_test_results',
               'pos_rate', 'hospitalized_currently']
    for col in ra_cols:
        colname = "ra_{}".format(col)
        df[colname] = df[col].rolling(window=7).mean()
    return df

def get_state_data(state=None):
    # import USA daily tracking data
    df = pd.read_csv("https://covidtracking.com/api/v1/states/daily.csv")
    if state:
        df = df[df['state'] == state]
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    # flip dataframe by rows to get rolling averages to behave
    df = df.sort_index(axis=1)
    df = df.iloc[::-1]
    df = df.rename(columns={'positive':'total_positives',
                            'positiveIncrease':'daily_positives',
                            'deathIncrease':'daily_deaths',
                            'totalTestResults':'total_test_results',
                            'totalTestResultsIncrease':'daily_test_results',
                            'hospitalizedCurrently':'hospitalized_currently',
                            'onVentilatorCurrently':'on_ventilator_currently'})
    df['pos_rate'] = (df['daily_positives'] / df['daily_test_results']) * 100
    # change errant AZ pos rate
    df['pos_rate'][(df['state'] == 'AZ') & (df['date'] == '2020-06-12')] = 18
    # import state populations (taken from June 1, 2019 US census)
    # the csv is in github repo
    pops = pd.read_csv("C:/Users/john/Anaconda3/Scripts/covid19/state_pops.csv")
    pd.to_numeric(pops['Population'])
    # add 'Population' column to df
    df = pd.merge(df, pops, left_on='state', right_on='State')
    # create per capita columns
    pc_cols = ['total_positives', 'daily_positives', 'death', 'daily_deaths',
               'total_test_results', 'daily_test_results', 'hospitalized_currently']
    for col in pc_cols:
        colname = "pc_{}".format(col)
        df[colname] = (df[col] / (df['Population'] / 100000))
    # create rolling average columns
    ra_cols = ['total_positives', 'daily_positives', 'death', 'daily_deaths',
               'total_test_results', 'daily_test_results', 'hospitalized_currently']
    for col in ra_cols:
        colname = "ra_{}".format(col)
        df[colname] = (df[col].rolling(window=7).mean()) / (df['Population'] / 100000)
    df['ra_pos_rate'] = df['pos_rate'].rolling(window=7).mean()
    df['raw_ra_daily_positives'] = df['daily_positives'].rolling(window=7).mean()
    return df

def plot_state(*args, x='date', y='ra_daily_positives', days=0, type='ra'):
    """*args are 2 letter state abbreviations"""
    df = get_state_data()
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.autofmt_xdate()
    ax.fmt_xdata = mdates.DateFormatter('%m-%d')
    for state in args:
        plot_data = df[df['State'] == state]
        plot_data = plot_data[6:] # for rolling average
        if days > 0:
            plot_data = plot_data[-1*days:]
        ax.plot(plot_data[x], plot_data[y][plot_data['State'] == state],
        linestyle='-', label=state)
        ax.grid()
    fig.text(0.15, 0.86, 'data source: covidtracking.com', fontsize=11, color='gray')
    if(type == 'pc'):
        ax.set_title("{} per 100,000 people".format(y))
    elif (type == 'ra'):
        ax.set_title("7 day rolling average {} per 100,000 people".format(y))
    else:
        ax.set_title(y)
    ax.yaxis.grid(True)
    ax.legend()
    plt.style.use('seaborn')
    plt.show()

def plot_us(*args, x='date', days=0):
    """*args are column names from the USA COVID-19 dataframe (df).
    Each arg is plotted against x, which defaults to 'date'
    Use df.info() to see column names"""
    df = get_us_data()
    # unpack args (stored in tuple) to list form
    a = []
    a.append(x)
    for arg in args:
        a.append(arg)
    plot_data = df[a].dropna()
    if days > 0:
        plot_data = plot_data[-1*days:]
    fig, ax = plt.subplots(nrows=len(args), ncols=1, figsize=(9,9))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.text(0.7, 0.07, 'data source: covidtracking.com', fontsize=11, color='gray')
    for i in range(len(args)):
        ax[i].fmt_xdata = mdates.DateFormatter('%m-%d')
        ax[i].plot(plot_data[x], plot_data[args[i]], color='b', linestyle='-', label='USA')
        ax[i].set_yticklabels(['{:,}'.format(int(x)) for x in ax[i].get_yticks().tolist()])
        ax[i].set_title(args[i])
        ax[i].grid()
        ax[i].legend()
    plt.style.use('seaborn')
    plt.show()

def plot_posrate(region='USA', x='date', days=0):
    if region == 'USA':
        df = get_us_data()
    else:
        df = get_state_data(state=region)
    plot_data = df[['date', 'ra_pos_rate', 'daily_test_results', 'daily_positives']].dropna()
    if days > 0:
        plot_data = plot_data[-1*days:]
    fig, ax1 = plt.subplots(nrows=1, ncols=1, figsize=(8,8))
    ax2 = ax1.twinx()
    fig.autofmt_xdate()
    ax1.fmt_xdata = mdates.DateFormatter('%m-%d')
    fig.tight_layout()
    fig.text(0.07, 0.95, 'data source: covidtracking.com', fontsize=11, color='lightgray')
    # plots
    ax1.bar(plot_data[x], plot_data['daily_test_results'], color='navajowhite', label='Daily tests')
    ax1.bar(plot_data[x], plot_data['daily_positives'], color='tan', label='Daily positive tests')
    ax2.plot(plot_data[x], plot_data['ra_pos_rate'], color='tab:brown', linestyle='-', label='% Positive tests')
    ax1.set_ylabel('Daily test results')
    ax2.set_ylabel('Positive test % (7-day average)')
    ax1.legend(loc='upper right')
    ax2.legend(bbox_to_anchor=(0.977,0.93))
    # format axis
    ax1.yaxis.grid(True)
    ax1.set_yticklabels(['{:,}'.format(int(x)) for x in ax1.get_yticks().tolist()])
    plt.style.use('seaborn')
    plt.title('{} Daily Test Results and Positive Test Rate'.format(region))
    plt.savefig("C:/Users/john/Pictures/covid_charts/posrate_{}.png".format(region), bbox_inches='tight')
    plt.show()

def plot_redblue(party, x='date', y='daily_positives', days=0):
    """plot states with red or blue governors"""
    df = get_state_data()
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.autofmt_xdate()
    ax.fmt_xdata = mdates.DateFormatter('%m-%d')
    df = df[df['Governor'] == party]
    if party == 'republican':
        df = df[3:]
        color = 'red'
    if party == 'democrat':
        df = df[36:]
        color = 'blue'
    df = df[['date', 'state', 'daily_positives']].dropna()
    grouper = df.groupby(x)[y].sum()
    print(grouper.tail())
    if days > 0:
        plot_data = plot_data[-1*days:]
    ax.plot(df[x].unique(), grouper, linestyle='-', label=party, color=color)
    ax.grid()
    fig.text(0.15, 0.86, 'data source: covidtracking.com', fontsize=11, color='gray')
    ax.set_title("{} States {}".format(party.title(), y))
    ax.yaxis.grid(True)
    plt.style.use('seaborn')
    plt.show()

#d = get_state_data(state='LA')
#d = d[['state', 'date', 'daily_positives', 'ra_daily_positives', 'ra_daily_test_results', 'pos_rate']]
#print(d.tail(7))
c = get_fastest_growing()
print(c)
#plot_us('ra_daily_positives', 'ra_daily_test_results', 'ra_hospitalized_currently', 'ra_daily_deaths')
#plot_posrate()
#plot_state('TX', 'GA', 'CA', 'FL', 'AZ', 'SC', 'NY')
#plot_redblue('democrat')
#plot_redblue('republican')
plot_redblue('democrat')
