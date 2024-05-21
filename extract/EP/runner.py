import os
import utils as utils
import gender as ge

def preprocess():
    store = utils.ep_make_store()
    utils.ep_iterate_files(r'C:\Users\Valentin\PycharmProjects\DE_gender_project\data\Europarl\txt\de', store)
    print(len(store['docs']))
    print(len(store['speakers']))
    print(store['languages'])
    # filtered_ids = utils.ep_dumb_filter(store)
    # print(len(filtered_ids))
    docs = utils.ep_doc_list(store)
    # filt_docs = utils.ep_doc_list(store, filtered_ids)
    # utils.ep_write_doc_list_json('../chapters/all.txt', docs)
    # utils.ep_write_doc_list_json('../chapters/innen.txt', filt_docs)
    utils.ep_write_continuous_fragments(docs, r'C:\Users\Valentin\PycharmProjects\DE_gender_project\data\Europarl\fragments\all', 'all')
    # utils.ep_write_continuous_fragments(filt_docs, '../fragments/innen', 'innen')


def label_fragments():
    f_out = 'data/Europarl/fragments/labeled/filtered.txt'
    directory = os.fsencode('data/Europarl/fragments/all')
    with open(f_out, 'w', encoding='utf-8') as otf:
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            for fragment in utils.ep_read_fragments(f'data/Europarl/fragments/all/{filename}'):
                joined_text = ' '.join(fragment['text'])
                labels = ge.label_text(joined_text)
                if len(labels) > 0:
                    label_string = ';'.join(sorted(labels))
                    otf.write(f'{fragment["id"]}\t{label_string}\t{joined_text}\n')
    pass


if __name__ == '__main__':
    preprocess()
    # label_fragments()
