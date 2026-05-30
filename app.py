import pickle

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from logic import ipl
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
    trace  =go.Bar(x=df1[x],y=df1[y],text=df1[y],textposition='auto')
    data = [trace]
    layout = go.Layout(title=title1)
    fig = go.Figure(data =data,layout=layout )
    return st.plotly_chart(fig)
data_cleaning()
st.sidebar.title("IPL Analyzer")
c_teams = [
        'Kolkata Knight Riders', 'Chennai Super Kings', 'Punjab Kings', 'Rajasthan Royals', 'Sunrisers Hyderabad',
        'Delhi Capitals', 'Lucknow Super Giants', 'Gujarat Titans', 'Royal Challengers Bengaluru', 'Mumbai Indians'
    ]
venue = ['Arun Jaitley Stadium',
 'Barabati Stadium',
 'Barsapara Cricket Stadium, Guwahati',
 'Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow',
 'Brabourne Stadium',
 'Buffalo Park',
 'De Beers Diamond Oval',
 'Dr DY Patil Sports Academy',
 'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium',
 'Dubai International Cricket Stadium',
 'Eden Gardens',
 'Green Park',
 'Himachal Pradesh Cricket Association Stadium',
 'Holkar Cricket Stadium',
 'JSCA International Stadium Complex',
 'Kingsmead',
 'M Chinnaswamy Stadium',
 'MA Chidambaram Stadium',
 'Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur',
 'Maharashtra Cricket Association Stadium',
 'Narendra Modi Stadium',
 'Nehru Stadium',
 'New Wanderers Stadium',
 'Newlands',
 'OUTsurance Oval',
 'Punjab Cricket Association IS Bindra Stadium',
 'Rajiv Gandhi International Stadium',
 'Saurashtra Cricket Association Stadium',
 'Sawai Mansingh Stadium',
 'Shaheed Veer Narayan Singh International Stadium',
 'Sharjah Cricket Stadium',
 'Sheikh Zayed Stadium',
 "St George's Park",
 'Subrata Roy Sahara Stadium',
 'SuperSport Park',
 'Vidarbha Cricket Association Stadium, Jamtha',
 'Wankhede Stadium',
 'Zayed Cricket Stadium, Abu Dhabi']

options = [
    'Batter Analysis',
    'Batter vs Bowler',
    'Bowler Analysis',
    'Team1 vs Team2'
]

batters = sorted(df['batter'].dropna().unique())
bowlers = sorted(df['bowler'].dropna().unique())

teams = sorted(df['batting_team'].unique())


single_player_options = [
    'Batter Analysis',

    'Bowler Analysis',

]


models = st.sidebar.selectbox('Select', ['WIN Predictor','Score Predictor','Data Analysis'])
if models == 'WIN Predictor':
    @st.cache_resource(show_spinner=False)
    def load_model():
        with open('LogisticRegression.pkl', 'rb') as f:
            return pickle.load(f)


    pipe = load_model()

    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox('Batting Team',sorted(c_teams))
    with col2:
        team2 = st.selectbox('Bowling Team',sorted(c_teams))

    if team1 == team2:
        st.error("Choose Different Teams")
    city = st.selectbox('Select Venue',sorted(venue))
    target = st.number_input('Target',step=1,min_value=0)
    col3, col4 ,col5,col6= st.columns(4)
    with col3:
        score = st.number_input('Score',step=1,min_value=0)
    with col4:
        overs = st.number_input('Overs Bowled',step=1,max_value=19,min_value=0)
    with col5:
        balls = st.number_input('Balls Bowled',step=1,max_value=6,min_value=1)
    with col6:
        wickets = st.number_input('Wickets',step=1,max_value=10,min_value=0)

    btn = st.button('Prediction Win % ')
    if btn:
        if team1 == team2:
            st.error("Choose Different Teams")
        elif target == 0:
            st.error("Target Score is 0")
        elif (target-1== score) & (overs == 19) & (balls == 6) :
            st.success("Match is tied")
        elif target <= score :
            st.success("Match is won by {}".format(team1))
        elif wickets == 10:
            st.success("Match is won by {}".format(team2))
        else:
            runs_left = target - score
            wickets_left = 10 - wickets
            balls_left = (120 - (overs * 6) - balls)
            crr =  (score * 6)/ (120 -balls_left)
            rrr = (runs_left*6) / balls_left

            data = pd.DataFrame(
                {
                    'batting_team':[team1],
                    'bowling_team':[team2],
                    'venue':[city],
                    'target score':[target],
                    'Runs Remaining':[runs_left],
                    'balls remaining':[balls_left],
                    'wickets_left':[wickets_left],
                    'crr':[crr],
                    'rrr':[rrr]
                 }
            )

            result = pipe.predict_proba(data)
            if rrr > 36:
                st.success("Match is won by {}".format(team1))
            else:
                st.write("{}- {}%".format(team1,round(result[0][1] *100,2) ))
                st.write("{}- {}%".format(team2, round(result[0][0] * 100,2) ))
elif models == 'Score Predictor':
    @st.cache_data(show_spinner=False)
    def load_model():
        zip_path = 'randomforestregressor_predictscore.zip'
        filename = 'randomforestregressor_predictscore.pkl'

        with zipfile.ZipFile(zip_path, 'r') as z:
            with z.open(filename) as f:
                df = pickle.load(f)

        return df
    pipe = load_model()
    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox('Batting Team',sorted(c_teams))
    with col2:
        team2 = st.selectbox('Bowling Team',sorted(c_teams))
    venue = st.selectbox('Select Venue',sorted(venue))
    col3, col4 ,col5,col6= st.columns(4)
    with col3:
        score = st.number_input('Score',step=1,min_value=0)
    with col4:
        overs = st.number_input('Overs Bowled',step=1,max_value=19,min_value=0)
    with col5:
        balls = st.number_input('Balls Bowled',step=1,max_value=6,min_value=0)
    with col6:
        wickets = st.number_input('Wickets',step=1,max_value=10,min_value=0)
    balls_bowled = (overs*6) +balls

    btn = st.button('Prediction  Score ')
    if btn:
        if team1 == team2:
            st.error("Choose Different Teams")
        elif (balls == 0)  & (overs == 0):
            st.error("At least one ball should be bowled in the match")
        else:
            data = pd.DataFrame({
                'bowling_team':[team2],
                'batting_team':[team1],
                'team_runs' :[score],
                'team_wicket':[wickets],
                'team_balls':[balls_bowled],
                'venue':[venue]
            })

            result = pipe.predict(data)
            st.subheader('Predicted Score : {} to {}'.format(int(result[0]),int(result[0])+10))
else:

    available_options = st.sidebar.selectbox('Select', options)
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
                    #phase wise runs
                    powerplay = data[data['over'] < 6]
                    middleovers = data[(data['over'] >= 6) & (data['over'] > 15)]
                    deathovers = data[(data['over'] >= 15) & (data['over'] < 20)]
                    powerplay_runs = powerplay.groupby('batter')['runs_batter'].sum().reset_index()
                    middleovers_runs =  middleovers.groupby('batter')['runs_batter'].sum().reset_index()
                    deathovers_runs =  deathovers.groupby('batter')['runs_batter'].sum().reset_index()
                    trace1 = go.Bar(x=powerplay_runs['batter'], y=powerplay_runs['runs_batter'],name='Powerplay',text=powerplay_runs['runs_batter'],textposition='auto',textfont_size=20)
                    trace2 = go.Bar(x=powerplay_runs['batter'], y=middleovers_runs['runs_batter'],name ='Middle overs',text=middleovers_runs['runs_batter'],textposition='auto',textfont_size=20)
                    trace3 = go.Bar(x=powerplay_runs['batter'], y=deathovers_runs['runs_batter'],name='Death overs',text=deathovers_runs['runs_batter'],textposition='auto',textfont_size=20)
                    data1 = [trace1,trace2,trace3]
                    layout = go.Layout(title='Phase wise Runs')
                    fig = go.Figure(data=data1, layout=layout)
                    st.plotly_chart(fig)

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

                    #phasewise wickets
                    powerplay = w[w['over'] < 6]
                    middleovers = w[(w['over'] >= 6) & (w['over'] < 15)]
                    deathovers = w[(w['over'] >= 15) & (w['over'] < 20)]
                    powerplay_runs = powerplay.groupby('bowler')['over'].count().reset_index()
                    middleovers_runs = middleovers.groupby('bowler')['over'].count().reset_index()
                    deathovers_runs = deathovers.groupby('bowler')['over'].count().reset_index()
                    trace1 = go.Bar(x=powerplay_runs['bowler'], y=powerplay_runs['over'], name='Powerplay',text=powerplay_runs['over'],textposition='auto',textfont_size=20)
                    trace2 = go.Bar(x=powerplay_runs['bowler'], y=middleovers_runs['over'], name='Middle overs',text=middleovers_runs['over'],textposition='auto',textfont_size=20)
                    trace3 = go.Bar(x=powerplay_runs['bowler'], y=deathovers_runs['over'], name='Death overs',text=deathovers_runs['over'],textposition='auto',textfont_size=20)
                    data1 = [trace1, trace2, trace3]
                    layout = go.Layout(title='Phase wise wickets',barmode='group')
                    fig = go.Figure(data=data1, layout=layout)
                    st.plotly_chart(fig)


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
            if team1 == team2:
                st.error("Choose Different Teams")
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

    text = st.chat_input("Enter feedback")

    if text:
        with open('feedback.txt','a') as f:
            f.write(text)
