

# Import the config file and set up logging 
import config 
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import csv
import nltk.data
import gensim.models
import re

def load_sentences(): 
	sentences = []
	with open("/home/andrew/lab_project/parsed_files/parsed_pets.csv") as f:
		r = csv.reader(f)
		for row in r: 
			sentences.append(row)
	return sentences

# sentences = load_sentences()

def minor_parse():
	with open("/home/andrew/lab_project/corpus/Pets.txt") as f: 
		with open("/home/andrew/lab_project/corpus/minor_pets.txt", 'w') as new_f:
			for line in f.readlines():
				new_f.write(re.sub("[^a-zA-Z \n]","", line))

minor_parse()

model = gensim.models.Word2Vec()

sentences = gensim.models.word2vec.LineSentence("/home/andrew/lab_project/corpus/minor_pets.txt")
model.build_vocab(sentences, keep_raw_vocab = True)
model.train(sentences)

# for sentence in sentences: 
#	print str(sentence)

# model.save('NAME.txt')

print model.n_similarity(['pet'], ['animal'])

sentences2 = gensim.models.word2vec.LineSentence("/home/andrew/lab_project/corpus/Artificial Intelligence.txt")
sentences2.sort()
model.build_vocab(sentences2, keep_raw_vocab = True)
model.train(sentences2)

print model.n_similarity(['pet'], ['animal'])
