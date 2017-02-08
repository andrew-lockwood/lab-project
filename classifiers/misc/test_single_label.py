
from single_label import run_classifier, get_original_data, get_redirect_data, model

def d2v_tester(keyword, num_tests, test):
    scores = []

    for i in range(num_tests):
        if i % 5 == 0: 
            print("On iteration: %i" % i)

        if test == 'redirect':
            data = get_redirect_data(keyword)
        if test == 'original':
            data = get_original_data(keyword)

        titles, targets = zip(*data)
        vectors = [model.docvecs[t] for t in titles]

        scores.append(run_classifier(vectors, targets)[0])

    print(sum(scores)/len(scores))

if __name__ == "__main__":
	kwd = "emotion"
	n = 5

	print("Scoring keyword: %s" % kwd)
	print("--------------------------")
	d2v_tester(kwd, n, 'redirect')

