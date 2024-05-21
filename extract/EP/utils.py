import os
import re
import json
from tqdm import tqdm


def ep_iterate_files(parent_dir, store):
    directory = os.fsencode(parent_dir)
    count = 0
    for file in tqdm(os.listdir(directory), desc='Processing files..'):
        filename = os.fsdecode(file)
        ep_parse_file(parent_dir, filename, store)
        count += 1
    print(f'Files: {count}')


def ep_parse_file(parent_dir, filename, store):
    with open(f'{parent_dir}/{filename}', 'r', encoding='utf-8') as inf:
        file_id = filename.split('.')[0]
        chapter_id = '<UNK>'
        doc_id = None
        speaker_id = '<TITLE>'
        lang_id = '<UNK>'
        for line in inf:
            stripped = line.strip()
            if len(stripped) < 4:
                continue
            if stripped.startswith('(') and stripped.endswith(')'):
                continue
            if stripped.startswith('<CHAPTER ID='):
                chapter_id = stripped.split('=')[1][:-1]
                doc_id = f'{file_id}_{chapter_id}'
                store['docs'][doc_id] = []
                speaker_id = '<TITLE>'
                lang_id = '<UNK>'
                continue
            if stripped.startswith('<SPEAKER ID='):
                match = re.search(r'SPEAKER ID=\d+( LANGUAGE="(?P<lang>[^"]+)")?( NAME="(?P<name>[^"]+)")?', stripped)
                if match and match.group('lang'):
                    lang_id = match.group('lang')
                    if lang_id not in store['languages']:
                        store['languages'].append(lang_id)
                if match and match.group('name'):
                    speaker_id = match.group('name')
                    if speaker_id not in store['speakers']:
                        store['speakers'].append(speaker_id)
                continue
            store['docs'][doc_id].append((lang_id, speaker_id, stripped))
    pass


def ep_make_store():
    return {
        'docs': {},
        'speakers': [],
        'languages': []
    }


def ep_dumb_filter(store):
    matches = []
    for doc_id in store['docs']:
        found = False
        if found:
            continue
        for line in store['docs'][doc_id]:
            if 'innen' in line[2]:
                matches.append(doc_id)
                found = True
                break
    return matches


def ep_doc_list(store, ids=None, only_de=False, no_title=False):
    doc_list = []
    doc_ids = ids if ids else store['docs'].keys()
    for doc_id in tqdm(doc_ids, desc='Converting docs..'):
        doc = {
            'id': doc_id,
            'lines': []
        }
        for line in store['docs'][doc_id]:
            if no_title and line[1] == '<TITLE>':
                continue
            if only_de and line[0] != 'DE':
                continue
            doc['lines'].append({
                'language': line[0],
                'speaker': line[1],
                'text': line[2]
            })
        doc_list.append(doc)
    return doc_list


def ep_write_doc_list_json(f_out, docs):
    with open(f_out, 'w', encoding='utf-8') as otf:
        for doc in tqdm(docs, desc='Writing output..'):
            otf.write(f'{json.dumps(doc, ensure_ascii=False)}\n')
    pass


def ep_read_doc_list_json(f_in):
    doc_list = []
    with open(f_in, 'r', encoding='utf-8') as inf:
        for line in tqdm(inf, desc='Loading docs..'):
            doc = json.loads(line)
            doc_list.append(doc)
    return doc_list


def ep_yield_fragment_strings(docs, skip_title=True, only_de=False):
    for doc in tqdm(docs, desc='Generating fragments..'):
        frag_count = -1
        speaker = None
        fragment = []
        for line in doc['lines']:
            if skip_title and line['speaker'] == '<TITLE>':
                continue
            if only_de and line['language'] != 'DE':
                continue
            if line['speaker'] != speaker:  # speaker change, new fragment
                speaker = line['speaker']
                frag_count += 1
                if len(fragment) > 0:
                    yield '\n'.join(fragment)
                fragment = [f'<{doc["id"]}_{frag_count}> <{speaker}>']
            fragment.append(line['text'])


def ep_write_continuous_fragments(docs, output_dir, f_name, skip_title=True, only_de=False, count=10000):
    file_count = 0
    frag_count = 0
    otf = open(f'{output_dir}/{f_name}_{file_count:02d}.txt', 'w', encoding='utf-8')
    for frag in ep_yield_fragment_strings(docs, skip_title, only_de):
        otf.write(f'{frag}\n')
        frag_count += 1
        if frag_count % count == 0:
            otf.flush()
            otf.close()
            file_count += 1
            otf = open(f'{output_dir}/{f_name}_{file_count:02d}.txt', 'w', encoding='utf-8')
    otf.flush()
    otf.close()
    print(f'Wrote {frag_count} fragments to {file_count +1} files')
    pass


def ep_make_fragment():
    return {
        'id': '',
        'text': [],
        'speaker': 'unknown'
    }


def ep_read_fragments(f_in):
    with open(f_in, 'r', encoding='utf-8') as inf:
        fragment = None
        for line in tqdm(inf, desc='Reading fragments..'):
            stripped = line.strip()
            if stripped.startswith('<') and stripped.endswith('>'):
                if fragment:
                    yield fragment
                fragment = ep_make_fragment()
                split = stripped.split('> <')
                if(len(split) > 1):
                    fragment['id'] = split[0][1:]
                    fragment['speaker'] = split[1][:-1]
                else:
                    fragment['id'] = stripped[1:-1]
            else:
                if fragment:
                    fragment['text'].append(stripped)
        if fragment:
            yield fragment
