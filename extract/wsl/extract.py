import re
import glob, os
import pandas as pd
import pickle
from dateutil.parser import parse

test_string = 'das sind meine schüler und schülerinnen, meine lehrerinnen oder lehrer und studentinnen und studenten ' \
              'aber auch beamte und beamtinnen. Oder schüler*innen drinnen. Studierende auch.'

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
        (re.compile(r'\b(([\S]+)(([*:_!/|]-?i)|I)nnen)\b'), (1, ''), (0, ''))
    ],
    'star_sg': [
        (re.compile(r'\b(([\S]+)(([*:_!/|]-?i)|I)n)\b'), (1, ''), (0, ''))
    ],
    # 'in_form_sg': [
    #    (re.compile(r'\b([A-ZÄÖÜ]([\S]+([^aeiouäüöyh\s]|ch))in)\b'), (1, ''), (0, ''))  # no vowel or sole h before in
    # ],
    # 'in_form_pl': [
    #    (re.compile(r'\b([A-ZÄÖÜ]([\S]+)innen)\b'), (1, ''), (0, ''))
    # ],
    'nde_form': [
        # re.compile(r'(?!(.+ochenenden*)|.+ausende(r*|n*)|.+wende|.+spende|.+ividende|Dutzende(*r|n*)\b([A-ZÄÖÜ][a-z]{2,})ende(r*|n*|m*)\b'),
        (re.compile(
            r'(?!(.+ochenenden*)|.+ausende(r*|n*)|.+wende|.+spende|.+ividende|[Dd]utzende(r*|n*)|.*[Kk]alendern*|.*sitzenden*)'
            r'\b([A-ZÄÖÜ][a-z]{2,})ende(r*|n*|m*)\b'),
         (1, ''), (0, ''))
    ],
    'kraft_form': [
        (re.compile(r'(?!Wasser.|Atom.|Muskel.|Spreng.|Vorstellungs.)\b([A-ZÄÖÜ][a-z]{2,})(kraft|kräfte)\b'), (1, ''),
         (0, ''))
    ],
    'Person/Mensch': [
        (re.compile(r'\b([a-zäöü][a-z]{2,})ende Person\b'), (1, ''),(0, '')),
        (re.compile(r'\b([a-zäöü][a-z]{2,})ender Mensch\b'), (1, ''),(0, '')),
        (re.compile(r'\bPerson, die\b'), (1, ''),(0, '')),
        (re.compile(r'\bMensch, der\b'), (1, ''),(0, '')),
    ],
}

exclude = {'darin', 'worin', 'dahin', 'wohin', 'vorhin', 'drinnen', 'binnen', 'disziplin', 'benzin', 'kamin',
               'termin', 'berlin', 'ansinnen', 'doktrin', 'beginnen', 'michelin', 'putin', 'turin', 'gewinnen',
               'hierin', 'robin', 'kevin', 'dublin', 'nikotin', 'vorsitzender', 'vorsitzende'}
exclude_set = {'Saisonende',  'Reisende', 'Anwesende', 'Anziehungskraft', 'Aussagekraft',
               'Kernkraft', 'Überlebende', 'Überlebender', 'Sonnenkraft', 'Kaufkraft',
               'Jahresende', 'Kriegsende', 'Herausragende', 'Herausragender', 'Legende', 'Sterbende', 'Sterbender', 'Sterbenden',
               'Gegenden', 'Lebender', 'Lebende', 'Tugenden', 'Fernsehsender', 'Spielende'}


def read_files(dir_name):
    arr = os.listdir(dir_name)
    sentence_files = []
    source_files = []
    for file in arr:
        if '.DS_Store' not in file:
            corpus_dir = dir_name + '/' + file
            for file in os.listdir(corpus_dir):
                if file.endswith("sentences.txt"):
                    sentence_files.append(corpus_dir + '/' + file)
                if file.endswith("sources.txt"):
                    source_files.append(corpus_dir + '/' + file)
    return sorted(sentence_files), sorted(source_files)

def extract_year(sentence_file):
    return re.search(r"(\d{4})", sentence_file).group(1)
def make_filename(dir, year):
    size = sentence_file[20:].split('_')[-1] # e.g. extracted_2010_100k
    size = size.split('-')[0] #split off '-sentences.txt'
    return dir + 'extracted_' + str(year) + '_'+ str(size)# e.g. extracted_2010_100

OUT_DIR = '2001-2005'
FILES = '/Users/anna-katharinadick/DE_gender_project/data/Wortschatz Leipzig/mil_news2'

if __name__ == '__main__':
    with open('/Users/anna-katharinadick/DE_gender_project/gender_wörterbuch.pickle', 'rb') as pickle_file:
        gender_dict = pickle.load(pickle_file)
    mega_df = pd.DataFrame(columns=['ID', 'year', 'type', 'form', 'sentence'])
    sentence_files, source_files = read_files(FILES)
    for sentence_file in sentence_files:
        year = extract_year(sentence_file)
        filename = make_filename(OUT_DIR, year)
        df = pd.DataFrame(columns=['ID', 'type', 'form', 'sentence'])
        with open(sentence_file, 'r') as file:
            for line in file:
                line = line.split('\t')
                for label in query_dict:
                    for query in query_dict[label]:
                        if (re.search(query[0], line[1])):
                            match = re.search(query[0], line[1])
                            if match.group() not in exclude_set:
                                if label in ['kraft_form', 'nde_form', 'Person/Mensch']:
                                    for gendered,ungendered in zip(gender_dict['gendered'], gender_dict['non-gendered']):
                                        try:
                                            if str(match.group()) in ungendered:
                                                df = df.append({'ID': line[0], 'year': year, 'type': label, 'form': match.group(), 'span': match.span(), 'generic_masc': gendered,
                                                         'sentence': match.string.strip()}, ignore_index=True)
                                        except:
                                            continue
                                else:
                                    matches = re.findall(query[0], line[1])
                                    for match in matches:
                                        male = match[query[1][0]] + query[1][1]
                                    match = re.search(query[0], line[1])
                                    df = df.append({'ID':line[0], 'year': year, 'type':label, 'form':match.group(), 'span': match.span(), 'generic_masc': str(male),
                                                        'sentence': match.string.strip()}, ignore_index=True)
            df.to_csv(filename +'.csv', index=False)
            print(f'File done! {filename}')
            mega_df = pd.concat([mega_df, df])
    mega_df.to_pickle(OUT_DIR + '/all_deu_news_2005.pickle')
    mega_df.to_csv(OUT_DIR + '/all_deu_news_2005.csv', index=False)