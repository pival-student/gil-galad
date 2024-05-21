import pandas as pd


def upd(x, prefix):
    return f'{prefix}{int(x):05d}'


s1 = pd.read_pickle('ep_samples.zip')
s2 = pd.read_pickle('twitter_samples.zip')
s3 = pd.read_pickle('wortschatz_leipzig_samples.pickle')
s4 = pd.read_pickle('diss_samples.zip')
s5 = pd.read_pickle('apuz_samples.zip')

newids = [upd(x, 'wl_') for x in s3['id']]
s3['id'] = newids

newids2 = [f'ds_{x}' for x in s4['id']]
s4['id'] = newids2


print(len(s3))
print(s3['id'][:5])

print(len(s4))
print(s4['id'][:5])

sdf = pd.concat([s1, s2, s3, s4, s5], ignore_index=True)
print(f'Samples: {len(sdf)}')
sdf.rename(columns={'id': 'sample_id'}, inplace=True)
sdf.to_pickle('samples.zip')

h1 = pd.read_pickle('ep_hits.zip')
h2 = pd.read_pickle('twitter_hits.zip')
h3 = pd.read_pickle('wortschatz_leipzig_hits.pickle')
h4 = pd.read_pickle('diss_hits.zip')
h5 = pd.read_pickle('apuz_hits.zip')

newids = [upd(x, 'wl_') for x in h3['sample_id']]
h3['sample_id'] = newids

newids = [f'ds_{x}' for x in h4['sample_id']]
h4['sample_id'] = newids

hdf = pd.concat([h1, h2, h3, h4, h5], ignore_index=True)
print(f'Hits: {len(hdf)}')
hdf.to_pickle('hits.zip')
