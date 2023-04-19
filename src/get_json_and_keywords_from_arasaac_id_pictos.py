"""From the Arasaac png images, get the keywords info and store it in a .csv file.

Example of use:
python get_json_and_keywords_from_arasaac_id_pictos.py --picto_png ./png/ --outdir ./out/ --outfile pictos.csv

Author
 * Cécile MACAIRE 2023
"""

import json
import subprocess
from os import listdir
from os.path import isfile, join
import pandas as pd
from argparse import ArgumentParser, RawTextHelpFormatter


def get_files_from_directory(path_picto_ids):
    """
        Function to get name of the files in a directory with .png extension.

        Arguments
        ---------
        path_picto_ids : str
            Path of stored .png files.

        Returns
        -------
        A list with the name of each .png file.
    """
    return [f for f in listdir(path_picto_ids) if isfile(join(path_picto_ids, f)) and f.endswith(".png")]


def get_data_from_picto(name_file, output_path):
    """
        Function to get the json info associated to the picto id and retrieve the keywords.

        Arguments
        ---------
        name_file : str
            Name of the .png file.
        output_path : str
            Directory to store the json file linked to a picto id.

        Returns
        -------
        A list with the picto id and the associated keywords.
    """
    id_picto = name_file.split('/')[-1].split('.png')[0]
    command = 'curl -X GET "https://api.arasaac.org/api/pictograms/fr/' + str(
        id_picto) + '" -H "accept: application/json"'
    result = subprocess.check_output(command, shell=True).decode('UTF-8')
    with open(output_path + id_picto + '.json', "w") as f:
        f.write(result)
    data = json.loads(result)
    keywords = [k['keyword'] for k in data['keywords']]
    if not keywords:
        return id_picto, ""
    else:
        return id_picto, keywords[0]


def get_all_data_from_arasaac_and_save_in_csv(args):
    """
        Function to get the json info associated to all picto ids and retrieve the keywords.
        The info are saved in a .csv file.
    """
    all_id_pictos = []
    all_keywords = []
    files = get_files_from_directory(args.picto_png)
    for f in files:
        print("File : ", f)
        id_picto, k = get_data_from_picto(f, args.outdir)
        all_id_pictos.append(id_picto)
        all_keywords.append(k)

    # save in csv file
    data = {'id_picto': all_id_pictos, 'keyword': all_keywords}
    dataframe = pd.DataFrame.from_dict(data)
    dataframe.to_csv(args.outfile, index=False, sep='\t')


parser = ArgumentParser(
    description="Create a .csv file with each id picto linked to their keywords, and saved all json from arasaac.",
    formatter_class=RawTextHelpFormatter)
parser.add_argument('--picto_png', type=str, required=True,
                    help="Path of the json files from arasaac.")
parser.add_argument('--outdir', type=str, required=True,
                    help="Path of the directory to store the json files.")
parser.add_argument('--outfile', type=str, required=True,
                    help="Path of the csv file with info.")
parser.set_defaults(func=get_all_data_from_arasaac_and_save_in_csv)
args = parser.parse_args()
args.func(args)
