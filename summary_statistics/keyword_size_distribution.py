from data_generator import KeywordData
import matplotlib.pyplot as plt
import numpy as np

data = KeywordData()

def distinct_ngram_graph():
    width = 0.35

    distinct_ngram_counts = data.kwd_grams(True)
    sorted(distinct_ngram_counts.items())

    d_counts = []
    X = []
    for gram, count in distinct_ngram_counts.items():
        if gram <= 5: 
            X.append(gram)
            d_counts.append(count)

    absolute_ngram_counts = data.kwd_grams(False)
    sorted(absolute_ngram_counts.items())

    a_counts = []
    for gram, count in absolute_ngram_counts.items():
        if gram <= 5: 
            a_counts.append(count)

    X = np.array(X)

    fig, ax = plt.subplots()

    g1 = ax.bar(X, proportion(d_counts), width, color='b')
    g2 = ax.bar(X+width, proportion(a_counts), width, color='r')

    ax.set_title("Distribution of the Number of Words in a Keyword")
    ax.set_ylabel("Proportion of Keywords")

    ax.set_xticks(X+width/2)
    ax.set_xlabel("Length of a Keyword")
    ax.set_xticklabels(X)

    ax.legend((g1[0],g2[0]), ("distinct","absolute"))

    plt.show()

def proportion(data):
    total = sum(data)
    prop = [d/total for d in data]
    return prop

distinct_ngram_graph()

