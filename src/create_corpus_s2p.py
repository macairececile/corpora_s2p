"""From a directory with subdirectories with recordings downloaded from LitDevTools,
create a corpus by assigning an id to each speaker
and get the info to each recorded sentences from the data.csv to create the new corpus.

Example of use: python create_corpus_s2p.py --path_recordings ./all/recordings/recordings/ --path_data all.csv
--output corpus_parole_texte_pictos.csv

Author
 * Cécile MACAIRE 2023
"""

from utils import *
import os
import pandas as pd
import json
from argparse import ArgumentParser, RawTextHelpFormatter


def get_name_speakers(path_recordings):
    """
        Function to get the name of speakers (corresponding to the name of each subdirectories).

        Arguments
        ---------
        path_recordings : str
            Path of the recordings' folder.

        Returns
        -------
        A list with the name of each speaker.
    """
    return next(os.walk(path_recordings))[1]


def get_info_in_json(path_recordings, name_speaker):
    """
        Function to read the content of the json files generated from LitDevTools.

        Arguments
        ---------
        path_recordings : str
            Path of the folder where the recordings are stored.
        name_speaker : str
            Name of the speaker to access the subdirectory with the json file.

        Returns
        -------
        The json data.
    """
    with open(path_recordings + name_speaker + '/metadata_help.json', 'r') as f:
        return json.load(f)


def align_data(corpus_data, sentence):
    """
        Function to get the info of the recorded sentence from the dataframe.

        Arguments
        ---------
        corpus_data : dataframe
            Dataframe which contains the info in each sentence (picto ids, etc.).
        sentence : str
            Sentence from the json file.

        Returns
        -------
        A dict with the info from the dataframe corresponding to the searched sentence.
    """
    return corpus_data.loc[corpus_data["sentence"] == sentence].to_dict('records')[0]


def create_data_corpus_s2p(args):
    """
    Function to create the corpus with the name of the recorded file + speaker + the info from the recorded sentence.
    A .csv file is created with the name of the recorded file + speaker info + info of the recorded sentence.
    """
    data = {'path': [], 'speaker': [], 'speaker_id': [], 'doc_name': [], 'sentence': [], 'pictos_ref_ids': [],
            'sense_keys': []}
    corpus_data = read_csv(args.path_data)
    for i, speak in enumerate(get_name_speakers(args.path_recordings)):
        json_data = get_info_in_json(args.path_recordings, speak)
        for sent in json_data:
            request = align_data(corpus_data, sent['text'])
            data['path'].append(sent["file"])
            data['speaker'].append(speak)
            data['speaker_id'].append(str(i + 1))
            data["doc_name"].append(request["doc_name"])
            data["sentence"].append(sent["text"])
            data["pictos_ref_ids"].append(request["pictos_ref_ids"])
            data["sense_keys"].append(request["sense_keys"])
    df = pd.DataFrame(data)
    df.to_csv(args.output, index=False, sep='\t')


parser = ArgumentParser(description="Create a .csv file from recorded files of LitDevTools.",
                        formatter_class=RawTextHelpFormatter)
parser.add_argument('--path_recordings', type=str, required=True,
                    help="Path of the folder with the recorded files.")
parser.add_argument('--path_data', type=str, required=True,
                    help="Path of the .csv data with info for each sentence recorded.")
parser.add_argument('--output', type=str, required=True,
                    help="Path of the output .csv file generated.")
parser.set_defaults(func=create_data_corpus_s2p)
args = parser.parse_args()
args.func(args)
