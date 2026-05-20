
import zipfile
import pandas as pd
import streamlit as st




@st.cache_data
def load_data():
    zip_path = 'Dataset.zip'
    csv_filename = 'IPL.csv'

    with zipfile.ZipFile(zip_path, 'r') as z:
        with z.open(csv_filename) as f:
            df = pd.read_csv(f, low_memory=False)

    return df
class ipl:
    def __init__(self):


        self.df = load_data()
        self.clean_data()


    def clean_data(self):
        self.df.dropna()
        self.df.replace('Kings XI Punjab', 'Punjab Kings', inplace=True)
        self.df.replace('Rising Pune Supergiant', 'Rising Pune Supergiants', inplace=True)
        self.df.replace('Royal Challengers Bangalore', 'Royal Challengers Bengaluru', inplace=True)
        self.df.replace('Delhi Daredevils', 'Delhi Capitals', inplace=True)

    def batter_run_overall(self,name):
        data = self.df.where(self.df['batter'] == name)
        if data['batter'].count() == 0:
            return "No batter run",data
        else:
            data = data[data['innings'].isin([1, 2])]
            runs = data.groupby('batter')['runs_batter'].sum()
            return runs,data

    def batter_vs_bowler(self,batter,bowler):
        batter = str(batter)
        bowler = str(bowler)
        m1 = self.df['batter'] == batter
        m2 = self.df['bowler'] == bowler
        data = self.df[m1 & m2]
        if data['match_id'].count() == 0:
            return None
        else:
            runs = data.groupby('batter')['runs_batter'].sum()
            w = data.where(data['bowler_wicket'] == 1)
            wicket = w['valid_ball'].count()
            balls = data['match_id'].count()
            strike_rate = (runs / balls ) * 100
            return data


    def bowler_overall_wicket(self,bowler):
        bowler = str(bowler)
        m1 = self.df['bowler'] == bowler
        data = self.df[m1]
        w = data.where((data['bowler_wicket'] == 1) &(data['valid_ball'] == 1))

        exclude_list = ['run out', 'retired hurt']


        w = w[~w['wicket_kind'].isin(exclude_list)]
        super_over= ['NaN']
        w = w[w['innings'].isin([1,2])]
        return data,w
    def count_player_of_the_match(self,player):
        data = self.df.where(self.df['player_of_match'] == player)
        count = data['match_id'].nunique()
        return count

    def t1_vs_t2(self, team1, team2):
        team1, team2 = str(team1), str(team2)

        data1 = self.df[
            ((self.df['batting_team'] == team1) & (self.df['bowling_team'] == team2)) |
            ((self.df['batting_team'] == team2) & (self.df['bowling_team'] == team1))
            ].copy()
        data2 = data1.drop_duplicates(['match_id'], keep='first')

        if data1.empty:
            return 0, 0 ,None


        win_counts = data2['match_won_by'].value_counts()

        team1_wins = int(win_counts.get(team1, 0))
        team2_wins = int(win_counts.get(team2, 0))

        return team1_wins, team2_wins,data1

