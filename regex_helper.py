import re

queries = {
    'double_mention': [
        (r'\b([\S]+)innen (und|oder|,\s?|;\s?|\s?-\s?) \1en\b', (1, 'en'), (1, 'innen')),
        # studenten
        (r'\b([\S]+)en (und|oder|,\s?|;\s?|\s?-\s?) \1innen\b', (1, 'en'), (1, 'innen')),
        (r'\b([\S]+)innen (und|oder|,\s?|;\s?|\s?-\s?) \1e\b', (1, 'e'), (1, 'innen')),  # beamte
        (r'\b([\S]+)e (und|oder|,\s?|;\s?|\s?-\s?) \1innen\b', (1, 'e'), (1, 'innen')),
        (r'\b([\S]+)innen (und|oder|,\s?|;\s?|\s?-\s?) \1n\b', (1, 'n'), (1, 'innen')),  # schülern
        (r'\b([\S]+)n (und|oder|,\s?|;\s?|\s?-\s?) \1innen\b', (1, 'n'), (1, 'innen')),
        (r'\b([\S]+)innen (und|oder|,\s?|;\s?|\s?-\s?) \1\b', (1, ''), (1, 'innen')),  # schüler
        (r'\b([\S]+) (und|oder|,\s?|;\s?|\s?-\s?) \1innen\b', (1, ''), (1, 'innen')),
        (r'\b([\S]+)männer (und|oder|,\s?|;\s?|\s?-\s?) \1frauen\b', (1, 'männer'), (1, 'frauen')),
        # *männer
        (r'\b([\S]+)frauen (und|oder|,\s?|;\s?|\s?-\s?) \1männer\b', (1, 'männer'), (1, 'frauen')),
        (
            r'\b([\S]+)jungen (und|oder|,\s?|;\s?|\s?-\s?) \1mädchen\b', (1, 'jungen'),
            (1, 'mädchen')),
        # *jungen
        (
            r'\b([\S]+)mädchen (und|oder|,\s?|;\s?|\s?-\s?) \1jungen\b', (1, 'jungen'),
            (1, 'mädchen')),
        (r'\b([\S]+)mann (und|oder|,\s?|;\s?|\s?-\s?) \1frau\b', (1, 'mann'), (1, 'frau')),  # *mann
        (r'\b([\S]+)frau (und|oder|,\s?|;\s?|\s?-\s?) \1mann\b', (1, 'mann'), (1, 'frau')),
        (r'\b([\S]+)junge (und|oder|,\s?|;\s?|\s?-\s?) \1mädchen\b', (1, 'junge'), (1, 'mädchen')),
        # *jungen
        (r'\b([\S]+)mädchen (und|oder|,\s?|;\s?|\s?-\s?) \1junge\b', (1, 'junge'), (1, 'mädchen'))
    ],
    'star_pl': [
        (r'\b(([^\s-]{3,})(([*:_!/|]-?i)|I)nnen)\b', (2, ''), (1, ''))
    ],
    'star_sg': [
        (r'\b(([^\s-]{3,})(([*:_!/|]-?i)|I)n)\b', (2, ''), (1, ''))
    ],
    'in_form_sg': [
        (r'\b([A-ZÄÖÜ]([\S]{2,}([^aeiouäüöyh\s]|ch))in)\b', (2, ''), (1, ''))
        # no vowel or sole h before in
    ],
    'in_form_pl': [
        (r'\b(([A-ZÄÖÜ][\S]{2,})innen)\b', (2, ''), (1, ''))
    ],
    'nde_form': [
        # re.compile(r'(?!(.+ochenenden*)|.+ausende(r*|n*)|.+wende|.+spende|.+ividende|Dutzende(*r|n*)\b([A-ZÄÖÜ][a-z]{2,})ende(r*|n*|m*)\b'),
        (re.compile(
            r'(?!(.+ochenenden*)|.+ausende(r*|n*)|.+wende|.+spende|.+ividende|[Dd]utzende(r*|n*)|.*[Kk]alendern*|.*sitzenden*)'
            r'\b([A-ZÄÖÜ][a-z]{2,})ende(r*|n*|m*)\b'),
         (4, ''), (4, ''))
    ],
    'kraft_form': [
        (re.compile(r'(?!Wasser.|Atom.|Muskel.|Spreng.|Vorstellungs.)\b([A-ZÄÖÜ][a-z]{2,})(kraft|kräfte)\b'), (0, ''),
         (0, ''))
    ],
    'Person/Mensch': [
        (re.compile(r'\b([a-zäöü][a-z]{2,})ende Person\b'), (0, ''), (0, '')),
        (re.compile(r'\b([a-zäöü][a-z]{2,})ender Mensch\b'), (0, ''), (0, '')),
        (re.compile(r'\bPerson, die\b'), (0, ''), (0, '')),
        (re.compile(r'\bMensch, der\b'), (0, ''), (0, '')),
    ],
}

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

def norm_text(txt):
    x = re.sub(r'[\r\n\s]+', ' ', txt)
    x = re.sub(r'\u200B', '', txt)
    return x



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


def find_hits_with_indices(text, excluded=[], skip_labels=[]):
    hits = []
    for label in queries:
        if label not in skip_labels:
            for query in queries[label]:
                for match in re.finditer(query[0], text):
                    male = match[query[1][0]] + query[1][1]
                    female = match[query[2][0]] + query[2][1]
                    full = match[0]
                    if re.search(r'[(){}?!\[\],;&%<>$§#]|\*{2,}|\.{2,}|\\{2,}|/{2,}\d|\.[^iI]', full):
                        continue
                    if male.casefold() not in excluded and female.casefold() not in excluded and full.casefold() not in excluded:
                        hits.append({'label': label, 'full': full, 'male': male, 'female': female,
                                     'start': match.start(0), 'end': match.end(0)})
    return hits
