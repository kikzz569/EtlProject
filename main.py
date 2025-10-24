import pandas as pd

from pandas_profiling import ProfileReport

df = pd.read_csv('data.csv')
profile = ProfileReport(df, title='Profiling Report')
profile.to_file("output.html")