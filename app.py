import pandas as pd
import streamlit as st
import numpy as np

from streamlit.elements.widgets import selectbox

from logic import ipl
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px



import zipfile




obj = ipl()

df = obj.df
#df = pd.read_csv('IPL.csv.zip', low_memory=False)


def data_cleaning():

    df.dropna()
    df.replace('Kings XI Punjab', 'Punjab Kings', inplace=True)
    df.replace('Rising Pune Supergiant', 'Rising Pune Supergiants', inplace=True)
    df.replace('Royal Challengers Bangalore', 'Royal Challengers Bengaluru', inplace=True)
    df.replace('Delhi Daredevils', 'Delhi Capitals', inplace=True)


def line_plot(x,y,title1,df):
    d1 = [go.Scatter(x=df[x],y = df[y])]
    fig = go.Figure(d1,layout=go.Layout(title=title1))
    st.plotly_chart(fig)

def pie_plot(labels,values,title1,df1):
    df1 = pd.DataFrame(df1)
    d2 = [go.Pie(values=df1[values], labels=df1[labels])]
    fig = go.Figure(data=d2, layout=go.Layout(title=title1))
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return st.plotly_chart(fig, width='stretch')

def bar_plot(x,y,title1,df1):
    df1 = pd.DataFrame(df1)
    trace  =go.Bar(x=df1[x],y=df1[y],

        )
    data = [trace]
    layout = go.Layout(title=title1)
    fig = go.Figure(data =data,layout=layout )
    return st.plotly_chart(fig)
data_cleaning()
st.sidebar.title("IPL Analyzer")


options = [
    'Batter Analysis',
    'Batter vs Bowler',
    'Bowler Analysis',
    'Team1 vs Team2'
]

batters = sorted(df['batter'].dropna().unique())
bowlers = sorted(df['bowler'].dropna().unique())

teams = sorted(df['batting_team'].unique())

available_options = st.sidebar.selectbox('Select', options)

single_player_options = [
    'Batter Analysis',

    'Bowler Analysis',

]





if available_options in single_player_options:

    players = sorted(set(batters + bowlers))

    name = st.selectbox('Select Player', players)
    btn = st.button('Start Analyzing')
    if btn:
        if available_options == 'Batter Analysis':
            runs,data = obj.batter_run_overall(name)
            if data is None:
                st.error("No Data Available")
            else:
                st.error
                st.write(runs)

                #batter year - year performance
                year_d= data.groupby('year')['runs_batter'].sum().reset_index()
                line_plot('year','runs_batter','{} year - year performance'.format(name),year_d)

                #batter wickets kind
                out = data[data['wicket_kind'].notna() ].reset_index()
                outs = out['wicket_kind'].unique()
                d = data[data['wicket_kind'].isin(outs)].value_counts(data['wicket_kind']).reset_index()
                pie_plot('wicket_kind', 'count','{} out type'.format(name), d)

                # played for how many teams
                d2 = data['batting_team'].unique()

                teams_played_for = d2.dropna().unique().tolist()
                st.write('Played for : \n')

                #POTM won by player
                st.write(teams_played_for)
                st.write('Player of the match won: {} POTM'.format(obj.count_player_of_the_match(name)))
                #batter vs all teams
                d3 = data.groupby('bowling_team')['runs_batter'].sum().reset_index()
                bar_plot('bowling_team', 'runs_batter', '{} Runs vs teams'.format(name), d3)


        elif available_options == 'Bowler Analysis':
            data,w = obj.bowler_overall_wicket(name)
            if data is None:
                st.error("No Data Available")
            else:
                #year-year wickets
                d1 = w.groupby('year')['ball_no'].count().reset_index()
                # Economy year-year

                d3 = data.groupby('year')['runs_bowler'].sum().reset_index()
                d4 = data.groupby('year')['over'].count().reset_index()
                eco = ((d3['runs_bowler'] * 6) / d4['over']).reset_index()


                trace1 = go.Scatter(x=d1['year'], y=eco[0],name='Economy')
                trace2 = go.Scatter(x=d1['year'], y=d1['ball_no'],name='Wickets')

                data1 = [trace1, trace2]
                fig = go.Figure(data=data1,layout=go.Layout(title='Economy and Wickets year - year'))
                st.plotly_chart(fig)

                #wicket type

                d2 = w.groupby('wicket_kind')['ball_no'].count().reset_index()
                pie_plot('wicket_kind','ball_no','{} wickets kind'.format(name),d2)

                #Teams played for
                d2 = data['bowling_team'].unique()
                teams_played_for = d2.dropna().unique().tolist()
                st.write('Played for : \n')
                st.write(teams_played_for)
                # POTM Count
                st.write('Player of the match won: {} POTM'.format(obj.count_player_of_the_match(name)))
                #wickets vs teams
                d3 = w.groupby('batting_team')['over'].count().reset_index()
                bar_plot('batting_team', 'over', '{} wickets vs teams'.format(name), d3)


else:

    if available_options == 'Batter vs Bowler':
        batter = st.selectbox('Select Batter', batters)
        bowler = st.selectbox('Select Bowler', bowlers)
        btn = st.button('Start Analyzing')
        if batter == bowler:
            st.write("Enter different players")
        else:

            data = obj.batter_vs_bowler(batter, bowler)
            if data is None:
                st.write("{} has not faced {}".format(batter, bowler))

            else:


                # runs each year
                d1 = data.groupby('year')['runs_batter'].sum().reset_index()


                #wickets
                d2 = data[(data['bowler_wicket'] == 1) & (data['valid_ball'] == 1)]
                d2 = d2.groupby('year')['over'].count().reset_index()

                #strike rate
                d3 = data.groupby('year')['runs_batter'].sum().reset_index()
                d4 = data.groupby('year')['over'].count().reset_index()
                d5 = data.groupby('year')['runs_bowler'].sum().reset_index()
                strike_rate = ((d3['runs_batter'] / d4['over']) * 100).reset_index()
                eco = ((d5['runs_bowler'] * 6) / d4['over']).reset_index()


                trace1 = go.Scatter(x=d2['year'], y=d2['over'], name='OUT',mode='markers')
                trace2 = go.Scatter(x=d1['year'], y=d1['runs_batter'], name='Total RUNS',mode='lines+markers')
                trace3 = go.Scatter(x=d1['year'], y= strike_rate[0],name = 'strike_rate',mode='lines+markers')
                trace4 = go.Scatter(x=d1['year'],y=eco[0],name='Economy',mode='lines+markers')
                data1 = [trace1, trace2,trace3,trace4]
                fig = go.Figure(data=data1, layout=go.Layout(title='{} vs {} Battle'.format(batter,bowler)))
                st.plotly_chart(fig)


    elif available_options == 'Team1 vs Team2':
        team1 = st.selectbox('Select team1', teams)
        team2 = st.selectbox('Select team2', teams)
        team1 = str(team1)
        team2 = str(team2)
        btn = st.button('Start Analyzing')
        if btn and team1 == team2:
            st.write("Enter different teams")
        if btn and team1 != team2:

            t1_c, t2_c ,data = obj.t1_vs_t2(team1, team2)
            st.write("{} ({}) - {} ({}) ".format(team1,t1_c,t2_c,team2))

            if data is None:
                st.error("No Data Available")
            else:
                #Head to Head Records
                d2 = [go.Pie(values=[t1_c,t2_c], labels=[team1,team2])]
                fig = go.Figure(data=d2, layout=go.Layout(title='{} vs {}'.format(team1,team2)))
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, width='stretch')

                data = data.drop_duplicates(['match_id'],keep='first')
                d = data.groupby(['batting_team', 'toss_decision', ])['match_won_by'].count()
                d = d.reset_index()
                fig = px.sunburst(d,path=['batting_team','toss_decision'],values='match_won_by',
                                  title='match_won_by bat first or bat second'
                                  )
                st.plotly_chart(fig, width='stretch')

                trophies = df.drop_duplicates(['year'], keep='last')
                trophies = trophies[trophies['year'] < 2026].reset_index()
                data1 = trophies[(trophies['match_won_by'] == team1) | (trophies['match_won_by'] == team2)]
                d1 = data1.groupby('match_won_by')['match_id'].count().reset_index()

                bar_plot(x='match_won_by',y='match_id',title1='Trophies won by {} and {}'.format(team1,team2),df1=d1)