# Samrómur

Version 0.9.
Published 01/06/2020

Samrómur is a crowd-sourced speech corpus in Icelandic. This is the first version of the corpus. The version contains 100.000 validated utterances from adult speakers. The age and gender distribution are as follows:

[Bæta inn tölum hér]

# The directory
samromur
	/audio
		
	/metadata.tsv
	/transcripts.tsv

The directory /audio contains all the audio files. They are WAV formatted with a sample rate of 16khz and a bit depth of 16. 

Each line in the metadata.tsv has a corresponding audio file. There are 9 columns, they are:

speaker_id -    An integer value for the speaker that donated this voice sample. The amount of clips speakers donate varies from just a few clips to hundreds or thousands. The speaker_id is not a perfect indicator as some speakers might be counted together under the same integer and the same speaker might have a few speaker ids. This because the 
speaker_id is derived from the client_id of the device used to record and other demographic information provided.
sex -   The gender of the speaker. It can be male, female or other. 
age -   The age of the speaker.
native_language -   The native language of the speaker.
duration    -   Duration of the audio clip.
orginal_sample_rate -   The sample rate used while recording the audio clip.
sample_rate -   The sample rate of the audio clip in the corpus
audio_file -    The name of the audio file.
sentence -  The transcript of the recording.

## About the corpus
The Samrómur speech corpus is a crowded-sourced corpus. Volunteers donated there voice by using the website [Samrómur](www.samromur.is). The collection effort started in autumn 2019 and is on-going as of this publication. 

The work is funded by the ministry of education, managed by  Almannarómur - Miðstöð máltækni, an NGO, and executed by the Language and Voice lab in Reykjavik University 



## License
This work is licensed under a [Creative Commons Attribution 4.0 International
License][cc-by].

[cc-by]: http://creativecommons.org/licenses/by/4.0/
