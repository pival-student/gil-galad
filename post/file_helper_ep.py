import re
import os
import json
from regex_helper import find_hits_with_indices, load_and_filter_excl, norm_text
from tqdm import tqdm
import pandas as pd


def get_files(directory):
    dir = os.fsencode(directory)
    for file in os.listdir(dir):
        filename = os.fsdecode(file)
        if re.match(r'all_\d*\.txt', filename):
            yield os.path.abspath(os.path.join(directory, filename))
    pass


def get_sample_files(directory):
    dir = os.fsencode(directory)
    for file in os.listdir(dir):
        filename = os.fsdecode(file)
        if re.match(r'samples.*\.txt', filename):
            yield os.path.abspath(os.path.join(directory, filename))
    pass


def get_samples_legacy(file):
    with open(file, 'r', encoding='utf-8') as inf:
        sample = None
        text = []
        for line in inf:
            if line.startswith('<ep-'):
                if sample:
                    sample['text'] = norm_text(' '.join(text))
                    text = []
                    yield sample
                sid, speaker, chapter, fragment, day, month, year = parse_meta(line.strip())
                sample = {
                    'id': sid,
                    'day': day,
                    'month': month,
                    'year': year,
                    'author': speaker,
                    'source': 'europarl',
                    'location': 'na'
                }
            else:
                text.append(line.strip())
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


def parse_meta(s):
    split0 = s.split('> <')
    sid = split0[0][1:].replace('-', '_')
    first = split0[0][4:]
    speaker = split0[1][:-1]
    split1 = first.split('_')
    chapter = split1[1]
    fragment = split1[2]
    date = split1[0].split('-')
    day = date[2]
    month = date[1]
    year = f'19{date[0]}' if int(date[0]) > 25 else f'20{date[0]}'
    return sid, speaker, chapter, fragment, day, month, year


def setup_dfs(s, h):
    samples = pd.DataFrame(data=s,
                           columns=['id', 'text', 'source', 'author', 'day', 'month', 'year', 'location'])
    hits = pd.DataFrame(data=h, columns=['sample_id', 'start', 'end', 'type', 'original', 'male', 'female'])
    return samples, hits


if __name__ == '__main__':
    excl = load_and_filter_excl(r'C:\Users\Valentin\PycharmProjects\DE_gender_project\iterative\exclude.txt')
    spath = r'C:\Users\Valentin\PycharmProjects\DE_gender_project\data\Europarl\samples'

    s = []
    h = []
    for sf in get_sample_files(spath):
        for sample in tqdm(get_samples(sf), desc=sf):
            s.append([sample['id'], sample['text'], sample['source'],
                     sample['author'], sample['day'], sample['month'],
                     sample['year'], sample['location']])
            for hit in find_hits_with_indices(sample['text'], excluded=excl,
                                              skip_labels=['nde_form', 'kraft_form', 'Person/Mensch']):
                h.append([sample['id'], hit['start'], hit['end'], hit['label'],
                          hit['full'], hit['male'], hit['female']])
    samp, hts = setup_dfs(s, h)
    print(len(samp))
    print(samp[:1].to_string())
    print(len(hts))
    print(hts[:1].to_string())
    samp.to_pickle('ep_samples.zip')
    hts.to_pickle('ep_hits.zip')
    pass
