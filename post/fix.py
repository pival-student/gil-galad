import pandas as pd
from collections import Counter

s = pd.read_pickle('wortschatz_leipzig_samples.pickle')
s.drop_duplicates(inplace=True)
print(len(s))
print(s.dtypes)

print(s['id'])
print(Counter(s['id']).most_common(100))
