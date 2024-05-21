import pandas as pd
import time
from collections import Counter

s = pd.read_pickle('samples.zip')
h = pd.read_pickle('hits.zip')
print(f'Loaded {len(h)} hits')

keep_mask = h['action'] == 'keep'
keep_hits = h[keep_mask]
keep_hits.to_pickle('hits_filtered.zip')
print(f'Keeping {len(keep_hits)} hits')

kick_mask = h['action'] != 'keep'
kicked_hits = h[kick_mask]
t = time.time()
kicked_hits.to_pickle(f'kicked_{t}.zip')
print(f'Discarding {len(kicked_hits)} hits')
print('Joining data..')

x = s[['sample_id', 'source', 'author', 'year', 'month', 'day']]

newh = pd.merge(keep_hits, x, on='sample_id', how='left')
newh.dropna(subset='type')
newh.drop_duplicates()
newh.to_pickle('hits_joined.zip')


# h = pd.read_pickle('hits_joined.zip')
# print(h.dtypes)
# print(len(h))

# s = pd.read_pickle('samples.zip')
# s.drop_duplicates(inplace=True)
# print(Counter(s['sample_id']).most_common(100))

# m = s['sample_id'] == 'tw_000001'
# print(s[m].to_string())

# m = s['author'] == 'Barón Crespo'
# print(s[m].to_string())