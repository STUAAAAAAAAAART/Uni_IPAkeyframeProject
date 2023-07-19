# Uni_IPAkeyframeProject
Part of the Research and Development unit at Bournemouth University, 2022/23


### License notice
Published under GNU GPL 3.0, although it'd be best to refer to sources in code comments and attribute to them instead.
(!) Test audio are from copyrighted sources (youtubers mainly) and attribution is specified in the audio examples folder.

## Opening note
` ResultsPlusIPA.json `
This is the file to be parsed by the keyframing script in maya.

The pronunciation for "winograd" had to be manually sourced from wikipedia, as it does not exist in the open-dict databases

## Summary of how it works
- Audio is transcribed and per-word timecoded via a speech-to-text converter (Vosk)
- text is parsed with an IPA dictionary into a timecoded IPA JSON file ( https://github.com/open-dict-data/ipa-dict )
- JSON file is read in Maya and null group is made with keyframes for Consonant and Vowel location values (internal dictionary of 3D/2D floats)
- Group with keyframed attributes are to be connected to Consonant and Vowel control surfaces of the character rig (rig not included)

## Directions of use



## Quality notice
2023.07.18
- code is provided as-is, in more of a prototype state
	- some phonetic motions missed/mistargeted/mismatch, i.e. weird movements not indicative to actual word spoken
	- will need fine tuning of the phoneneme-to-float dictionary
	- most functionality still needs attendace with code edtior open, which isn't ideal to hand off directly to pipeline in current state
	- Maya struggles somewhat with keyframe generation on long JSON files, consider generating keyframes to a .ma or .FBX ASCII file externally, then import to maya
	- 
- future functionality
	- MAYA - word spread scaling (and UI) for retiming syllables or inserting pauses 
	- MAYA - 
	- phoneme editing, either in maya or externally
	- user-sided addition of more word IPA definitions