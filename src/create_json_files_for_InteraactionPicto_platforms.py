"""From the ARASAAC json file per picto, you can create 4 files for InteraactionPicto platforms:
** names.json : only the keyword from arasaac.
** synsets.json : each synset is linked to the possible id picto.
** names2.json : each possible word annotated to picto (keywords).
** synsets_fr.json : each word is associated to their possible synsets.

Example of use: python create_json_files_for_InteraactionPicto_platforms.py --arasaac_jsons ./arasaac_jsons/
--wolf_data ./arasaac.fr.csv --data_wn31 index.sense --type 1

Author
 * Cécile MACAIRE 2023
"""

import json
from os import listdir
from os.path import isfile, join
from nltk.corpus import wordnet as wn
from utils import *
from argparse import ArgumentParser, RawTextHelpFormatter


def get_json_from_directory(path_picto_ids):
    """
        Function to get the name of all the json files saved from arasaac.

        Arguments
        ---------
        path_picto_ids : str
            Path of stored json files.

        Returns
        -------
        A list with the name each json file.
    """
    return [f for f in listdir(path_picto_ids) if isfile(join(path_picto_ids, f)) and f.endswith(".json")]


def get_data_from_wolf(wolf_data):
    """
        Function to parse the data from arasaac.fre30.bis file.

        Arguments
        ---------
        wolf_data : str
            Path of arasaac.fre30.bis file.

        Returns
        -------
        A dataframe with the wanted information.
    """
    df = pd.read_csv(wolf_data, delimiter=',')
    picto_table = df[['lemma', 'synset2', "lemma_plural"]]
    # picto_table.loc[:, 'synset2_proc'] = picto_table['synset2'].apply(lambda a: a.split('-')[0])
    return picto_table


def get_lemma_from_wolf_and_corresponding_synsets(picto_table, data_wn31):
    """
        Function to get the lemma and the corresponding sense keys from arasaac.fr table.

        Arguments
        ---------
        picto_table : dataframe
            Dataframe with the info of arasaac pictos.
        data_wn31 : dataframe
            Dataframe with the info of wordnet3.1.

        Returns
        -------
        A dict with each lemma associated with their synsets.
    """
    results = {}
    for index, row in picto_table.iterrows():
        if isinstance(row["lemma"], float):
            lemma = ''
        else:
            lemma = row["lemma"].split('_')
            if lemma[-1].isdigit():
                lemma = ' '.join(lemma[:-1])
            else:
                lemma = ' '.join(lemma)
        plural = ''
        if row["lemma_plural"] != r"\N":
            plural = ' '.join(row["lemma_plural"].split('_'))
        sense_keys = get_sense_key_from_synset(row["synset2"], data_wn31)
        for sense in sense_keys:
            try:
                synset = wn.synset_from_sense_key(sense).name()
                for word in [lemma, plural]:
                    if word != '':
                        results.setdefault(word, []).append(synset)
                # if lemma != '':
                #     if lemma not in results.keys():
                #         results[lemma] = [synset]
                #     else:
                #         results[lemma].append(synset)
                # if plural != '':
                #     if plural not in results.keys():
                #         results[plural] = [synset]
                #     else:
                #         results[plural].append(synset)
            except Exception as e:
                print("No synset found for ", e)
    return results


def get_sense_key_from_synset(synset, data_wn31):
    """
        Function to get the sense key(s) associated to the synset.

        Arguments
        ---------
        synset : str
        data_wn31 : dataframe
            Dataframe with the info of wordnet3.1.

        Returns
        -------
        A list with sense key(s) or empty string.
    """
    if synset not in ["", r"\N", 'None', 'closed']:
        synset_to_search = synset.split("-")[0]
        rows_with_synset = data_wn31.loc[data_wn31['synset'] == int(synset_to_search)]
        sense_keys = rows_with_synset["sense_key"].tolist()
        return sense_keys
    else:
        return [""]


def get_data_from_picto(file, saved_data: dict):
    """
        Function to get the keywords with corresponding picto ids from json file.

        Arguments
        ---------
        file : str
            Json file with the info of an arasaac picto.
        saved_data : dict
            Dict with, for each keyword, the corresponding picto id.
    """
    with open(file, 'r') as f:
        data = json.load(f)
    _id = data['_id']
    keywords = []
    if "keyword" in data["keywords"].__str__():
        for keyword in data['keywords']:
            keywords.append(keyword['keyword'])
            if "plural" in keyword:
                keywords.append(keyword['plural'])
    for key in keywords:
        if key not in saved_data.keys():
            saved_data[key] = [_id]
        else:
            saved_data[key].append(_id)


def get_data_synsets_from_picto(file, data_wn31, saved_data: dict):
    """
        Function to get the corresponding sense key(s) from a synset in json file.

        Arguments
        ---------
        file : str
            Json file with the info of an arasaac picto.
        data_wn31 : dataframe
            Dataframe with the info of wordnet3.1.
        saved_data : dict
            Dict with, for each sense key, the corresponding picto id.
    """
    with open(file, 'r') as f:
        data = json.load(f)
    _id = data['_id']
    synsets = data["synsets"]
    for s in synsets:
        if s != "closed":
            sense_keys = get_sense_key_from_synset(s, data_wn31)
            for sense in sense_keys:
                try:
                    synset = wn.synset_from_sense_key(sense).name()
                    if synset not in saved_data.keys():
                        saved_data[synset] = [_id]
                    else:
                        saved_data[synset].append(_id)
                except Exception as e:
                    print("No synset found for ", e)


def create_json_file_with_keywords_and_pictos(path_picto_ids):
    """
        Function to create the names.json file.

        Arguments
        ---------
        path_picto_ids : str
            Path of the json file with arasaac picto info.
    """
    files = get_json_from_directory(path_picto_ids)
    saved_data = {}
    for f in files:
        get_data_from_picto(path_picto_ids + f, saved_data)
    for k, v in saved_data.items():
        v = list(set(v))
        saved_data[k] = v
    # with open("keywords_pictos.json", "w") as f:
    #     json.dump(saved_data, f)
    only_keywords = list(saved_data.keys())
    with open("names.json", "w") as f2:
        json.dump(only_keywords, f2)


def create_synsets_from_arasaac(path_picto_ids, data_wn31):
    """
        Function to create the synsets.json file.

        Arguments
        ---------
        path_picto_ids : str
            Path of the json file with arasaac picto info.
        data_wn31 : dataframe
            Dataframe with the info of wordnet3.1.
    """
    data_wn = parse_wn31_file(data_wn31)
    files = get_json_from_directory(path_picto_ids)
    saved_data = {}
    for f in files:
        get_data_synsets_from_picto(path_picto_ids + f, data_wn, saved_data)
    for k, v in saved_data.items():
        v = list(set(v))
        saved_data[k] = v
    with open("synsets.json", "w") as f:
        json.dump(saved_data, f)


def associate_words_with_synsets_from_wolf(wolf_data, data_wn31):
    """
        Function to create the synsets_fr.json + names2.json files.

        Arguments
        ---------
        wolf_data : str
            Path of the arasaac.fre .csv file.
        data_wn31 : dataframe
            Dataframe with the info of wordnet3.1.
    """
    data_wn = parse_wn31_file(data_wn31)
    data_picto = get_data_from_wolf(wolf_data)
    results = get_lemma_from_wolf_and_corresponding_synsets(data_picto, data_wn)
    for k, v in results.items():
        v = list(set(v))
        results[k] = v
    names = list(results.keys())
    with open("synsets_fr.json", "w") as f:
        json.dump(results, f)
    with open("names2.json", "w") as f2:
        json.dump(names, f2)


def choose_jsons(args):
    """Choose which type of json files to generate."""
    if args.type == 1:
        create_json_file_with_keywords_and_pictos(args.arasaac_jsons)
    elif args.type == 2:
        create_synsets_from_arasaac(args.arasaac_jsons, args.data_wn31)
    elif args.type == 3:
        associate_words_with_synsets_from_wolf(args.wolf_data, args.data_wn31)
    else:
        create_json_file_with_keywords_and_pictos(args.arasaac_jsons)


parser = ArgumentParser(description="Create different json files for InteraactionPicto platforms.",
                        formatter_class=RawTextHelpFormatter)
parser.add_argument('--arasaac_jsons', type=str, required=True,
                    help="Path of the json files from arasaac.")
parser.add_argument('--wolf_data', type=str, required=True,
                    help="Path of the .csv data with info of arasaac.")
parser.add_argument('--data_wn31', type=str, required=True,
                    help="Path of file with wordnet3.1 infos.")
parser.add_argument('--type', type=int, required=True, choices=[1, 2, 3],
                    help="Type of the json files to generate.")
parser.set_defaults(func=choose_jsons)
args = parser.parse_args()
args.func(args)
