"""Convert a .txt file into a .csv file (from Magali's corpora).

The ref .txt file is structured as :
<refset setid="devtest" srclang="Arasaac" trglang="French">
<DOC docid="emails" sysid="orig">
<seg>comment être tes frère ?</seg>
<seg>_ _ _ Camille être ton amie ?</seg>

The source .txt file is structured as :
<srcset setid="devtest" srclang="Arasaac" trglang="French">
<DOC docid="emails">
<seg>comment vont tes frères ?</seg>
<seg>est ce que Camille est ton amie ?</seg>

Example of use by command line : python create_corpus_from_eval_magali.py --source_file Tst_Source_Arasaac.txt
--ref_file Tst_Ref_Arasaac.txt --data_arasaac arasaac.fre30bis.csv --data_wn31 index.sense name_csv name.csv

Author
 * Cécile MACAIRE 2023
"""

import string
import re
import csv
from argparse import ArgumentParser, RawTextHelpFormatter
from utils import *


def read_tsv_file(tsv_file):
    """
        Function to read the data into a dataframe from arasaac.fre30bis.

        Arguments
        ---------
        tsv_file : str
            Path of the .tsv file.

        Returns
        -------
        A pandas dataframe with the data.
    """
    data = pd.read_csv(tsv_file, sep=',')
    data["synset2"] = data["synset2"].replace("\\N", "0")
    return data


def read_txt_file(txt_file):
    """
        Function to read the .txt file with the annotated data.

        Arguments
        ---------
        txt_file : str
            Path of the .txt file.

        Returns
        -------
        The content of the .txt file.
    """
    with open(txt_file, "r") as f:
        # Lire le contenu du fichier
        content = f.read()

        # Extraire le contenu de chaque balise <seg>
        seg_regex = re.compile(r"<seg>(.*?)</seg>")
        seg_contents = seg_regex.findall(content)

        return seg_contents


def read_source_ref_txt_file(source_file, ref_file):
    """
        Function to read the .txt file from both source and reference and process the content.

        Arguments
        ---------
        source_file : str
            Path of the .txt source file.
        ref_file : str
            Path of the .txt reference file.

        Returns
        -------
        The processing content of both source and reference .txt file.
    """
    source_content = read_txt_file(source_file)
    ref_content = read_txt_file(ref_file)

    # remove punctuation in source content + "-" and extra spaces
    exclude = set(string.punctuation) - set('-') - set("'")
    source_content = [re.sub(' +', ' ', "".join([char for char in s if char not in exclude])).lower() for s
                      in source_content]

    # remove specific punctuation marks in reference
    to_remove = [" !", " ?"]
    f = []
    for s in ref_content:
        for a in to_remove:
            s = s.replace(a, "")
        f.append(s)
    ref_content = [re.sub(' +', ' ', s) for s in f]

    return source_content, ref_content


def get_picto_and_synsets_from_ref_content_sentence(ref_sentence, data_wn31, data_arasaac):
    """
        Function to get the corresponding picto ids and sense keys from reference sentence lemmas.

        Arguments
        ---------
        ref_sentence : str
            Reference sentence.
        data_wn31 : dataframe
            Dataframe with the WordNet 3.1 infos.
        data_arasaac : dataframe
            Dataframe with the arasaac.fre30 infos.

        Returns
        -------
        The id pictos and sense key(s) to each lemma of the reference sentence.
    """
    ids_picto = []
    senses_per_pictos = []
    lemmas_picto = ref_sentence.split(" ")
    for l in lemmas_picto:
        ids_picto.append(list(set(data_arasaac.loc[data_arasaac["lemma"] == l]["idpicto"].tolist())))
        synset = data_arasaac.loc[data_arasaac["lemma"] == l]["synset2"].tolist()
        senses = list(
            set([element for sous_liste in [get_sense_key_from_synset_2(s, data_wn31) for s in synset] for element in
                 sous_liste]))
        senses_per_pictos.append(senses)
    return ids_picto, senses_per_pictos


def get_id_picto_and_senses_corpus(source_content, ref_content, data_arasaac, data_wn31):
    """
        Function to get the corresponding picto ids and sense keys from the sentences of the corpus.

        Arguments
        ---------
        source_content : list[str]
            Source sentence.
        ref_content : list[str]
            Reference sentence.
        data_arasaac : dataframe
            Dataframe with the arasaac.fre30 infos.
        data_wn31 : dataframe
            Dataframe with the WordNet 3.1 infos.

        Returns
        -------
        Return a dict with, for each source sentence, the id pictos and sense key(s) of each lemma.
    """
    infos = {}
    for i, s in enumerate(ref_content):
        id_pictos, senses = get_picto_and_synsets_from_ref_content_sentence(s, data_wn31, data_arasaac)
        infos[source_content[i]] = [id_pictos, senses]
    return infos


def create_csv_file_from_infos(infos, name_csv):
    """
        Function to create a .csv file from the info of the .txt file.

        Arguments
        ---------
        infos : dict
            Dict with, for each source sentence, the id pictos and sense key(s) of each lemma.
        name_csv : str
            Name of the .csv file which will be created.

    It will create a .csv file with the corresponding information.
    """
    with open(name_csv, 'w', newline='') as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(['sentence', 'pictos_ref_ids', 'sense_keys'])
        for key, value in infos.items():
            writer.writerow([key, value[0], value[1]])


def create_corpus(args):
    """
        Function to create the corpus in .csv format from source and reference .txt files.
        It will create a .csv file with the corresponding information.
    """
    source_content, ref_content = read_source_ref_txt_file(args.source_file, args.ref_file)
    data_wn31 = parse_wn31_file(args.data_wn31)
    data_arasaac = read_tsv_file(args.data_arasaac)

    corpus = get_id_picto_and_senses_corpus(source_content, ref_content, data_arasaac, data_wn31)

    create_csv_file_from_infos(corpus, args.name_csv)


parser = ArgumentParser(description="Create a .csv file from source and reference .txt files.",
                        formatter_class=RawTextHelpFormatter)
parser.add_argument('--source_file', type=str, required=True,
                    help="Path of the source file.")
parser.add_argument('--ref_file', type=str, required=True,
                    help="Path of the reference file.")
parser.add_argument('--data_arasaac', type=str, required=True,
                    help="Path of the arasaac.fre30bis.csv file.")
parser.add_argument('--data_wn31', type=str, required=True,
                    help="Path of index.sense file.")
parser.add_argument('--name_csv', type=str, required=True,
                    help="name of the output .csv file.")
parser.set_defaults(func=create_corpus)
args = parser.parse_args()
args.func(args)
