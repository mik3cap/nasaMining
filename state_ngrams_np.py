from __future__ import unicode_literals
import json
from gensim.models.phrases import Phrases
from textblob import TextBlob


states = ['colorado', 'hawaii', 'illinois', 'iowa', 'maine', 'maryland', 'michigan', 'nj', 'ny', 'oregon', 'texas', 'vermont']

# from gensim: threshold represents a threshold for forming the phrases (higher means fewer phrases).
# A phrase of words a and b is accepted if (cnt(a, b) - min_count) * N / (cnt(a) * cnt(b)) > threshold, where N is the total vocabulary size.
thresh = 10
# n = 5

if __name__ == '__main__':
    dataset = []
    desc = []
    doc_id = []

    print 'Tokenizing state descriptions'
    for n, state in enumerate(states):
        data = json.load(open('data/%s.json' % state))['dataset']

        print '\t%s' % state

        for i, ds in enumerate(data):
            ds['source'] = 'http://data.%s.gov/data.json' % state
            text = TextBlob(ds['description'])
            for sentence in text.sentences:
                desc.append(sentence.tokens)
                # doc_id.append(i)
                doc_id.append(len(dataset))

            dataset.append(ds)

    desc_nasa = []
    nasa_data = json.load(open('data/nasa.json'))['dataset']
    print 'Tokenizing NASA descriptions'
    for i, ds in enumerate(nasa_data):
        text = TextBlob(ds['description'])
        for sentence in text.sentences:
            desc_nasa.append(sentence.tokens)

    print 'Constructing ngrams'

    print 'Bigrams'
    # desc_bigrams = Phrases(desc, threshold=thresh)
    desc_bigrams = Phrases(desc + desc_nasa, threshold=thresh)
    bigrams = desc_bigrams[desc]

    print 'Trigrams'
    desc_trigrams = Phrases(bigrams, threshold=thresh)
    trigrams = desc_trigrams[bigrams]

    print 'Fourgrams'
    desc_fourgrams = Phrases(trigrams, threshold=thresh)
    fourgrams = desc_fourgrams[trigrams]

    print 'Fivegrams'
    desc_fivegrams = Phrases(fourgrams, threshold=thresh)
    fivegrams = desc_fivegrams[fourgrams]

    # pull out keywords
    print 'Extracting keywords'

    field = 'description_ngram_np'

    for i, ngram in enumerate(fivegrams):
        doc = doc_id[i]

        if field not in dataset[doc]:
            dataset[doc][field] = set()

            if doc > 0 and doc % 1000 == 0:
                print '\t', doc

        for kw in filter(lambda k: '_' in k, ngram):
            keyword = kw.replace('_', ' ')

            kw_tb = TextBlob(keyword)

            # filter out punctuation, etc (make sure that there are two non-punc words)
            if len(kw_tb.words) < 2:
                continue

            # add keywords which are all proper nouns
            distinct_tags = set(t[1] for t in kw_tb.tags)
            if distinct_tags - {'NNP', 'NNPS'} == {}:
                dataset[doc][field].add(kw_tb.lower())
                continue

            # add noun phrases
            for np in kw_tb.lower().noun_phrases:
                dataset[doc][field].add(np)

    # convert set into list for json serialization
    for d in dataset:
        d[field] = list(d[field])

        # fix 's
        for i, np in enumerate(d[field]):
            if np.endswith(" 's"):
                np = np[:-3]

            if np.startswith("'s "):
                np = np.replace("'s ", "", 1)

            np = np.replace(" 's", "'s")

            d[field][i] = np
        d[field] = list(set(d[field]))

    with open('data/states_ngram_np.json', 'w') as f:
        json.dump(dataset, f)