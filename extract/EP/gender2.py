import re, utils
import pandas as pd

test_string = 'das sind meine schüler und schülerinnen, meine lehrerinnen oder lehrer und studentinnen und studenten ' \
              'aber auch beamte und beamtinnen. Oder schüler*innen drinnen. Worin unterscheiden sich ..'

query_dict = {
    'double_mention': [
        (re.compile(r'\b([\S]+)innen (und|oder|,\s?|;\s?|\s?-\s?) \1en\b'), (0, 'en'), (0, 'innen')),  # studenten
        (re.compile(r'\b([\S]+)en (und|oder|,\s?|;\s?|\s?-\s?) \1innen\b'), (0, 'en'), (0, 'innen')),
        (re.compile(r'\b([\S]+)innen (und|oder|,\s?|;\s?|\s?-\s?) \1e\b'), (0, 'e'), (0, 'innen')),  # beamte
        (re.compile(r'\b([\S]+)e (und|oder|,\s?|;\s?|\s?-\s?) \1innen\b'), (0, 'e'), (0, 'innen')),
        (re.compile(r'\b([\S]+)innen (und|oder|,\s?|;\s?|\s?-\s?) \1n\b'), (0, 'n'), (0, 'innen')),  # schülern
        (re.compile(r'\b([\S]+)n (und|oder|,\s?|;\s?|\s?-\s?) \1innen\b'), (0, 'n'), (0, 'innen')),
        (re.compile(r'\b([\S]+)innen (und|oder|,\s?|;\s?|\s?-\s?) \1\b'), (0, ''), (0, 'innen')),  # schüler
        (re.compile(r'\b([\S]+) (und|oder|,\s?|;\s?|\s?-\s?) \1innen\b'), (0, ''), (0, 'innen')),
        (re.compile(r'\b([\S]+)männer (und|oder|,\s?|;\s?|\s?-\s?) \1frauen\b'), (0, 'männer'), (0, 'frauen')),
        # *männer
        (re.compile(r'\b([\S]+)frauen (und|oder|,\s?|;\s?|\s?-\s?) \1männer\b'), (0, 'männer'), (0, 'frauen')),
        (re.compile(r'\b([\S]+)jungen (und|oder|,\s?|;\s?|\s?-\s?) \1mädchen\b'), (0, 'jungen'), (0, 'mädchen')),
        # *jungen
        (re.compile(r'\b([\S]+)mädchen (und|oder|,\s?|;\s?|\s?-\s?) \1jungen\b'), (0, 'jungen'), (0, 'mädchen')),
        (re.compile(r'\b([\S]+)mann (und|oder|,\s?|;\s?|\s?-\s?) \1frau\b'), (0, 'mann'), (0, 'frau')),  # *mann
        (re.compile(r'\b([\S]+)frau (und|oder|,\s?|;\s?|\s?-\s?) \1mann\b'), (0, 'mann'), (0, 'frau')),
        (re.compile(r'\b([\S]+)junge (und|oder|,\s?|;\s?|\s?-\s?) \1mädchen\b'), (0, 'junge'), (0, 'mädchen')),
        # *jungen
        (re.compile(r'\b([\S]+)mädchen (und|oder|,\s?|;\s?|\s?-\s?) \1junge\b'), (0, 'junge'), (0, 'mädchen'))
    ],
    'star_pl': [
        (re.compile(r'\b(([^\s-]+)(([*:_!/|]-?i)|I)nnen)\b'), (1, ''), (0, ''))
    ],
    'star_sg': [
        (re.compile(r'\b(([^\s-]+)(([*:_!/|]-?i)|I)n)\b'), (1, ''), (0, ''))
    ],
    'in_form_sg': [
        (re.compile(r'\b([A-ZÄÖÜ]([\S]+([^aeiouäüöyh\s]|ch))in)\b'), (1, ''), (0, ''))  # no vowel or sole h before in
    ],
    'in_form_pl': [
        (re.compile(r'\b([A-ZÄÖÜ]([\S]+)innen)\b'), (1, ''), (0, ''))
    ],
}

exclude_set = {'darin', 'worin', 'dahin', 'wohin', 'vorhin', 'drinnen', 'binnen', 'disziplin', 'benzin', 'kamin',
               'termin', 'berlin', 'ansinnen', 'doktrin', 'beginnen', 'michelin', 'putin', 'turin', 'gewinnen',
               'hierin', 'robin', 'kevin', 'nikotin'}


def extract_forms(txt, queries, exclude):
    hits = []
    for label in queries:
        for query in queries[label]:
            matches = re.findall(query[0], txt)
            for match in matches:
                male = match[query[1][0]] + query[1][1]
                female = match[query[2][0]] + query[2][1]
                if male.casefold() not in exclude and female.casefold() not in exclude:
                    hits.append((label, male, female))
    return hits


def process_text(txt, queries, exclude, output_file, count_dict, hit_df=None, txt_id='', speaker='None', sep='\t', hitsep=';'):
    hits = extract_forms(txt, queries, exclude)
    if len(hits) > 0:
        output_file.write(f'{txt_id}{sep}{format_hits(hits, hitsep)}{sep}{txt}\n')
        count_hits(hits, count_dict)
        if hit_df is not None:
            store_hits(hit_df, txt_id, hits, speaker)


def format_hits(hits, sep=';'):
    buf = []
    for hit in hits:
        label = hit[0]
        male = hit[1]
        fem = hit[2]
        if label == 'double_mention':
            buf.append(f'{label}-{male}-{fem}')
        else:
            buf.append(f'{label}-{fem}')
    return sep.join(buf)


def count_hits(hits, dct):
    for hit in hits:
        label = hit[0]
        male = hit[1]
        fem = hit[2]
        if label not in dct['labels']:
            dct['labels'][label] = 0
        dct['labels'][label] += 1
        if fem not in dct['forms']:
            dct['forms'][fem] = 0
        dct['forms'][fem] += 1


def make_hit_df(data):
    return pd.DataFrame(data, columns=['frag_id', 'speaker', 'year', 'type', 'form'])


def store_hits(df, frag_id, hits, speaker):
    year = None
    if len(frag_id) > 0:
        year = int(frag_id.split('-')[1]) + 1900
        if year < 1996:
            year += 100
    for hit in hits:
        df.append([frag_id, speaker, year, hit[0], hit[2]])



if __name__ == '__main__':
    otf = open('long.txt', 'w', encoding='utf-8')
    data = []
    counter = {'labels': {}, 'forms': {}}
    for i in range(9):
        fname = f'C:/Users/Valentin/PycharmProjects/DE_gender_project/data/Europarl/fragments/all/all_0{i}.txt'
        for frag in utils.ep_read_fragments(fname):
            process_text(' '.join(frag['text']), query_dict, exclude_set, otf, counter, data, frag['id'], frag['speaker'])
        otf.flush()
    otf.close()
    print(counter['labels'])
    df = make_hit_df(data)
    df.to_pickle('forms.pickle')
    df.to_csv('forms.csv')
    with open('forms.txt', 'w', encoding='utf-8') as fotf:
        for form in counter['forms'].keys():
            fotf.write(f'{form}\t{counter["forms"][form]}\n')


