# Base code source:
	# https://singerlinks.com/2021/07/how-to-convert-speech-to-text-using-python-and-vosk/


# !! start singerlinks.com code
from vosk import Model, KaldiRecognizer
import wave
import json

import os
scriptPath = os.path.dirname(os.path.realpath(__file__))

'''
this script reads a mono wav file (inFileName) and writes out a json file (outfileResults) with the speech to text conversion results.  It then writes out another json file (outfileText) that only has the "text" values.
'''
# Replace filename with intended file or file dialog

#inFileName = os.path.join(scriptPath,'answerinprogressSmallTalk.wav')
inFileName = os.path.join(scriptPath,'tomScottMachineTranslation.wav')
#inFileName = os.path.join(scriptPath,'gradyNordStream2PracticalEngineering.wav')
#inFileName = os.path.join(scriptPath,'pixarToyStory1YouAreAToy.wav')

# outputs are saved to the same directory. Coordinate adjustments to this code with script for step 2
outfileResults = os.path.join(scriptPath,'M1S3-Results.json')
outfileText = os.path.join(scriptPath,'M1S3-Text.json')


# >> functional code begins here

wf = wave.open(inFileName, "rb")

phraseCounter = 0

# initialize a string to hold results
results = ''
textResults = []

# build the model and recognizer objects.
#model = Model(os.path.join(scriptPath,'models/vosk-model-en-us-daanzu-20200328'))
model = Model(os.path.join(scriptPath,"models/vosk-model-en-us-0.22"))
print(model)

recognizer = KaldiRecognizer(model, wf.getframerate())
recognizer.SetWords(True)

# !! end singerlinks code

# code refactored to weld multiple result JSONs to a single JSON dict
	# each result is standalone JSON, possibly intended to generate multiple files
	# code changed to have a superkey hold multiple JSON dicts
	# a simple dictionary merge could suffice, but opted to retain the text key just in case  
while True:    
	data = wf.readframes(4000)
	if len(data) == 0:
		break
	if recognizer.AcceptWaveform(data):
		print(f">>>> {phraseCounter}")
		if phraseCounter>0:
			results += ','
		recognizerResult = recognizer.Result()
		results = results + recognizerResult
		# convert the recognizerResult string into a dictionary  
		resultDict = json.loads(recognizerResult)
		# save the 'text' value from the dictionary into a list
		textResults.append(resultDict.get("text", ""))
		phraseCounter += 1
		print(f"<<<< {phraseCounter}")
		

##    else:
##        print(recognizer.PartialResult())


# process "final" result
	# recognizer.FinalResult() apparently flushes the last result after handing over return
lastOne = recognizer.FinalResult()
if phraseCounter > 0:
	results += ","
results = '{\n "phrase" : [\n' + results + lastOne + "\n]\n}"
resultDict = json.loads(lastOne)
textResults.append(resultDict.get("text", ""))
#print(lastOne)


# !! start singlerlinks.com code
# write results to a file
with open(outfileResults, 'w') as output:
	print(results, file=output)

# write text portion of results to a file
with open(outfileText, 'w') as output:
	print(json.dumps(textResults, indent=4), file=output)

# !! end singerlinks.com code