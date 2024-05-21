import requests
from bs4 import BeautifulSoup


def normalize_query(s):
    n = s.replace("ä", "ae")
    n = n.replace("Ä", "Ae")
    n = n.replace("ö", "oe")
    n = n.replace("Ö", "Oe")
    n = n.replace("ü", "ue")
    n = n.replace("Ü", "Ue")
    n = n.replace("ß", "sz")
    return n

def make_request(word, skip_check=True):
    query = normalize_query(word)
    r = requests.get("https://www.duden.de/rechtschreibung/" + query)

    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'html.parser')

        s = soup.find()
        content = s.find_all('h2')
        match_start = str(content).find("</em> und")
        match_end = str(content).find("</em></h2>")

        result = str(content)[match_start + 14:match_end]
        if skip_check or normalize_query(make_request(result)) == query:
            return result
        else:
            return None

    else:
        return None


if __name__ == '__main__':

    list = ["Arzt", "Ärzte",  "Akteurin", "Ärztin", "Glub"]
    expected = ["Ärztin", "Ärztinnen", "Akteur", "Arzt", None]
    omit_check = False

    for word, target in zip(list, expected):
        print(f'Query: "{word}"  Result: "{make_request(word, omit_check)}"  Expected: "{target}"')