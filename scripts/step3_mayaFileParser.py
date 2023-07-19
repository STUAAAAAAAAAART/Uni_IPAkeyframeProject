# run this file directly in maya's script editor
# have the JSON folder occupy the same location as the maya file

import json
import pymel.core as pm
import maya.cmds as mc

from os import path

def lerp(a, b, t):
	# https://gist.github.com/laundmo/b224b1f4c8ef6ca5fe47e132c8deab56
	"""Linear interpolate on the scale given by a to b, using t as the point on that scale.
	Examples
	--------
		50 == lerp(0, 100, 0.5)
		4.2 == lerp(1, 5, 0.8)
	"""
	return (1.0 - t) * a + t * b


# ====== Get and Load keyframe value dictionary
thisFile_Ma = mc.file(q=True, sn=True)
thisPath = path.dirname(path.realpath(thisFile_Ma))
#print(thisPath)
valIPAPath = path.join(thisPath, "JSON\\valIPA.json")
#print(valIPAPath)
with open(valIPAPath) as loadKeyframes:
    keyJSON = json.load(loadKeyframes)
    print("keyJSON initialised \n")

# >>>>>> invoke file dialog to get speech recognition results
inFile = pm.fileDialog2(dialogStyle=1, fileFilter="*.json", fileMode=1)

# pm.fileDialog2 passes over [List] despite one-item selection
print(inFile)
print(path.basename(inFile[0]))

with open(inFile[0]) as loadFile:
    inJSON = json.load(loadFile)
    print("inJSON initialised \n")

# generate lookup lists
allConsonant = list(keyJSON["consonant"].keys())[2:]
allVowel = list(keyJSON["vowel"].keys())[1:]
consonantKeyDict = keyJSON["map"]["consonant"]["place"]
consonantDictCount = 1.0 / len(consonantKeyDict)
oneThird = 1.0/3.0

# ====== create dataholder network

ingestProc = mc.group(em=True, n='g_testIngest0')
print(ingestProc)
mc.select(ingestProc)
mc.addAttr(dt="string", k=True, sn='filename')
mc.setAttr(ingestProc+".filename", path.basename(inFile[0]) ,type="string")
mc.addAttr(dt="string", k=True, sn='wordStream')

mc.addAttr(at="long", k=True, sn='wordIndex', dv = 0)
mc.addAttr(at="long", k=True, sn='wordEnd', dv = 0)
mc.addAttr(dt="string", k=True, sn='symbolStream')
mc.addAttr(at="long", k=True, sn='symbolIndex', dv = 0)

quickAttrfloat = [
	["outConsonantHeight",0.25],
	["outConsonantPlace", 0.0],
	["outVowelHeight", 0.25],
	["outVowelBackness",0.0],
	["outVowelRoundness",0.5],
	["switchConsonantVowel",0.0],
	["midpt1Bilabial",0.1],
	["midpt2Labiodental",0.2],
	["midpt3Fricatives",0.35],
	["midpt4Velar",0.5]
	]
for aa in quickAttrfloat:
	mc.addAttr(at="float", k=True, sn=aa[0], dv=aa[1] )

# ====== fill word stream
holdPhrase = ""
for aa in inJSON["phrase"]:
	holdPhrase += aa["text"] + " "
mc.setAttr(ingestProc+".wordStream", holdPhrase ,type="string")

# prepare IPA keystomping function
def keystomp():
	mc.setKeyframe(ingestProc, attribute='outConsonantHeight',itt="linear",ott="linear")
	mc.setKeyframe(ingestProc, attribute='outConsonantPlace',itt="linear",ott="linear")
	mc.setKeyframe(ingestProc, attribute='outVowelHeight',itt="linear",ott="linear")
	mc.setKeyframe(ingestProc, attribute='outVowelBackness',itt="linear",ott="linear")
	mc.setKeyframe(ingestProc, attribute='outVowelRoundness',itt="linear",ott="linear")
	mc.setKeyframe(ingestProc, attribute='switchConsonantVowel',itt="linear",ott="linear")



# ====== fill IPA symbol stream
holdPhrase = "/"
wordCounter = 0
for aa in inJSON["phrase"]:
	for bb in aa["result"]:
		# hold IPA stream
		holdPhrase += bb["IPA"][1:]
		startWd = str(bb['start'])+'sec'
		endWd = str(bb['end'])+'sec'
		# >>> turtle over and set keys, because booleans don't key so good with mc.setKeyframe
		mc.currentTime(startWd)
		mc.setAttr(ingestProc+".wordIndex", wordCounter)
		mc.setKeyframe(ingestProc, attribute='wordIndex',itt="stepnext",ott="step")

		# ====== enumerate symbols
		symbLen = float(len(bb["IPA"])) -2.0
		symbTick = -1.0
		for cc in bb["IPA"][1:-1]:
			symbTick += 1.0
			foundSymbol = False
			# lerp to glyph position
			goTime = str(lerp(bb['start'], bb['end'], symbTick/symbLen))+'sec'
			mc.currentTime(goTime)
			
			# look up current symbol
			for gly in allVowel:
				if gly.find(cc) >-1:
					# this is a vowel, set 4 items, key all
					try: vowArray = keyJSON["vowel"][cc]
					except: break
					foundSymbol = True
					mc.setAttr(ingestProc+".outVowelHeight", vowArray[0] * oneThird)
					mc.setAttr(ingestProc+".outVowelBackness", vowArray[1])
					mc.setAttr(ingestProc+".outVowelRoundness", vowArray[2])
					mc.setAttr(ingestProc+".switchConsonantVowel", 1.0)
					keystomp()
			if foundSymbol: continue
			for gly in allConsonant:
				if gly.find(cc) >-1:
					# this is a consonant, set 3 items, key all
					try: conArray = keyJSON["consonant"][cc]
					except: break
					foundSymbol = True
					conValue = [0.45, consonantKeyDict.index(conArray[0]) * consonantDictCount]
					# consonant mouth height modifier
					if conArray[0] == "bilabial":
						conValue[0] = 0.0
					elif conArray[0] == "labiodental":
						conValue[0] = 0.1
					elif conArray[1] == "fricative":
						conValue[0] = 0.2
					elif conArray[0] > 3:
						conValue[0] == 0.35
					mc.setAttr(ingestProc+".outConsonantHeight", conValue[0])
					mc.setAttr(ingestProc+".outConsonantPlace", conValue[1])
					mc.setAttr(ingestProc+".switchConsonantVowel", 0.0)
					keystomp()
					break
			



		# <<< close out word keyframe marker
		mc.currentTime(endWd)
		mc.setAttr(ingestProc+".wordEnd", wordCounter)
		mc.setKeyframe(ingestProc, attribute='wordEnd',itt="stepnext",ott="step")
		wordCounter += 1

	# park turtle
mc.currentTime('0.0sec')
mc.setAttr(ingestProc+".symbolStream", holdPhrase ,type="string")



del inJSON
print("inJSON deleted\n")