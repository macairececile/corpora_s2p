"""Utils methods that are used in scripts to create picto corpora.

Author
 * Cécile MACAIRE 2023
"""

import os
import pandas as pd
import spacy
from pathlib import Path

chars_to_ignore_regex = '[\,\?\.\!\-\;\:\"\“\%\‘\”\\n\-\_\'\…\[\]\&\(\)\*\/]'

special_char = ['à', 'â', 'ä', 'ç', 'è', 'é', 'ê', 'ë', 'î', 'ï', 'ô', 'ö', 'ù', 'û', 'ü']
equivalent = ['%C3%' + s for s in
              ['A0', 'A2', 'A4', 'A7', 'A8', 'A9', 'AA', 'AB', 'AE', 'AF', 'B4', 'B6', 'B9', 'BB', 'BC']]


def get_file_names(folder):
    """
        Function to get the names of file in a directory.

        Arguments
        ---------
        folder : str
            Path of the directory.

        Returns
        -------
        A list with the names of the files.
    """
    names = []
    for path, subdirs, files in os.walk(folder):
        for name in files:
            names.append(os.path.join(path, name).split('/')[-1][:-4])
    return names


def read_csv(path_data):
    """
        Function to read the data from the .csv file.

        Arguments
        ---------
        path_data : str
            Path of the .csv data file.

        Returns
        -------
        A pandas dataframe.
    """
    return pd.read_csv(path_data, sep='\t')


def load_spacy_model(model_name):
    """
        Function to load a spacy model given as input.

        Arguments
        ---------
        model_name : str
            Name of the spacy model to load

        Returns
        -------
        nlp : `spacy.lang`
            Loaded spacy model
    """

    # Load the spacy model
    try:
        nlp = spacy.load(model_name)
        print("*** Spacy model ready to use : " + model_name + " ***\n")
        return nlp

    # Raise exception
    except Exception as e:
        raise RuntimeError(e)


def create_directory(outdir, name=None):
    """
        Function to create a directory if it does not exist.

        Arguments
        ---------
        outdir : str
            Path of the directory to store the .png images.
        name : str
            Name of the folder if wanted to create.

        Returns
        -------
        A string with the path of the created directory.
    """
    if name:
        out = Path(outdir) / name
    else:
        out = Path(outdir)
    out.mkdir(exist_ok=True, parents=True)
    return str(out) + '/'


def parse_wn31_file(file):
    """
        Function to parse the Wordnet 3.1 file.

        Arguments
        ---------
        file : str
            Path of WordNet 3.1 file.

        Returns
        -------
        A dataframe with the wanted information.
    """
    return pd.read_csv(file, delimiter=" ", names=["sense_key", "synset", "id1", "id2"], header=None)


def get_sense_key_from_synset(wn31_data, synset_key):
    """
        Function to get the sense key(s) from a synset.

        Arguments
        ---------
        wn31_data : dataframe
            WordNet 3.1 data.
        synset_key : str
            String to look for.

        Returns
        -------
        A list with the possible sense key(s).
    """
    if not wn31_data.loc[wn31_data['synset'] == int(synset_key)]["sense_key"].tolist():
        return []
    else:
        return str(wn31_data.loc[wn31_data['synset'] == int(synset_key)]["sense_key"].tolist()[0])


def get_sense_keys_from_synset_wolf(wn31_data, picto_table, synset_wolf):
    """
        Function to get the sense key(s) from a synset.

        Arguments
        ---------
        wn31_data : dataframe
            WordNet 3.1 data.
        picto_table : dataframe
            Data from arasaac.fr
        synset_wolf : str
            String to look for.

        Returns
        -------
        A list with the possible sense key(s) for a given synset.
    """
    synset_ids_from_synset_wolf = list(
        set(picto_table.loc[picto_table['synset'] == synset_wolf]["synset2_proc"].tolist()))
    sense_keys = []
    for synset in synset_ids_from_synset_wolf:
        sense_key = get_sense_key_from_synset(wn31_data, synset)
        sense_keys.append(sense_key)
    return sense_keys


def get_sense_key_from_synset_2(synset, data_wn31):
    """
        Function to get the associated sense key(s) to the synset.

        Arguments
        ---------
        synset : str
        data_wn31 : dataframe
            Dataframe with the WordNet 3.1 infos.

        Returns
        -------
        An empty list or a list with sense key(s).
    """
    if synset != "" or synset != "0":
        synset_to_search = synset.split("-")[0]
        rows_with_synset = data_wn31.loc[data_wn31['synset'] == int(synset_to_search)]
        sense_keys = rows_with_synset["sense_key"].tolist()
        return sense_keys
    else:
        return [""]


def load_picto_table(filepath):
    """
    Function to load a pictogram table from a csv file.

    Arguments
    ---------
    filepath: str
        Path of the csv file containing the pictogram table

    Returns
    -------
    Dictionary containing the table with : lemma as key, list of pictogram information as value.
    """
    try:
        # Read the csv file with pandas
        df = pd.read_csv(filepath)

        picto_table = df[['idpicto', 'lemma', 'synset', 'synset2']]
        picto_table.loc[:, 'synset2_proc'] = picto_table['synset2'].apply(lambda a: a.split('-')[0])

        print("*** Pictogram table loaded : " + filepath + " ***\n")

        return picto_table

    except IOError:
        print("Could not read file, wrong file format.", filepath)
        return
