"""From the ARASAAC website, save the info of all french picto into json and download the picto .png files.

Example of use:
python get_all_pictos_arasaac_and_download_images.py --outdir ./images

Author
 * Cécile MACAIRE 2023
"""

import subprocess
import json
import urllib.request
from argparse import ArgumentParser, RawTextHelpFormatter

from utils import *


def get_ids_pictos_arasaac_from_json():
    """
        Function to get the info of all picto in json file and get all picto ids.

        Returns
        -------
        A list with all picto ids.
    """
    # get the json file of all pictos arasaac from the API
    command = 'curl -X GET "https://api.arasaac.org/api/pictograms/all/fr" -H "accept: application/json"'
    result = subprocess.check_output(command, shell=True).decode('UTF-8')  # run the MAUS command

    # save the output json in a file
    with open("/data/macairec/Cloud/PROPICTO_RESSOURCES/ARASAAC_Pictos_All/all_pictos_arasaac.json", 'w') as f:
        json.dump(result, f)

    # retrieve ids from json files
    data = json.loads(result)
    ids = [el['_id'] for el in data]
    return ids


def download_image(id_picto, outdir):
    """
        Function to download a picto .png from arasaac from the picto id.

        Arguments
        ---------
        id_picto : int
            Picto id.
        outdir : str
            Path of the directory to store the .png images.
    """
    url = 'https://static.arasaac.org/pictograms/' + str(id_picto) + '/' + str(id_picto) + '_2500.png'
    name_image = url.split('/')[-2] + '.png'
    urllib.request.urlretrieve(url, outdir + name_image)


def download_all_images(args):
    """Function to download all the images from arasaac and save them into a specific directory."""
    outdir = create_directory(args.outdir)
    ids = get_ids_pictos_arasaac_from_json()
    for i in ids:
        download_image(i, outdir)


parser = ArgumentParser(description="Download picto images from arasaac.",
                        formatter_class=RawTextHelpFormatter)
parser.add_argument('--outdir', type=str, required=True,
                    help="Path of the directory to store the images.")
parser.set_defaults(func=download_all_images)
args = parser.parse_args()
args.func(args)
