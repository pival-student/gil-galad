import matplotlib.pyplot as plt
from datetime import datetime, timezone

from matplotlib.dates import DateFormatter

datafile = '../data/out/run1/stats_temporal.txt'


def load_data(filename):
    times = []
    tweets = []
    hits = []
    with open(filename, 'r', encoding='utf-8') as inf:
        for line in inf:
            if line.startswith('Total'):
                continue
            split = line.strip().split('\t')
            if len(split) >= 3:
                times.append(datetime.strptime(split[0], "%Y-%m-%d"))
                tweets.append(int(split[1]))
                hits.append(int(split[2]))
            else:
                print(f'Skipped datum: {line}')
    return times, tweets, hits


if __name__ == '__main__':
    t, y1, y2 = load_data(datafile)

    for i in range(25):
        print (f'{t[i].year}-{t[i].month:02d}-{t[i].day:02d}')

    ax1 = plt.subplot()
    # date_form = DateFormatter("%m-%d")
    # ax1.xaxis.set_major_formatter(date_form)
    l1 = ax1.bar(t, y1, color='blue')
    ax2 = ax1.twinx()
    l2 = ax2.bar(t, y2, color='orange')

    plt.legend([l1, l2], ["tweets", "gendered mentions"])

    plt.show()

    fig, ax = plt.subplots(figsize=(12, 12))
    ax.bar(t, y1, secondary_y=y2)
    plt.show()

    # print(t)
