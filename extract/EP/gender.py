import re

patterns = {
    'double': [
        re.compile(r'\b([\S]+)innen (und|oder) \1en\b'),  # studenten
        re.compile(r'\b([\S]+)en (und|oder) \1innen\b'),
        re.compile(r'\b([\S]+)innen (und|oder) \1e\b'),  # beamte
        re.compile(r'\b([\S]+)e (und|oder) \1innen\b'),
        re.compile(r'\b([\S]+)innen (und|oder) \1n\b'),  # schülern
        re.compile(r'\b([\S]+)n (und|oder) \1innen\b'),
        re.compile(r'\b([\S]+)innen (und|oder) \1\b'),  # schüler
        re.compile(r'\b([\S]+) (und|oder) \1innen\b'),
        re.compile(r'\b([\S]+)männer (und|oder) \1frauen\b'), # *männer
        re.compile(r'\b([\S]+)frauen (und|oder) \1männer\b')
    ],
    'innen': [
        re.compile(r'\b([\S]{3,})innen\b') # min length 3
    ],
    'pronoun': [
        re.compile(r'\ber|sie|ihn|ihm|ihr(e|es|em|en|er)?|sein(s|e|es|em|en|er)?|(diese|jede|jene)[smnr]?\b')
    ],
    'nde': [
        re.compile(r'\b([\S]{3,})ende\b') # min length 3
    ]
}


def find_gendered_pronouns(txt):
    for pattern in patterns['double']:
        if re.search(pattern, txt.casefold()):
            return True
    return False


def find_double_mentions(txt):
    for pattern in patterns['double']:
        if re.search(pattern, txt):
            return True
    return False


def find_innen_forms(txt):
    for pattern in patterns['innen']:
        if re.search(pattern, txt):
            return True
    return False


def find_nde_forms(txt): # also nte?
    for pattern in patterns['nde']:
        if re.search(pattern, txt):
            return True
    return False


def find_neo_pronouns(txt):
    return True


def label_text(txt):
    labels = []
    if find_nde_forms(txt):
        labels.append('ND')
    if find_double_mentions(txt):
        labels.append('2X')
    if find_gendered_pronouns(txt):
        labels.append('GP')
    if find_innen_forms(txt):
        labels.append('IN')
    return labels

