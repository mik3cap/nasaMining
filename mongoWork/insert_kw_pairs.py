from pymongo import MongoClient
import json

# insert the databases around bigram, pair, and textrank frequencies
client=MongoClient('proximus.modulusmongo.net:27017')
client.tepO9seb.authenticate('nasahack', 'hacking4nasa')
db=client.tepO9seb

data=json.load(open("/Users/Jon/Code/DataKind/GlobalGiving/nasaMining/data/keyword_pair_freq.json"))
counter=0
for d in data:
	if counter%100==0:
		print counter
	counter+=1
	db.kw_pair_freq.insert(d)
