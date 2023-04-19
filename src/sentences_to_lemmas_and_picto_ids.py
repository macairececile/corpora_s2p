"""From the .csv file with sentences, get all the possible ids pictos linked to each lemma of sentences.
The images of picto per sentences will be stored in a subdirectory per sentence.

Example of use:
python

Author
 * Cécile MACAIRE 2023
"""

import subprocess
import json
import stanza
import urllib.request
import re
from utils import *
from argparse import ArgumentParser, RawTextHelpFormatter


def get_sentences(file):
    """
        Function to get the sentences from a .csv file.

        Arguments
        ---------
        file : str
            Path of the .csv file.

        Returns
        -------
        A list with the sentences.
    """
    data = pd.read_csv(file, sep=',')
    return data['sentence'].tolist()


def preprocessing(sentences):
    """
        Function to process the sentences with stanza library.

        Arguments
        ---------
        sentences : list
            Sentences retrieved from the .csv file.

        Returns
        -------
        A list of lists with the lemmas of words of each sentences.
    """
    nlp = stanza.Pipeline(lang='fr', processors='tokenize,mwt,pos,lemma')
    sent_prep = []
    for s in sentences:
        doc = nlp(s)
        lemmas = [word.lemma for sent in doc.sentences for word in sent.words if word.pos != 'PUNCT']
        lemmas = list(filter(None, [re.sub(chars_to_ignore_regex, '', i) for i in lemmas]))
        sent_prep.append(lemmas)
    return sent_prep


def get_ids_pictos_from_word(word):
    """
        Function to get the picto ids from the word.

        Arguments
        ---------
        word : str

        Returns
        -------
        The picto ids linked to the word in arasaac.
    """
    mapping = dict(zip(special_char, equivalent))
    word_for_url = ''.join(mapping.get(c, c) for c in word)
    command = 'curl -X GET "https://api.arasaac.org/api/pictograms/fr/search/' + word_for_url + '" -H "accept: application/json"'
    result = subprocess.check_output(command, shell=True).decode('UTF-8')
    data = json.loads(result)
    ids = []
    for el in data:
        keywords = [k['keyword'] for k in el['keywords']]  # check if the word is in the keywords, else not printed
        if word in keywords:
            ids.append(el['_id'])
    return ids


def download_image(url, word, outdir):
    """
        Function to download an image.

        Arguments
        ---------
        url : str
            Url of the image to download.
        word : str
            Word which is linked to the picto.
        outdir : str
            Directory where to store the downloaded image.
    """
    name_image = url.split('/')[-2] + '_' + word + '.png'
    urllib.request.urlretrieve(url, outdir + name_image)


def get_pictos_per_doc(sentences, outdir):
    """
        Function to get the picto ids from the words and download the image.

        Arguments
        ---------
        sentences : list
            Sentences from the .csv file.
        outdir : str
            Directory where to store the downloaded images.

        Returns
        -------
        A list of list with picto ids per sentence.
    """
    all_ids = []
    for i, s in enumerate(sentences):
        dir_to_save = create_directory(outdir, str(i))
        ids_per_sentence = []
        for w in s:
            ids = get_ids_pictos_from_word(w)
            ids_per_sentence.append(ids)
            for e in ids:
                download_image('https://static.arasaac.org/pictograms/' + str(e) + '/' + str(e) + '_2500.png', w,
                               dir_to_save)
        all_ids.append(ids_per_sentence)
    return all_ids


def add_ids_to_data(ids, lemma_sent, csv_file):
    """
        Function to add the picto ids to the .csv file.

        Arguments
        ---------
        ids : list[list]
            Ids per sentence.
        lemma_sent : list[list]
            Lemmas per sentence.
        csv_file : str
            File where the data are stored.
    """
    data = pd.read_csv(csv_file, sep=',')
    pictos_ids = pd.DataFrame({'lemma': lemma_sent, 'pictos_all_ids': ids})
    data = data.merge(pictos_ids, left_index=True, right_index=True)
    data.to_csv('final_corpus_txt_pictos.csv', index=False)


def sentences_to_lemmas_and_picto_ids(args):
    """
        Function to get lemmas and picto ids per sentence and store it in .csv file.
    """
    sentences = get_sentences(args.csv_file)
    sent_prep = preprocessing(sentences)
    ids = get_pictos_per_doc(sent_prep, args.outdir)
    add_ids_to_data(ids, sent_prep, args.csv_file_out)


parser = ArgumentParser(description="From sentences, get the lemmas and possible linked picto ids."
                                    "A new .csv file will be created.",
                        formatter_class=RawTextHelpFormatter)
parser.add_argument('--csv_file', type=str, required=True,
                    help="Path of the .csv file.")
parser.add_argument('--outdir', type=str, required=True,
                    help="Path the directory to store the picto images per sentence.")
parser.add_argument('--csv_file_out', type=str, required=True,
                    help="Name of the .csv file with added information.")
parser.set_defaults(func=sentences_to_lemmas_and_picto_ids)
args = parser.parse_args()
args.func(args)
