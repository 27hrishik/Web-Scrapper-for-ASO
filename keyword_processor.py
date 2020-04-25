import pandas as pd

# creating keywords data frame
keywords_df = pd.read_csv('common/traffic_and_difficulty.csv',index_col=[0])
keywords_df['TRAFFIC'] = keywords_df['TRAFFIC']
keywords_df['DIFFICULTY'] = keywords_df['DIFFICULTY']
keywords_df['SCORE'] = keywords_df['TRAFFIC'] ** 2 * (10 - keywords_df['DIFFICULTY']) ** 2 / 100
temp = keywords_df.sort_values(by=['SCORE'],ascending=False)
temp.to_csv('common/keywords_scored.csv',index=False)
