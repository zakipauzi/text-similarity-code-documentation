import glob
import string
import keyword
import decamelize
import nltk
import json
import logging
import re
import os
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

logging.basicConfig(level=logging.DEBUG)

# This extraction of concepts is based on the NLP method

def extract_from_code(folder, kw, nlp):
    # classes = []
    # methods = []
    # attributes = []
    extracted = []

    kw_pattern = re.compile(r'\b(' + r'|'.join(kw) + r')\b\s*')

    # fetch all java files from folder
    files = [f for f in glob.glob(folder + '**/*.java', recursive=True)]

    # remove any folders that may resemble a file
    files = [f for f in files if os.path.isfile(f)]

    for f in files:
        # ingest the source code
        try:
            extracted.append(code_ingest(f, kw_pattern, nlp))
        except:
            logging.debug('Unable to read code {}'.format(f))
        # classes.append(x)
        # methods.append(y)
        # attributes.append(z)

    extracted = [ x for x in extracted if x ] # remove empty strings

    if not extracted:
        return np.nan # no codes able to be extracted

    # final merging of all strings
    extracted = ' '.join(extracted)

    return extracted


def code_ingest(filename, kw_pattern, nlp):
    class_list = []
    att_list = []
    method_list = []

    with open(filename, 'r', encoding='utf-8') as file:
        code_text = file.readlines()

    terms_list = []

    # strip strings of newlines and whitespaces
    code_text = [x.strip() for x in code_text]

    # only pull classes, attributes & methods
    for x in code_text:
        if (x.startswith('public') or x.startswith('private') or x.startswith('protected') or x.startswith('class')
        or x.startswith('enum')):
            terms_list.append(x)

    # remove noise by tokenising
    terms_list = [word_tokenize(x) for x in terms_list]

    # flatten list
    terms_list = [x for sublist in terms_list for x in sublist]

    # decamelize
    terms_list = [decamelize.convert(x) for x in terms_list]

    # split back those decamelised to tuple values (using only first '_')
    terms_list = [x.split('_') for x in terms_list]

    # flatten list
    terms_list = [x for sublist in terms_list for x in sublist]

    # remove any characters w/out meaning
    terms_list = [x for x in terms_list if (len(x) > 2 and x.isalpha())]

    # remove keywords
    terms = kw_pattern.sub('', ' '.join(terms_list))

    terms_list = [x.lemma_ for x in nlp(terms)]

    terms = ' '.join(terms_list)

    return terms

def generate_kw():
    # populate keywords list including stopwords
    try:
        with open('java_kw.txt', 'r') as f:
            java_kw = f.readlines()
            java_kw = [x.strip() for x in java_kw]
    except:
        print('Java keywords missing!')

    kw_list = keyword.kwlist # python keywords
    kw_list += java_kw # java keywords
    kw_list += (set(stopwords.words('english'))) # stop words
    return kw_list
