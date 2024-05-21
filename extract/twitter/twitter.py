import re
import os
import json
import gzip
from types import SimpleNamespace as Namespace
from datetime import datetime, timezone
from tqdm import tqdm

url_pattern = r'(https?|ftp)\S+'
usr_pattern = r'@\S+'

def ymd_from_timestamp(ts_string):
    s = ts_string[:10] + '.' + ts_string[:10]  # timestamp stored as string without decimal point ...
    d = datetime.fromtimestamp(float(s), timezone.utc)
    return d.year, d.month, d.day

def normalize_text(txt):
    s = re.sub(url_pattern, '<URL>', txt)
    s = re.sub(usr_pattern, '@USER', s)
    return s


class TwitterExtractor:

    def __init__(self, input_dir, output_dir, config_file):
        self.ipt_dir = input_dir
        self.opt_dir = output_dir
        with open(config_file, 'r', encoding='utf-8') as cff:
            self.cfg = json.load(cff, object_hook=lambda d: Namespace(**d))
        self.counter = {}
        for key in self.cfg.count_occ:
            self.counter[key] = {'all': {}, 'samples': {}}
        self.excluded = self.load_excluded()
        self.stats = {'all': {}, 'samples': {}}
        self.hits = {}
        self.sample_file = None
        self.sample_count = 0
        self.sample_file_count = 0
        self.hit_file = None
        self.hit_count = 0
        self.hit_file_count = 0
        self.hit_header = '\t'.join([
            'label',
            'male',
            'female',
            'year',
            'month',
            'day',
            'id'
        ]) + '\n'
        self.queries = {
            'double_mention': [
                (re.compile(r'\b([\S]+)innen (und|oder|,\s?|;\s?|\s?-\s?) \1en\b'), (0, 'en'), (0, 'innen')),
                # studenten
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
                (
                    re.compile(r'\b([\S]+)jungen (und|oder|,\s?|;\s?|\s?-\s?) \1mädchen\b'), (0, 'jungen'),
                    (0, 'mädchen')),
                # *jungen
                (
                    re.compile(r'\b([\S]+)mädchen (und|oder|,\s?|;\s?|\s?-\s?) \1jungen\b'), (0, 'jungen'),
                    (0, 'mädchen')),
                (re.compile(r'\b([\S]+)mann (und|oder|,\s?|;\s?|\s?-\s?) \1frau\b'), (0, 'mann'), (0, 'frau')),  # *mann
                (re.compile(r'\b([\S]+)frau (und|oder|,\s?|;\s?|\s?-\s?) \1mann\b'), (0, 'mann'), (0, 'frau')),
                (re.compile(r'\b([\S]+)junge (und|oder|,\s?|;\s?|\s?-\s?) \1mädchen\b'), (0, 'junge'), (0, 'mädchen')),
                # *jungen
                (re.compile(r'\b([\S]+)mädchen (und|oder|,\s?|;\s?|\s?-\s?) \1junge\b'), (0, 'junge'), (0, 'mädchen'))
            ],
            'star_pl': [
                (re.compile(r'\b(([^\s-]{3,})(([*:_!/|]-?i)|I)nnen)\b'), (1, ''), (0, ''))
            ],
            'star_sg': [
                (re.compile(r'\b(([^\s-]{3,})(([*:_!/|]-?i)|I)n)\b'), (1, ''), (0, ''))
            ],
            # 'in_form_sg': [
            #     (re.compile(r'\b([A-ZÄÖÜ]([\S]+([^aeiouäüöyh\s]|ch))in)\b'), (1, ''), (0, ''))
            #     # no vowel or sole h before in
            # ],
            # 'in_form_pl': [
            #     (re.compile(r'\b([A-ZÄÖÜ]([\S]+)innen)\b'), (1, ''), (0, ''))
            # ],
        }
        for q in self.queries:
            self.hits[q] = {'total': 0}

    def go(self):
        self.make_sample_file()
        self.make_hit_file()
        directory = os.fsencode(self.ipt_dir)
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if re.match(self.cfg.input_file_pattern, filename):
                self.process_file(os.path.join(self.ipt_dir, filename))
        self.finish()

    def test(self):
        for i in range(5):
            self.make_sample_file()
            self.make_hit_file()
        directory = os.fsencode(self.ipt_dir)
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.startswith(self.cfg.input_file_pattern):
                print(f'Found {filename}')

    def process_file(self, fpath):
        with gzip.open(fpath, 'rt', encoding='utf-8') as ipt:
            for line in tqdm(ipt, desc=f'Processing {fpath}'):
                try:
                    content = json.loads(line.strip())
                    self.process_tweet(content)
                except json.JSONDecodeError:
                    continue  # skip empty lines or malformed json
        pass

    def process_tweet(self, content):
        # gather stats for all tweets (date, user, loc ..)
        year, month, day = ymd_from_timestamp(content['timestamp'])
        date_key = ''
        if self.cfg.stats_per == 'year':
            date_key = f'{year}'
        elif self.cfg.stats_per == 'month':
            date_key = f'{year}-{int(month):02d}'
        elif self.cfg.stats_per == 'day':
            date_key = f'{year}-{int(month):02d}-{int(day):02d}'
        self.register_stats('all', date_key, content, [])
        # check text
        ntext = normalize_text(content['text'])
        hits = self.extract_forms(ntext)
        if len(hits) > 0:
            self.register_stats('samples', date_key, content, hits)
            self.write_sample(hits, content, year, month, day)
            self.write_hits(hits, content, year, month, day)

    def extract_forms(self, txt):
        hits = []
        for label in self.queries:
            for query in self.queries[label]:
                matches = re.findall(query[0], txt)
                for match in matches:
                    male = match[query[1][0]] + query[1][1]
                    female = match[query[2][0]] + query[2][1]
                    if male.casefold() not in self.excluded and female.casefold() not in self.excluded:
                        hits.append((label, male, female))
        return hits

    def make_sample_file(self):
        if self.sample_file is not None:
            self.sample_file.flush()
            self.sample_file.close()
        self.sample_file_count += 1
        self.sample_count = 0
        name = f'{self.cfg.sample_file_prefix}_{self.sample_file_count:03d}.txt'
        self.sample_file = open(os.path.join(self.opt_dir, name), 'w', encoding='utf-8')

    def make_hit_file(self):
        if self.hit_file is not None:
            self.hit_file.flush()
            self.hit_file.close()
        self.hit_file_count += 1
        self.hit_count = 0
        name = f'{self.cfg.hit_file_prefix}_{self.hit_file_count:03d}.txt'
        self.hit_file = open(os.path.join(self.opt_dir, name), 'w', encoding='utf-8')
        self.hit_file.write(self.hit_header)

    def load_excluded(self):
        ex = set()
        if self.cfg.exclusion_set != '':
            with open(self.cfg.exclusion_set, 'r', encoding='utf-8') as ipt:
                for line in ipt:
                    if len(line.strip()) > 0:
                        ex.add(line.strip().casefold())
        return ex

    def register_stats(self, group, date_key, content, hits):
        if date_key not in self.stats[group]:
            self.stats[group][date_key] = 0
        self.stats[group][date_key] += 1
        for val in self.cfg.count_occ:
            if val in content and content[val] not in self.counter[val][group]:
                self.counter[val][group][content[val]] = 0
            self.counter[val][group][content[val]] += 1
        for hit in hits:
            self.hits[hit[0]]['total'] += 1
            if hit[2] not in self.hits[hit[0]]:
                self.hits[hit[0]][hit[2]] = 0
            self.hits[hit[0]][hit[2]] += 1  # count female forms, disregard normalisation for now

    def write_sample(self, hits, content, year, month, day):
        content['year'] = year
        content['month'] = month
        content['day'] = day
        content['hits'] = [{'label': h[0], 'male': h[1], 'female': h[2]} for h in hits]
        self.sample_file.write(f'{json.dumps(content, ensure_ascii=False)}\n')
        if self.sample_count == self.cfg.sample_file_length:
            self.make_sample_file()
        self.sample_count += 1
        if self.sample_count == self.cfg.sample_file_length:
            self.make_sample_file()
        pass

    def write_hits(self, hits, content, year, month, day):
        for hit in hits:
            line = '\t'.join([
                *hit,
                str(year),
                str(month),
                str(day),
                str(content['id'])
            ])
            self.hit_file.write(f'{line}\n')
            self.hit_count += 1
            if self.hit_count == self.cfg.hit_file_length:
                self.make_hit_file()
        pass

    def write_overall_stats(self):
        print('Collecting/writing overall statistics...')
        # label and hits rough stats
        for q in self.hits:
            name = f'{self.cfg.stats_file_prefix}_{q}.txt'
            with open(os.path.join(self.opt_dir, name), 'w', encoding='utf-8') as otf:
                for k, v in sorted(self.hits[q].items(), key=lambda y: y[1], reverse=True):
                    otf.write(f'{k} : {v}\n')
        # total samples/hits by time interval
        name = f'{self.cfg.stats_file_prefix}_temporal.txt'
        with open(os.path.join(self.opt_dir, name), 'w', encoding='utf-8') as otf:
            times = sorted(self.stats['all'].keys())
            all_tweets = 0
            samples = 0
            for t in times:
                all_tweets += self.stats["all"][t]
                scount = self.stats['samples'][t] if t in self.stats['samples'] else 0
                samples += scount
                percentage = round((100.0 * scount) / self.stats["all"][t], 3)
                otf.write(f'{t}\t{self.stats["all"][t]}\t{scount}\t{percentage}\n')
            otf.write(f'Total\t{all_tweets}\t{samples}\t{round((100.0 * samples) / all_tweets, 3)}\n')
        pass

    def finish(self):
        if self.sample_file is not None:
            self.sample_file.flush()
            self.sample_file.close()
        if self.hit_file is not None:
            self.hit_file.flush()
            self.hit_file.close()
        self.write_overall_stats()
        print('Done!')


if __name__ == '__main__':
    # print('go')

    # print(os.path.join('..', 'data', 'log.txt'))
    x = TwitterExtractor('./de-tweets', './outputs', 'cfg.json')
    x.go()
    # for k in x.counter:
    #     print(x.counter[k]['samples'])

    # x.test()
    # print(x.cfg.sample_file_length)
    # x.process_file('tweets.txt')
    # j = json.loads('{"id": 1139511757309915136, "timestamp": "1560515748704"}')
    # print(ymd_from_timestamp(j['timestamp']))
    # print(j)
