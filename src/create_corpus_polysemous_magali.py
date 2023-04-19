"""From the file polysemous_words.csv of Magali, create a .csv file with the wanted information.

Example of use: python create_corpus_polysemous_magali.py --csv_file polysemous.csv --data_arasaac arasaac.fre30.bis.csv
--data_wn31 index.sense --outfile corpus.csv

Author
 * Cécile MACAIRE 2023
"""

import ast
from argparse import ArgumentParser, RawTextHelpFormatter
from utils import *


def create_data_for_sentence(picto_table, wn_table, model, sentence, wolf_senses, picto_id, word_to_wsd, sentences,
                             sentences_in_picto, sentences_in_senses):
    """
        Function to get the sentences in picto and in sense keys.

        Arguments
        ---------
        picto_table : dataframe
            Data with the arasaac picto information.
        wn_table : dataframe
            Data from WordNet 3.1 data.
        model : `spacy.lang.fr`
            Spacy model used.
        sentence : str
            Sentence to process with spacy.
        wolf_senses : str
            Synset from the data.
        picto_id : str
            Id of the picto
        word_to_wsd : str
        sentences : list
            List which will contain the sentences.
        sentences_in_picto : list
            List which will contain the sentences in picto.
        sentences_in_senses : list
            List which will contain the sentences in sense key(s).

        Returns
        -------
        The three list with sentences, sentences in picto, and sentences in senses.
    """
    wolf_senses = wolf_senses.split('_')

    all_sense_keys = []
    for w_sense in wolf_senses:
        all_sense_keys.extend(get_sense_keys_from_synset_wolf(wn_table, picto_table, w_sense))

    doc = model(sentence)

    sentence_in_picto = []
    sentence_in_senses = []

    for token in doc:
        if token.lemma_ != " " and token.lemma_ != "'":
            print("Lemma : ", token.lemma_)
            if word_to_wsd == token.lemma_:
                sentence_in_picto.append(ast.literal_eval(picto_id))
                sentence_in_senses.append(all_sense_keys)
            else:
                sentence_in_picto.append([])
                sentence_in_senses.append([])

    sentences.append(sentence)
    sentences_in_picto.append(sentence_in_picto)
    sentences_in_senses.append(sentence_in_senses)


def create_data(args):
    corpus_magali = pd.read_csv(args.csv_file, sep='\t')

    nlp = load_spacy_model("fr_dep_news_trf")
    picto_table = load_picto_table(args.data_arasaac)
    wn_table = parse_wn31_file(args.data_wn31)

    sentences = []
    sentences_in_picto = []
    sentences_in_senses = []

    for index, row in corpus_magali.iterrows():
        word_to_disambiguate = row["wordToDisambiguate"]
        sentence = row["sentence1"]
        picto_id = row["sense1_pictoID_correct_arasaac"]
        wolf_sense = row["sense_wolf_correct"]
        create_data_for_sentence(picto_table, wn_table, nlp, sentence, wolf_sense, picto_id, word_to_disambiguate,
                                 sentences, sentences_in_picto, sentences_in_senses)
        if not pd.isna(row["sentence2"]):
            sentence2 = row["sentence2"]
            create_data_for_sentence(picto_table, wn_table, nlp, sentence2, wolf_sense, picto_id, word_to_disambiguate,
                                     sentences, sentences_in_picto, sentences_in_senses)
        if not pd.isna(row["sentence3"]):
            sentence3 = row["sentence3"]
            create_data_for_sentence(picto_table, wn_table, nlp, sentence3, wolf_sense, picto_id, word_to_disambiguate,
                                     sentences, sentences_in_picto, sentences_in_senses)
        if not pd.isna(row["sentence4"]):
            sentence4 = row["sentence4"]
            create_data_for_sentence(picto_table, wn_table, nlp, sentence4, wolf_sense, picto_id, word_to_disambiguate,
                                     sentences, sentences_in_picto, sentences_in_senses)
        if not pd.isna(row["sentence5"]):
            sentence5 = row["sentence5"]
            create_data_for_sentence(picto_table, wn_table, nlp, sentence5, wolf_sense, picto_id, word_to_disambiguate,
                                     sentences, sentences_in_picto, sentences_in_senses)
        if not pd.isna(row["sentence6"]):
            sentence6 = row["sentence6"]
            create_data_for_sentence(picto_table, wn_table, nlp, sentence6, wolf_sense, picto_id, word_to_disambiguate,
                                     sentences, sentences_in_picto, sentences_in_senses)

    data = {'sentence': sentences, 'pictos_ref_ids': sentences_in_picto, 'sense_keys': sentences_in_senses}
    dataframe = pd.DataFrame.from_dict(data)
    dataframe.to_csv(args.outfile, index=False, sep='\t')


parser = ArgumentParser(description="Generate a .csv file from the polysemous data in the correct format.",
                        formatter_class=RawTextHelpFormatter)
parser.add_argument('--csv_file', type=str, required=True,
                    help="Path of the polysemous.csv file.")
parser.add_argument('--data_arasaac', type=str, required=True,
                    help="Path of the arasaac.fre30bis.csv file.")
parser.add_argument('--data_wn31', type=str, required=True,
                    help="Path of index.sense file.")
parser.add_argument('--outfile', type=str, required=True,
                    help="Path to store the generated .csv file.")
parser.set_defaults(func=create_data)
args = parser.parse_args()
args.func(args)
