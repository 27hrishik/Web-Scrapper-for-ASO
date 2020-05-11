import pandas as pd

# creating keywords data frame
keywords_df = pd.read_csv('ios/current-keywords.csv',index_col=[0])
keywords_df['TRAFFIC'] = keywords_df['TRAFFIC']/10
keywords_df['DIFFICULTY'] = keywords_df['DIFFICULTY']/10
keywords_df['SCORE'] = keywords_df['TRAFFIC'] ** 0.5 * (1 - keywords_df['DIFFICULTY']) ** 0.5 * 100
temp = keywords_df.sort_values(by=['SCORE'],ascending=False)
temp.to_csv('ios/current-keywords.csv')
