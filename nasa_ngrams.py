from __future__ import unicode_literals
import json
from gensim.models.phrases import Phrases
from textblob import TextBlob


# from gensim: threshold represents a threshold for forming the phrases (higher means fewer phrases).
# A phrase of words a and b is accepted if (cnt(a, b) - min_count) * N / (cnt(a) * cnt(b)) > threshold, where N is the total vocabulary size.
thresh = 10
# n = 5

if __name__ == '__main__':
    data = json.load(open('data/nasa.json'))
    dataset = data['dataset']

    print len(dataset), 'datasets'

    # tokenize description fields
    print 'Tokenizing descriptions'
    desc = []
    doc_id = []
    for i, ds in enumerate(dataset):
        text = TextBlob(ds['description'])
        for sentence in text.sentences:
            desc.append(sentence.tokens)
            doc_id.append(i)

        # text = TextBlob(ds['title'])
        # for sentence in text.sentences:
        #     desc.append(sentence.tokens)
        #     doc_id.append(i)

    print 'Constructing ngrams'

    print 'Bigrams'
    desc_bigrams = Phrases(desc, threshold=thresh)
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

    field = 'gensim_ngram_kw_%s' % thresh
    for i, ngram in enumerate(fivegrams):
        doc = doc_id[i]

        if field not in dataset[doc]:
            dataset[doc][field] = set()

        for kw in filter(lambda k: '_' in k, ngram):
            keyword = kw.replace('_', ' ').lower()

            # filter out punctuation, etc (make sure that there are two non-punc words)
            if len(TextBlob(keyword).words) < 2:
                continue

            dataset[doc][field].add(keyword)

    # convert set into list for json serialization
    for d in dataset:
        d[field] = list(d[field])

    # update the original data json and save
    data['dataset'] = dataset
    with open('data/nasa_ngram_%s.json' % thresh, 'w') as f:
        json.dump(data, f)