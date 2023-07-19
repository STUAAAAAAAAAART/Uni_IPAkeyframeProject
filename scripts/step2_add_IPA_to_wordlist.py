import json
import os

from sys import getsizeof

# print(os.path.dirname(os.path.realpath(__file__)))
# print( os.path.join(os.path.dirname(os.path.realpath(__file__)), "..\\DB\\en_UK.json") )
# AUDIO_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "english.wav")
thisPath = os.path.realpath(__file__)
print(thisPath)
# print(thisPath)
# print(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
# print(os.path.dirname(thisPath))

# get input word list JSON 
	# THIS IS THE EXISTING IPA JSON DATA THE SCRIPT WILL USE.
	# REPLACE WITH FILENAME OR FILE DIALOG 
inFile = os.path.join(os.path.dirname(thisPath), "M1S3-Results1_tom.json")
print(inFile)

# get IPA Dictionary
db_ipaDict = os.path.join(os.path.dirname(thisPath), "..\\..\\DB\\en_UK.json")
print(db_ipaDict)

# set output file
	# THIS IS WHAT THE COMPLETE JSON OUTPUT WILL BE NAMED.
	# REPLACE WITH FILENAME OR FILE DIALOG 
outfileResults = os.path.join(os.path.dirname(thisPath),'ResultsPlusIPA.json')
print(outfileResults)

with open(db_ipaDict, encoding="utf8") as loadIPA:
	inIPA = json.load(loadIPA)
	inIPA = inIPA[list(inIPA.keys())[0]] # bypass the single only superkey
	print("IPA library initialised")
	print(f"{getsizeof(loadIPA) / 1000} KB")

print(f'{ len( inIPA[0] )}')

# encoding="utf8" required, explicit for python3 unicode decoder
	# https://stackoverflow.com/questions/9233027/
with open(inFile, encoding="utf8") as loadFile:
	inJSON = json.load(loadFile)
	print("inJSON initialised")
	print(f"{getsizeof(loadFile) / 1000} KB")
# print dict keys
	# https://stackoverflow.com/questions/15789059/
	# https://www.w3schools.com/python/ref_dictionary_keys.asp
print(inJSON.keys())
print(f'{ len( inJSON["phrase"] )}')
print(inJSON["phrase"][0].keys())
print(f'{ len( inJSON["phrase"][0]["result"] )}')
print(inJSON["phrase"][0]["result"][0].keys())

# parse IPA
for phrase in inJSON["phrase"]:
	for wd in phrase["result"]:
		try:
			wd.update({"IPA": inIPA[0][wd["word"]] })
		except:
			wdWord = wd["word"]
			if wdWord == "the":
				# override case for "the", depending on region and tonality
				# https://en.wiktionary.org/wiki/the#Pronunciation
	#			wd.update({"IPA": "/ˈðiː/"}) # UK Recieved / US topic-stressed 
				wd.update({"IPA": "/ðə/"}) # common / US unstressed
			elif wdWord == "are":
				# https://en.wiktionary.org/wiki/are#Pronunciation
				wd.update({"IPA": "/ɑɹ/"})
			
			elif wdWord == "a":
				# override case for "a", depending on region and context (singular or letter)
				# https://en.wikipedia.org/wiki/Pronunciation_of_English_%E2%9F%A8a%E2%9F%A9
				# default to letter, this requires adjustments on the speech recognition model
				wd.update({"IPA": "/ðə/"})
			elif wdWord == "it's":
				# override case for it's, mapping to "its"
				wd.update({"IPA": inIPA[0]["its"] })
			elif wdWord == "i'm" : # "i"m"
					wd.update({"IPA": "/aɪm/"})
			elif wdWord == "processing":
				# dictionary missing definition?
				wd.update({"IPA": "/ˈpɹəʊsɛsɪŋ/"})
			elif wdWord.count("'") == 1 : # contains 're 's 've n't 'm 'll
				# override case for contractions
				# skipping compound contractions (especially "I would not have"/"I’d’nt’ve")
				ct = wdWord.split("'")[1]
				if ct == "ve":
					wdBase = inIPA[0][wd["word"]].split("/")[1] # strip IPA of /slashes/ and take the ['','pronounciation',''] bit at index [1]
					wdCon = "əv"
					wd.update({"IPA": f"/{wdBase}{wdCon}/"})
				elif ct == "re":
					wdBase = inIPA[0][wd["word"]].split("/")[1] # strip IPA of /slashes/ and take the ['','pronounciation',''] bit at index [1]
					wdCon = "əv"
					wd.update({"IPA": f"/{wdBase}{wdCon}/"})
				elif ct == "s":
					wdBase = inIPA[0][wd["word"]].split("/")[1] # strip IPA of /slashes/ and take the ['','pronounciation',''] bit at index [1]
					# https://en.wiktionary.org/wiki/%27s
					wdCon = "s" # defaulting to one definition, will require checking last glyph of base word's IPA (doable)
					wd.update({"IPA": f"/{wdBase}{wdCon}/"})
				elif ct == "t": # implies "-n't", complex contraction
					# https://dictionary.cambridge.org/grammar/british-grammar/contractions
					# https://en.wiktionary.org/wiki/ [word]#Pronunciation
					# pronounciation of main word changes at the end towards -n't
					# proper way would be to adjust IPA dictionay JSON file directly, but nuances may challenge attempts at change
					ctDict = {
						"aren’t" : "/ˈɑɹənt/", # regional, US used here
						"can't" : "/kɑːnt/", # regional, GB used here. #sorry
						"couldn’t" : "/ˈkʊd.(ə)nt/",
						"didn’t" : "/ˈdɪd(ə)nt/", # varies, skipping "diin"
						"hasn’t" : "/ˈhæzn̩t/",
						"haven’t" : "/ˈhævn̩t/",
						"isn’t" : "/ˈɪzənt/", # regional, GB used here, skipping "i'nn"
						"musn’t" : "/ˈmʌsnt/",
						"mustn’t" : "/ˈmʌs.n̩t/",
						"shan’t" : "/ˈʃɑːnt/",
						"shouldn’t" : "/ˈʃʊdn̩t/",
						"wasn’t" : "/ˈwɒzənt/",
						"weren’t" : "/ˈwɜːnt/",
						"won’t" : "/wəʊnt/",
						"wouldn’t" : "/ˈwʊdn̩t/"
					}
					try: wd.update({"IPA": ctDict[wdWord]})
					except:
						print(f"WORD NOT FOUND! << { wd['word'] }")
						wd.update({"IPA": "/▮/"})	
				else:
					print(f"WORD NOT FOUND! << { wd['word'] }")
					wd.update({"IPA": "/▮/"})
			
			else:
				print(f"WORD NOT FOUND! << { wd['word'] }")
				wd.update({"IPA": "/▮/"})


#print(inJSON["phrase"][0]["result"][0])
#inJSON["phrase"][0]["result"][0].update({"IPA": "TESTING"})


# save JSON to file
	# https://stackoverflow.com/questions/27092833/unicodeencodeerror-charmap-codec-cant-encode-characters
	# https://stackoverflow.com/questions/18337407/saving-utf-8-texts-with-json-dumps-as-utf-8-not-as-a-u-escape-sequence
with open(outfileResults, 'w', encoding="utf-8") as output:
	json.dump(inJSON, output, ensure_ascii=False, indent="\t")



del inJSON
print("inJSON deleted\n")
del inIPA
print("inIPA deleted\n")

