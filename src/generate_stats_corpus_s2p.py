"""From a corpus with sentences, and associated picto, generates general statistics.

Example of use:
python generate_stats_corpus_s2p.py --datafile corpus.csv

Author
 * Cécile MACAIRE 2023
"""

from ast import literal_eval
import matplotlib.pyplot as plt
import seaborn as sns
import subprocess
import json
from utils import *
from argparse import ArgumentParser, RawTextHelpFormatter


def get_sentences_and_pictos(data):
    """
        Function to get the sentences and the picto ids.

        Arguments
        ---------
        data : dataframe
            Dataframe with the corpus info.

        Returns
        -------
        Two files, with sentences, and picto ids respectively.
    """
    sentences = data['sentence'].tolist()
    pictos = data['pictos_ref_ids'].apply(literal_eval).tolist()
    return sentences, pictos


def process_sentences(sentences, spacy_model):
    """
        Function to process the sentences by using a psacy model.

        Arguments
        ---------
        sentences : list
            List with the sentences.
        spacy_model : `spacy.lang.fr`
            Spacy model to lemmatize, etc.

        Returns
        -------
        A list of list with words per sentence.
    """
    words_lemmas_per_s = []
    for s in sentences:
        doc = spacy_model(s)
        word_lemma = []
        for word in doc:
            if word.text == "aujourd'hui":
                word_lemma.append(["aujourd'", "aujourd'", word.pos_])
                word_lemma.append(["hui", "hui", word.pos_])
            else:
                word_lemma.append([word.text, word.lemma_, word.pos_])
        words_lemmas_per_s.append(word_lemma)
    print("Unique words = vocab : ",
          str(len(list(set([element[1] for sous_liste in words_lemmas_per_s for element in sous_liste])))))
    return words_lemmas_per_s


def associate_words_with_pictos(words_lemmas, pictos):
    """
        Function to associate each word with their corresponding picto id.

        Arguments
        ---------
        words_lemmas : list
            List with the words.
        pictos : list
            List with the picto ids.

        Returns
        -------
        A list of list with words lemmas + picto ids.
    """
    for i, j in enumerate(pictos):
        for a, b in enumerate(j):
            if not b:
                words_lemmas[i][a].append(None)
            else:
                words_lemmas[i][a].append(b[0])
    return words_lemmas


def stats_pictos(words_lemmas_pictos):
    """
        Function to get some stats about the corpus (number of words in the corpus, etc.).
        The number of annotated words in picto by grammatical categories is also generated.

        Arguments
        ---------
        words_lemmas_pictos : list[list]
            List of list with words associated to their picto.
    """
    total_words = sum([len(elem) for elem in words_lemmas_pictos])
    average_words_pictos_corpus = 0
    grammatical_categories_total_words = {'NOUN': [0, 0], 'VERB': [0, 0], 'AUX': [0, 0], 'DET': [0, 0], 'CCONJ': [0, 0],
                                          'ADJ': [0, 0], 'ADP': [0, 0], 'PRON': [0, 0]}
    for i in words_lemmas_pictos:
        for el in i:
            if el[3] is not None:
                average_words_pictos_corpus += 1
            for k, v in grammatical_categories_total_words.items():
                if el[2] == k and el[3] is not None:
                    grammatical_categories_total_words[k] = [v[0] + 1, v[1] + 1]
                elif el[2] == k and el[3] is None:
                    grammatical_categories_total_words[k] = [v[0], v[1] + 1]

    print('-----------------------------\nNumber of words in the corpus : ' + str(total_words) + '\n'
                                                                                                 'Percentage number '
                                                                                                 'of words translated '
                                                                                                 'into pictograms : '
          + str(
        round(average_words_pictos_corpus / total_words, 2) * 100) + '%\n'
                                                                     '-----------------------------\n'
                                                                     'Percentage of words translated in pictograms by '
                                                                     'grammatical categories\n')
    for k, v in grammatical_categories_total_words.items():
        print(k + ' : ' + str(v[0] / v[1]) + '\n')
    plot_grammar(grammatical_categories_total_words)


def average_words_per_sentence(words_lemmas):
    """
        Function to get the average number of words per sentence.

        Arguments
        ---------
        words_lemmas : list
            List with the words.
    """
    print("Average number of words in sentences in the corpus : ",
          sum(map(len, words_lemmas)) / float(len(words_lemmas)))


def get_mwe(words_lem_pictos):
    """
        Function to get MWE words.

        Arguments
        ---------
        words_lem_pictos : list
            List with the words.

        Returns
        -------
        A list with MWE words.
    """
    mwe = []
    for i in words_lem_pictos:
        length_sentence = len(i)
        incr = 0
        mwe_exp = []
        for a, b in enumerate(i):
            if not mwe_exp:
                mwe_exp = [b[1]]
            while incr < length_sentence - 1:
                if len(mwe_exp) >= 2 and b[3] != i[a + 1][3]:
                    mwe.append(mwe_exp)
                    mwe_exp = []
                    incr += 1
                    break
                elif b[3] == i[a + 1][3] and b[3] is not None:
                    mwe_exp.append(i[a + 1][1])
                    incr += 1
                    break
                else:
                    incr += 1
                    mwe_exp = [i[incr][1]]
                    break
            else:
                if len(mwe_exp) >= 2:
                    mwe.append(mwe_exp)
    print(list(set([i for i in [' '.join(sub_list) for sub_list in mwe]])))
    return mwe


def get_percentage_similarity_lemma_picto(words_lem_pictos):
    """
        Function to get the words that are translated with non similar picto.

        Arguments
        ---------
        words_lem_pictos : list
            List with the words.

        Returns
        -------
        A list with the words not translated with the same picto.
    """
    unsimilar_picto_words = []
    num_words = 0
    for i in words_lem_pictos:
        for a, b in enumerate(i):
            if b[3] is not None:
                num_words += 1
                try:
                    command = 'curl -X GET "https://api.arasaac.org/api/pictograms/fr/' + str(b[
                                                                                                  3]) + '" -H ' \
                                                                                                        '"accept: ' \
                                                                                                        'application' \
                                                                                                        '/json" '
                    result = subprocess.check_output(command, shell=True).decode('UTF-8')
                    data = json.loads(result)
                    keywords = [k['keyword'] for k in data['keywords']]
                    if b[0] not in keywords and b[1] not in keywords:
                        unsimilar_picto_words.append([b[1], keywords])
                except Exception as e:
                    print("No pictogram : ", e)
    print("Percentage of words translated with non similar picto : ", len(unsimilar_picto_words) / num_words * 100)
    print(unsimilar_picto_words)
    return unsimilar_picto_words


def plot_grammar(grammatical_cat):
    """
        Function to generate a plot with matplolib with percentage of words translated in picto per pos tag.

        Arguments --------- grammatical_cat : dict Dictionary with, for each category, the number of words translated
        in picto and the number of total words with the pos tag.
    """
    values = []
    for k, v in grammatical_cat.items():
        values.append(v[0] / v[1])
    data = pd.DataFrame({'grammatical_categories': ['Noun', 'Verb', 'Auxiliary', 'Determiner', 'Conjonction',
                                                    'Adjective', 'Preposition', 'Pronoun'], 'percentage': values})
    data = data.sort_values(by=['percentage'], ascending=False)
    ax = sns.barplot(x='grammatical_categories', y='percentage',
                     data=data,
                     palette='Blues_d')
    ax.set_ylim(0, 0.95)
    plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right', fontsize='x-small')
    plt.title("Percentage of words in pictograms by grammatical categories")
    plt.show()


def pipeline(args):
    """
        Function to generate all stats from a corpus file.
    """
    spacy_model = spacy.load("fr_dep_news_trf")
    data = read_csv(args.datafile)
    sent, p = get_sentences_and_pictos(data)
    s = process_sentences(sent, spacy_model)
    words_lemmas = associate_words_with_pictos(s, p)
    get_mwe(words_lemmas)
    average_words_per_sentence(words_lemmas)
    # get_percentage_similarity_lemma_picto(words_lemmas)
    stats_pictos(words_lemmas)


parser = ArgumentParser(description="Extract the info from corpus and generate stats.",
                        formatter_class=RawTextHelpFormatter)
parser.add_argument('--datafile', type=str, required=True,
                    help="Datafile")
parser.set_defaults(func=pipeline)
args = parser.parse_args()
args.func(args)
