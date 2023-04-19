"""Convert a csv data file into a UFSAC format for WSD task.
The csv file should contain the following information :
...

Author
 * Cécile MACAIRE 2023
"""

import ast
from utils import *
import xml.etree.ElementTree as ET
from xml.dom import minidom
from argparse import ArgumentParser, RawTextHelpFormatter


class Word:
    """Class which defines a word with the corresponding information :
    surface_form, lemma, pos tag, sense key"""

    def __init__(self, surface_form, lemma, pos, wn30_key=None, id_word=None):
        self.surface_form = surface_form
        self.lemma = lemma
        self.pos = pos
        self.wn30_key = wn30_key
        self.id = id_word


def create_xml_file():
    """
        Function to create a xml file with the ET library.

        Returns
        -------
        root : `ET.element`
            root of the ET element
    """
    root = ET.Element("corpus")
    return root


def create_doc_and_paragraph_in_xml(root, doc_name):
    """
        Function to create the structure of the xlm file.

        Arguments
        ---------
        root : ET.Element
            Root of the xml file.
        doc_name : str
            Name of the document.

        Returns
        -------
        The subElement "paragraph" of the xml file which will contain the sentences.
    """
    doc = ET.SubElement(root, "document")
    doc.set("id", doc_name)
    parag = ET.SubElement(doc, "paragraph")
    return parag


def linguistic_processing(sentence):
    """
        Function to process the sentence (replacing some elements, removing non-necessary spaces).

        Arguments
        ---------
        sentence : str
            Sentence to process.

        Returns
        -------
        The processed sentence.
    """
    if type(sentence) == str:
        sentence = sentence.lower()
        particules = ['qu ', 'c ', 'd ', 'n ', ' hui', 'j ', 'l ', 's ', 't ']
        replacements = {' qu ': " qu'", ' c ': " c'", ' d ': " d'", ' n ': " n'", ' hui ': "'hui ", ' j ': " j'",
                        ' l ': " l'", ' s ': " s'", ' t ': " t'"}
        for el in particules:
            if sentence.startswith(el):
                sentence = sentence[:len(el)].replace(el, el[:-1] + "'") + sentence[len(el):]
        for k, v in replacements.items():
            sentence = sentence.replace(k, v)
    return sentence


def set_sentence_in_xml(parag, doc_name, index, row, spacy_model):
    """
        Function to add a sentence to the xml file with the word info.

        Arguments
        ---------
        parag : ET.SubElement
            Paragrah subElement of the xml file.
        doc_name : str
            Name of the doc of the xml.
        index : int
            Index of the sentence corresponding to the num sentence in the csv file.
        row : datarow
            Row of the dataframe which contains the info of the sentence.
        spacy_model : spacy.lang.fr.French
            Spacy model to tokenize, lemmatize the sentence.
    """
    sent = ET.SubElement(parag, "sentence")
    sent.set("id", doc_name + ".s" + str(index))
    words = []
    doc = spacy_model(linguistic_processing(row["sentence"]))
    sense_keys = ast.literal_eval(row['sense_keys'])
    id_word = 1
    for i, token in enumerate(doc):
        w = Word(token.text, token.lemma_, token.pos_)
        if sense_keys[i]:
            w.wn30_key = ';'.join(sense_keys[i])
            w.id = doc_name + ".s" + str(index) + '.t' + str(id_word)
            id_word += 1
            words.append(w)
        else:
            words.append(w)
    for w in words:
        word = ET.SubElement(sent, "word")
        word_els = {"surface_form": w.surface_form, "lemma": w.lemma, "pos": w.pos}
        if w.wn30_key:
            word_els["wn30_key"] = w.wn30_key
            word_els["id"] = w.id
        for k, v in word_els.items():
            word.set(k, v)


def add_info_to_xml_file_per_doc(data_from_csv, root, spacy_model):
    """
        Function to read the data from csv file and create the xml file with the infos for all doc.

        Arguments
        ---------
        data_from_csv : dataframe
            Dataframe with the csv data.
        root : ET.Element
            Root of the xml file.
        spacy_model : `spacy.lang`
            Spacy model to use.
    """
    by_doc = data_from_csv.groupby("doc_name")
    for name, group in by_doc:
        new_df = by_doc.get_group(name)
        parag = create_doc_and_paragraph_in_xml(root, name)
        for index, row in new_df.iterrows():
            set_sentence_in_xml(parag, name, index, row, spacy_model)


def add_info_to_xml_file_per_doc_v2(data_from_csv, root, spacy_model):
    """
        Function to read the data from csv file and create the xml file with the infos for 1 doc.

        Arguments
        ---------
        data_from_csv : dataframe
            Dataframe with the csv data.
        root : ET.Element
            Root of the xml file.
        spacy_model : `spacy.lang`
            Spacy model to use.
    """
    """Methode pour lire les données du csv récupérées des pdf annotés en pictos"""
    parag = create_doc_and_paragraph_in_xml(root, "doc1")
    for index, row in data_from_csv.iterrows():
        print(index)
        set_sentence_in_xml(parag, "doc1", index, row, spacy_model)


def create_ufsac_file(args):
    """Function to create the UFSAC xml file for a csv data file.
    It will create the xml file into the UFSAC format.
    """
    data_from_corpus = read_csv(args.csv_file)
    xml_file = args.csv_file.split('.csv')[0] + '.xml'
    root = create_xml_file()
    spacy_model = load_spacy_model("fr_dep_news_trf")
    if args.v1:
        add_info_to_xml_file_per_doc(data_from_corpus, root, spacy_model)
    else:
        add_info_to_xml_file_per_doc_v2(data_from_corpus, root, spacy_model)
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open(args.output_path + xml_file, "w") as f:
        f.write(xmlstr)


parser = ArgumentParser(description="Create an .xml file in UFSAC format from a .csv data file.",
                        formatter_class=RawTextHelpFormatter)
parser.add_argument('--csv_file', type=str, required=True,
                    help="Path of the .csv data file.")
parser.add_argument('--output_path', type=str, required=True,
                    help="Path to store the .xml file.")
parser.add_argument('--v1', type=bool, required=True,
                    help="Version to create an .xml file for all the documents.")
parser.set_defaults(func=create_ufsac_file)
args = parser.parse_args()
args.func(args)
