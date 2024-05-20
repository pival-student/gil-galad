
# GIL-GALaD: Gender Inclusive Language - German Auto-Assembled Large Database

  * [About](#about)
  * [Content](#content)
  * [Authors](#authors)
  * [Usage](#usage)

## About
GIL-GALaD is a coupus of German gender-inclusive language.
- over 830k gender-inclusive forms 
- five different sources (social media posts, political speeches, newspapers, magazines, academic texts)

## Content
The corpus is divided into two parts.

Source texts:
sample_id,text, source, author, day, month, year, location

Forms:
sample_id, start, end, type, male, female, author, year, month, day

- types:
 - double_mention: explicit double mention e.g. Lehrer und Lehrerinnen
 - in_form: female form (sg. or pl.)
 - star: double mentions using special symbols like *
 - nde_form: nominalized participles such as 'Studierende'
 - kraft_form: abstract forms such as 'Fachkraft'
 - Person/Mensch: adjectival gender-evading constructions using person/human like 'unterzeichnende Person' 

## Authors

- Valentin Pickard [@pival-student](https://github.com/pival-student)
- Anna-Katharina Dick [@AnnaKatharinaD](https://github.com/AnnaKatharinaD)
- Matthias Drews [@madrews](https://github.com/madrews)
- Victoria Pierz

## Usage
The corpus can be used for a variety of purposes, including but not limited to:

- Machine translation:
    - from generically masculine German to gender-inclusive German
    - from languages without grammatical gender to German
- Training models to recognize and generate gender-inclusive text
- Studying the usage and development of gender-inclusive language in German over time in different domains

Load the forms:

```python
import pickle
import pandas as pd

df = pd.read_pickle('hits_joined')
# inspect data
df.head()
```

### Twitter
### Wortschatz Leipzig
### Europarl
### APuZ
