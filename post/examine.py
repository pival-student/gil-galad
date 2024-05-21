import pandas as pd
from tqdm import tqdm
import re
from collections import Counter

hdf = pd.read_pickle('hits_joined.zip')
m = hdf['source'] == 'twitter'
thdf = hdf[m]
sdf = pd.read_pickle('samples.zip')
m = sdf['source'] == 'twitter'
tsdf = sdf[m]

print(tsdf[:5].to_string())
print(thdf[:5].to_string())

# print(f'Loaded hits')
# found = []
# for type, form in tqdm(zip(hdf['type'], hdf['original'])):
#     if type == 'star_pl' or type == 'star_sg':
#         if re.search(r'[^A-Za-zÄÖÜäöüß-]', form):
#             found.append('symbol')
#         elif re.search(r'[a-zäöüß]I', form):
#             found.append('binnen')
#         else:
#             found.append('genfem')
#     elif type == 'in_form_pl' or type == 'in_form_sg':
#         if re.search(r'[^A-Za-zÄÖÜäöüß-]', form):
#             found.append('symbol')
#         elif re.search(r'[a-zäöüß]I', form):
#             found.append('binnen')
#         else:
#             found.append('genfem')
#     else:
#         found.append(type)
#
# print(Counter(found).most_common(20))

# m = hdf['action'] == 'male contains special chars'
# m = hdf['action'] == 'special char out of place'
# m = hdf['action'] == 'contains repeating special chars'
# m = hdf['type'] == 'in exclusion list'
# mdf = hdf[m]
#
# print(mdf[['male', 'original', 'type']])
# print(mdf['sample_id'])

# s = hdf['action'] == 'special char out of place'
# sdf = hdf[s]
#
# print(sdf['original'])
# print(sdf['sample_id'])