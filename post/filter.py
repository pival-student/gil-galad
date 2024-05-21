import re
import pandas as pd
from tqdm import tqdm
from collections import Counter

# define labeled exclusion patterns for hit subfields, 0 original, 1 male, 2 female

patterns = {
    # 'male contains special chars': (re.compile(r'[^a-zA-ZäöüÄÖÜß\-]'), [1]),  # allow only letters and hyphen
    'contains digits': (re.compile(r'\d'), [0, 1, 2]),
    'contains period': (re.compile(r'\.'), [0, 1, 2]),
    'contains quotes': (re.compile(r'[\'"\u201A\u2018\u2019\u201E\u201C\u201D]'), [0, 1, 2]),
    'contains repeating special chars': (re.compile(r'([^a-zA-ZäöüÄÖÜß])\1'), [0, 1, 2]),
    'special char out of place': (
        re.compile(r'[^a-zA-ZäöüÄÖÜß\-\s](?![iI])[a-zA-ZäöüÄÖÜß]'), [0, 1, 2])
    # followed by not i or special
}


def load_and_filter_excl(fpath):
    ex = []
    with open(fpath, 'r',
              encoding='utf-8') as exf:
        for line in exf:
            x = line.strip().casefold()
            skip = False
            for p in patterns:
                if re.search(patterns[p][0], x):
                  skip = True
                  break
            if not skip:
                ex.append(x)
    ex = list(set(ex))
    print(f'Loaded {len(ex)} exclusion items')
    with open(fpath, 'w',
              encoding='utf-8') as exf:
        for x in sorted(ex):
            exf.write(f'{x}\n')
    return ex


def check_hit(forms, exclude_list=[]):
    for exclude_reason in patterns.keys():
        (pattern, scope) = patterns[exclude_reason]
        for idx in scope:
            form = forms[idx]
            if not form or form == 'na' or len(form) == 0:
                continue
            if not isinstance(form, str):
                return 'no string value in form'
            if re.search(pattern, forms[idx]):
                return exclude_reason
    for form in forms:
        if form and form.casefold() in exclude_list:
            return 'in exclusion list'
    return 'keep'


if __name__ == '__main__':
    hdf = pd.read_pickle('hits.zip')
    print(f'Loaded {len(hdf)} hits')

    exclude = load_and_filter_excl('exclude.txt')

    # filter
    actions = [check_hit(x, exclude) for x in tqdm(zip(hdf['original'], hdf['male'], hdf['female']), desc='Running filter..')]
    hdf['action'] = actions
    print(Counter(actions))
    hdf.to_pickle('hits.zip')


