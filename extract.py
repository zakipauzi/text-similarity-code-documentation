import doc_extract as de
import code_extract as ce
import pandas as pd
import numpy as np
import os
import logging
import spacy
from pathlib import Path

def run_extract(root):
    # get all the folders in repo - 50 open sourced Github projects
    dirlist = [ item for item in os.listdir(root) if os.path.isdir(os.path.join(root, item)) ]
    readme_list = []
    code_list = []

    kw = ce.generate_kw()

    nlp = spacy.load('en_core_web_md')
    nlp.max_length = 4000000

    counter = 1

    for dir in dirlist:
        print('[{}/{}] Extracting {}...'.format(counter, len(dirlist),dir))

        # create output dir
        Path("output/" + dir).mkdir(parents=True, exist_ok=True)

        # extract from doc
        doc_extracted = de.extract_from_doc(root + '\\' + dir + '\\', nlp)
        out_doc_file = "output/{}/{}_doc.txt".format(dir, dir)

        if doc_extracted is not np.nan:
            with open(out_doc_file, "w", encoding='utf-8') as text_file:
                text_file.write(doc_extracted)

            readme_list.append('Doc extracted at {}'.format(out_doc_file))
        else:
            readme_list.append(np.nan)

        # Because there are multiple code files, we do not try catch here.
        code_extracted = ce.extract_from_code(root + '\\' + dir + '\\', kw, nlp)
        out_code_file = "output/{}/{}_code.txt".format(dir,dir)

        if code_extracted is not np.nan:
            with open(out_code_file, "w", encoding='utf-8') as text_file:
                text_file.write(code_extracted)
            code_list.append('Code extracted at {}'.format(out_code_file))
        else:
            code_list.append(np.nan)

        counter+=1


    df_readme = pd.DataFrame(list(zip(dirlist,readme_list)), columns=['Repo','Doc Extraction Status'])
    df_readme = df_readme.dropna() # remove empty rows

    df_code = pd.DataFrame(list(zip(dirlist,code_list)), columns=['Repo','Code Extraction Status'])
    df_code = df_code.dropna() # remove empty rows

    print('Code and Doc extraction completed successfully!')

    return df_readme, df_code
