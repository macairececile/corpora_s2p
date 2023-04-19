"""From a .csv data file with sentences, create the json with 50 random sentences to record in the LitDevTools.

Example of use:
python create_json_unige_platform.py --file all.csv --path_save ./all/

Author
 * Cécile MACAIRE 2023
"""

import pandas as pd
from argparse import ArgumentParser, RawTextHelpFormatter
import json
import os
import random


def read_datafile(file: str):
    """
        Function to read the .csv data into a dataframe.

        Arguments
        ---------
        file : str
            Path of the .csv datafile.

        Returns
        -------
        A dataframe.
    """
    return pd.read_csv(file, sep='\t')


def get_sentences(data):
    """
        Function to get the sentences of the dataframe into a list.

        Arguments
        ---------
        data : dataframe

        Returns
        -------
        A list with the sentences.
    """
    return data['sentence'].tolist()


def save_json_file(data: list, path_save: str, num_task: int):
    """
        Function to save the extracted data into a json file.

        Arguments
        ---------
        data : list
            List with sentences to record.
        path_save : str
            Path where to save the json generated file.
        num_task : int
            Number of the task.
    """
    with open(path_save + 'task_' + str(num_task) + '.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def create_json(sentences, path_save: str):
    """
        Function to create a json file from the data.

        Arguments
        ---------
        sentences : list
            List of the sentences of the data file.
        path_save : str
            Path where to save the json generated file.
    """
    if not os.path.isdir(path_save):
        os.makedirs(path_save)

    json_data = []
    sent_shuffle = random.sample(sentences, len(sentences))[:50]
    for i, j in enumerate(sent_shuffle):
        sentence = {"text": j, "file": "", "source": ""}
        json_data.append(sentence)
    save_json_file(json_data, path_save, 1)


def create_files_json_platform(args):
    """Function to create a json file for the platform."""
    data = read_datafile(args.file)
    sentences = get_sentences(data)
    create_json(sentences, args.path_save)


parser = ArgumentParser(description="Generate the json file for LitDevTool platform.",
                        formatter_class=RawTextHelpFormatter)
parser.add_argument('--file', type=str, required=True,
                    help="Path of the .csv file where sentences are stored to record.")
parser.add_argument('--path_save', type=str, required=True,
                    help="Path where to save the generated json file.")
parser.set_defaults(func=create_files_json_platform)
args = parser.parse_args()
args.func(args)
