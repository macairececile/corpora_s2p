"""From a corpus csv file with sentences and picto ids, get and add the corresponding sense keys.

Example of use:
python get_sense_keys.py --datafile ./corpus.csv --data_wn31 index.sense --outfile corpus_senses.csv

Author
 * Cécile MACAIRE 2023
"""

import subprocess
import json
from utils import *
from argparse import ArgumentParser, RawTextHelpFormatter


def get_annot_picto_ids(data):
    """
        Function to get picto ids from dataframe.

        Arguments
        ---------
        data : dataframe
            Data from the corpus

        Returns
        -------
        A list with the json files corresponding to each picto ids.
    """
    return [json.loads(i) for i in data['pictos_ref_ids'].tolist()]


def get_synsets_from_arasaac(id_picto):
    """
        Function to get the synset id from a picto id.

        Arguments
        ---------
        id_picto : int
            Picto id.

        Returns
        -------
        A list with the synset(s).
    """
    try:
        command = 'curl -X GET "https://api.arasaac.org/api/pictograms/fr/' + str(
            id_picto) + '" -H "accept: application/json"'
        result = subprocess.check_output(command, shell=True).decode('UTF-8')
        json_data = json.loads(result)
        return json_data["synsets"]
    except Exception as e:
        raise RuntimeError(e)


def get_synsets_from_ids_and_add_sense_keys(ids_picto, data_wn31):
    """
        Function to get the synset ids and add sense key(s) from picto ids.

        Arguments
        ---------
        id_picto : int
            Picto id.
        data_wn31 : dataframe
            Data from wordnet3.1.

        Returns
        -------
        A list with the sense keys per sentence.
    """
    all_sense_keys = []
    for sentence in ids_picto:
        sense_keys_per_sentence = []
        for id in sentence:
            if id:
                sense_keys = []
                for el in id:
                    synsets = get_synsets_from_arasaac(el)
                    for s in synsets:
                        sense_keys_picto = get_sense_key_from_synset_2(s, data_wn31)
                        sense_keys.extend(sense_keys_picto)
                sense_keys_per_sentence.append(sense_keys)  # ajoute les sense_keys par picto
            else:
                sense_keys_per_sentence.append([])
        all_sense_keys.append(sense_keys_per_sentence)
    return all_sense_keys


def add_sense_keys_to_data(args):
    """
        Function to add the sense key(s) to the dataframe and create a new csv file.
    """
    data_from_corpus = read_csv(args.datafile)
    picto_ids = get_annot_picto_ids(data_from_corpus)
    wn31_data = parse_wn31_file(args.data_wn31)
    sense_keys = get_synsets_from_ids_and_add_sense_keys(picto_ids, wn31_data)
    data_from_corpus["sense_keys"] = sense_keys
    data_from_corpus.to_csv(args.outfile, index=False, sep='\t')


parser = ArgumentParser(description="Add sense keys to corpus file with sentences and picto ids.",
                        formatter_class=RawTextHelpFormatter)
parser.add_argument('--datafile', type=str, required=True,
                    help="Path of the data file.")
parser.add_argument('--data_wn31', type=str, required=True,
                    help="Path of file with wordnet3.1 infos.")
parser.add_argument('--outfile', type=str, required=True,
                    help="Name of the new data file generated.")
parser.set_defaults(func=add_sense_keys_to_data)
args = parser.parse_args()
args.func(args)
