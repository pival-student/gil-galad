import re
import os
import json
from tqdm import tqdm
import pandas as pd


def get_files(directory):
    dir = os.fsencode(directory)
    for file in os.listdir(dir):
        filename = os.fsdecode(file)
        if re.match(r'samples.*\.txt', filename):
            yield os.path.abspath(os.path.join(directory, filename))
    pass


def get_samples(file):
    with open(file, 'r', encoding='utf-8') as inf:
        for line in inf:
            try:
                content = json.loads(line.strip())
                yield content
            except json.JSONDecodeError:
                continue
    pass


def hit_examples(sample, hit_dict):
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
    # # redo hits
    # exclude = []
    # with open('C:\\Users\\Valentin\\PycharmProjects\\DE_gender_project\\filter_tool\\twitter\\exclude.txt', 'r', encoding='utf-8') as exf:
    #     for line in exf:
    #         exclude.append(line.strip().casefold())
    # dct = {}
    # din = r'C:\Users\Valentin\PycharmProjects\DE_gender_project\data\Twitter\data\out\run1'
    # dout = r'C:\Users\Valentin\PycharmProjects\DE_gender_project\data\Twitter\data\out\run2'
    # count = 0
    # for f in tqdm(get_files(din), desc=f'Processing files..'):
    #     count += 1
    #     with open(f'{dout}/samples_{count:03d}.txt', 'w', encoding='utf-8') as otf:
    #         for s in get_samples(f):
    #             s['hits'] = find_hits_with_indices(s['text'], exclude)
    #             otf.write(f'{json.dumps(s, ensure_ascii=False)}\n')
    # pass
    #
    #
    #
    # # extract unique hits for review
    # dct = {}
    # d = r'C:\Users\Valentin\PycharmProjects\DE_gender_project\data\Twitter\data\out\run2'
    # for f in get_files(d):
    #     for s in tqdm(get_samples(f), desc=f'Processing {f}'):
    #         hit_examples(s, dct)
    # for htype in dct.keys():
    #     with open(f'C:\\Users\\Valentin\\PycharmProjects\\DE_gender_project\\filter_tool\\twitter\\{htype}.txt', 'w', encoding='utf-8') as otf:
    #         for hit in dct[htype].keys():
    #             otf.write(f'{hit}\t{dct[htype][hit]}\n')
    #     pass

    # build dataframe
    d = r'C:\Users\Valentin\PycharmProjects\DE_gender_project\data\Twitter\data\out\run2'
    sa = []
    h = []
    c = 0
    for f in tqdm(get_files(d), desc=f'Processing files..'):
        for s in get_samples(f):
            sid = f'tw_{c:06d}'
            if len(s['hits']) > 0:
                sa.append([sid, s['text'], 'twitter', f'{s["name"]} (@{s["user"]})', s['day'], s['month'], s['year'], s['loc']])
                for hit in s['hits']:
                    h.append([sid, hit['start'], hit['end'], hit['label'], hit['full'], hit['male'], hit['female']])
                c += 1
    samp, hts = setup_dfs(sa, h)
    print(len(samp))
    print(samp[:5])
    print(len(hts))
    print(hts[:5])
    samp.to_pickle('./twitter_samples.zip')
    hts.to_pickle('./twitter_hits.zip')



