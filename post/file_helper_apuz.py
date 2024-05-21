import re
import os
import json
from types import SimpleNamespace as Namespace
from datetime import datetime, timezone
from tqdm import tqdm
from regex_helper import find_hits_with_indices
import pandas as pd


def hit_examples(s, hit_dict):
    for hit in s['hits']:
        label = hit['label']
        if label not in hit_dict:
            hit_dict[label] = {}
        fem = hit['female']
        if fem not in hit_dict[label]:
            hit_dict[label][fem] = re.sub('\r?\n', '', s['text'])
    pass


def setup_dfs(s, h):
    samples = pd.DataFrame(data=s, columns=['id', 'text', 'source', 'author', 'day', 'month', 'year', 'location'])
    hits = pd.DataFrame(data=h, columns=['sample_id', 'start', 'end', 'type', 'original', 'male', 'female'])
    return samples, hits


if __name__ == '__main__':

    exclude = []
    with open('C:\\Users\\Valentin\\PycharmProjects\\DE_gender_project\\filter_tool\\all_exclude.txt', 'r',
              encoding='utf-8') as exf:
        for line in exf:
            exclude.append(line.strip().casefold())
    exclude = list(set(exclude))
    print(f'Excluding {len(exclude)} items')
    with open('C:\\Users\\Valentin\\PycharmProjects\\DE_gender_project\\filter_tool\\all_exclude.txt', 'w',
              encoding='utf-8') as exf:
        for x in sorted(exclude):
            exf.write(f'{x}\n')

    sa = []
    h = []
    indf = pd.read_pickle('apuz-valentin.zip')
    print(f'Found {len(indf)} samples\n')
    for idx, row in tqdm(indf.iterrows(), desc=f'Processing samples..'):
        txt = re.sub(r'[\r\n\s]+', ' ', row['Text'])
        sa.append([row['ID'], txt, 'apuz', row['Author'], row['Day'], row['Month'], row['Year'], 'na'])
        for hit in find_hits_with_indices(txt, excluded=exclude, skip_labels=['nde_form', 'kraft_form', 'Person/Mensch']):
            h.append([row['ID'], hit['start'], hit['end'], hit['label'], hit['full'], hit['male'], hit['female']])
    samp, hts = setup_dfs(sa, h)
    print(len(samp))
    print(samp[:5])
    print(len(hts))
    print(hts[:5])
    samp.to_pickle('apuz_samples.zip')
    hts.to_pickle('apuz_hits.zip')
