# Samrómur automated verification wrapup
The Samrómur corpus has appr. 1.1 million speech recordings with each recording being on average 5 seconds long. That gives us around 1528 hours, or 63 days, worth of audio data.  Most of them contain children voices with girls being in the majority. These numbers include noisy data as well, which is to be expected in corpus created by public volunteering effort.

As the corpus began to grow at a rapid pace we started to ask ourselves: how much of this data is actually usable for ASR training? Since February we have been on a mission to find out exactly that by verifying the recordings. But verifying over a million recordings is no easy task and is too much effort to expect of human verifiers. Even though the [Samrómur website](https://www.samromur.is) offers anyone to listen to the recordings and verify them, we cannot rely on that to solve this task as humans only have a certain amount of patience for repetitive tasks, especially if they are volunteering.

That leads us to the only sensible solution, automated verification. A large part of the Samrómur corpus has, as of August, been verified automatically.
This document explains the methods and tools which were used to perform the automated verification, what we learned while researching the subject as well as the result of that research.

*If you would like to skip straight to about how to use this package to process Marosijo votes, please go to the chapter called **The tools***.

Do note that all mentions of dates and months here refer to those of the year of 2021 unless otherwise specified.
 

## Table of Contents
- [Samrómur automated verification wrapup](#samrómur-automated-verification-wrapup)
  - [Table of Contents](#table-of-contents)
  - [Methods](#methods)
    - [Deciding dataset to verify](#deciding-dataset-to-verify)
    - [Shortcomings](#shortcomings)
    - [Attempts at improvement](#attempts-at-improvement)
    - [Result](#result)
      - [Processing of the Marosijo output](#processing-of-the-marosijo-output)
        - [Rules and score groups](#rules-and-score-groups)
        - [MFA's involvement](#mfas-involvement)
        - [Unverified recordings](#unverified-recordings)
        - [Exclusion of already verified recordings](#exclusion-of-already-verified-recordings)
        - [Vote statistics](#vote-statistics)
      - [Applying the votes to the Samrómur database](#applying-the-votes-to-the-samrómur-database)
        - [Results](#results)
        - [The machine_verified column](#the-machine_verified-column)
        - [The marosijo_score column](#the-marosijo_score-column)
      - [Updating the local metadata](#updating-the-local-metadata)
  - [Limitation of automated verification](#limitation-of-automated-verification)
  - [The tools](#the-tools)
    - [generate_marosijo_votes.py](#generate_marosijo_votespy)
    - [add_summary.py](#add_summarypy)
  - [How to apply the votes](#how-to-apply-the-votes)
- [Important note](#important-note)
- [Authors and credit](#authors-and-credit)

## Methods
When we started looking into automated verification we already had a tool designed for exactly that. It is called Marosijo and is developed by the people at LvL. It relies on having a pretrained acoustic model and uses Kaldi to perform the verification. It is part of the QualityCheck module of samromur-tools. samromur-tools also has a utility to train a model which Marosijo can use.

Marosijo uses Kaldi and the pretrained acoustic model to transcribe each audio file, then the transcription is compared to the supplied model transcription in order to calculate the word error rate (WER). The word error rate value is the confidence score which each recording is given and is used to determine how the votes should be. The confidence score is also often simply referred to as Marosijo score. The scores are on the range from 0.0 to 1.0 with 0.0 being the worst possible score - recordings contain no speech or just noise but are not necessarily empty - and 1.0 being the best possible score - recordings are usually flawless, with clear speech and correct pronunciation of words.

The first thing we did was to download all of the recordings present on Samrómur and run a Marosijo verification on all of them.

### Deciding dataset to verify
After downloading all of the recordings (along with their metadata) on February 5th, we started the automated verification using Marosijo. Out of 1.116.357 recordings, there were 791.104 which required verification. Those were recordings that had the following metadata values:

- marosijo_score == "NAN"
- empty == "0"

That is, they lacked Marosijo scores and were not empty.

They were verified in seven batches ranging in size from 41.663 to 214.194:

1. 190221_qc_big                  (214.194 verified recordings)
2. 240221_qc_first_200k           (65.619 verified recordings)
3. 260221_qc_150k_218042-895299   (149.999 verified recordings)
4. 010321_qc_150k_218042-1099684  (119.635 verified recordings)
5. 040321_qc_100k_218042-1192490  (99.994 verified recordings)
6. 080321_qc_100k_218042-1336566  (99.995 verified recordings)
7. 100321_qc_42k_218042-1397007   (41.663 verified recordings)

Note: The added up sum of those batches is 791.099 recordings, not 791.104. That is because Marosijo was unable to verify five recordings. Therefore, this Marosijo verification yielded us 791.099 Marosijo scores for an equal amount of recordings.

It took 19 days from start to finish. The start of a batch name denotes the date which its verification started. After "qc" comes the size of the batch, the reason these numbers don't match the actual number of verified recordings is because sometimes the verification process would fail due to time constraints set by SLURM on Terra and, in some cases, Marosijo failed to verify a few recordings because of reasons unknown. It may have been because they contained no speech but were still not classified as empty. The numerical range (e.g. 218042-895299) was supposed to denote the recording ids verified but that naming convention did not go as planned, so kindly dismiss this part of the batch name.

### Shortcomings
At this point, Marosijo had finished verifying all of the batches and we were stockpiled with scores upon scores of hundreds of thousands of recordings. One might intuitively think that, at this point, all what is left to do is to decide which score ranges get positive votes and which ones get negative votes and, based on that, gather the votes, apply them to the database and voila - everything is done. But no, not so fast. 

The next step was to verify that Marosijo's score could be trusted. The only way to do that was to have someone listen to and verify a few predetermined sets of recordings and evaluate if the recordings' quality was in line with the Marosijo scores. The sets were as diverse as possible, consisting of recordings of various combinations of score ranges, genders, age and native language. The total number of recordings was 1.250. 

During this evaluation of Marosijo, it was found out that the scores were not flawless. 
It turned out that recordings with high scores - from 0.9 to 1.0 - were in some cases not good enough. Around 20% of these high scoring recordings, which were manually verified, contained small pronunciation mistakes or had the start or end of the audio missing. Those kind of recordings were identified as false positives, as they falsely got positive scores they did not deserve.
Furthermore, the recordings with lower scores - from 0.01 to 0.89 - also proved to have similar problems. A considerable percentage of them was identified as false negatives as, as they falsely got negative scores which they did not deserve - they were good even though their scores were in the lower range. Some of them had a little background noise or poor (but clear enough) audio quality but that does not necessarily make a recording bad.
Later on we tried to look differently at the numbers by narrowing the otherwise wide score range of 0.01 to 0.89 down to 0.01 to 0.3. The percentage of false negatives was much lower here but it was still present. 
The remaining recordings on the score range of 0.301 to 0.89 were determined to be undecidable by Marosijo as these scores are simply too close around the center of the entire range. 
Then there are the zero-scoring recordings. Luckily, we observed that recordings with the score of absolute zero, 0.0, were in all cases bad. No false negatives there. 

We were not happy enough with these results though, even though we found out that scores in the range of 0.01 to 0.3 had lower percentage of false negatives than previously thought. It mainly had to do with the higher scoring recordings on the range of 0.9 to 1.0. We did not find the amount of false positives there acceptable and, therefore, we started looking into ways to improve that number in any ways possible.

### Attempts at improvement
The first thing we tried in order to improve the false positive and false negative rates was to tweak the acoustic model which Marosijo uses for the verification process. We made two attempts to tweak those models and tested them for verification on the already defined set of 1.250 recordings we used to evaluate Marosijo's quality. That set was chosen because for each of those recordings it was documented if it was good or bad and if it was bad, the type of flaw was documented as well.

The original verification model was trained using 50.000 Samrómur recordings which were supposedly all good and usable for acoustic model training.

In the first attempt at improvement we used a more carefully selected set of recordings to train the verification model. For the original model, we simply selected the first 50.000 recordings present in the Samrómur database. The thought was that they **should** be all verified and good for training but, just to be sure, we wanted to filter the training data more carefully. We, therefore, selected the first 50.000 recordings in the Samrómur database which were marked as valid and nonempty.
The results of this attempt were disappointing and the difference in the false negatives and false positives rates were ignorable. There was no improvement over the original verification model.

In the second attempt at improvement we returned to the original verification model as the one from the first attempt at improvement did not change anything. We retrained that model with exactly the same data, only this time we tried using a different pronunciation dictionary. As before, we tried out the resulting model on the manually tested 1.250 recordings and documented the results. As in the first attempt, there was almost no difference in the rates of false positives and false negatives. This second attempt did, therefore, not improve anything either.

The next step was to try something completely different. During the manual evaluation of Marosijo, it was observed that at least of the false positive recordings (with score of 0.9 to 1.0 but are actually not good) were considered bad because they had a word or two missing at the start or beginning of the audio. We thought to ourselves, what if we could make all of those recordings still usable somehow? That would reduce the number of false positives to an acceptable amount.

A recording's model transcription says, for instance:
"afi minn fór á honum rauð"

But the audio says:
"fór á honum rauð"

What if we could get the duration of every spoken word in the audio and, that way, detect words with no duration and cut them from the model transcription? Then the invalid audio recording would become valid. After this proposed fix, the example above would look like this:

Model transcription:
"fór á honum rauð"

Audio says:
"fór á honum rauð"

That is where Montreal Forced Aligner, from here on abbreviated to MFA, came in. MFA takes a recording and its model transcription as an input and outputs a file on a Praat format which contains timestamps and duration of every word and phoneme present in the model transcription. MFA's limitations for this project became quickly apparent as we looked over the Praat files. It seems that what defines *forced* alignment is that the aligner *forces* alignment upon every single word and phoneme present in the **model transcription** but not in the *audio itself*. This means that, even though some word is not present in the audio, MFA still gives it some mininum duration value (the duration of a single frame). The recording may even be completely empty and MFA still gives every word and phoneme a minimum duration. We came up with the idea that words with the minimum duration must be inaudible in the audio but upon further thinking we concluded that was a very unreliable measurement as some actually audible words may have the minimum duration as well. The final result was that MFA would not be of the use we thought it would be. For the record though, it performed very well on perfect data where the spoken dialogue was correct and output some very accurate timestamps and duration values for such recordings.

MFA's output turned out to have a small side product which we could make use of though. MFA outputs a list of unalignable recordings. After listening to a handful of such recordings it turned out they were most definitely bad. In the verification approach we ultimately used and we describe in next chapter, this list of unalignable recordings is used to reinforce that recordings in the low score range of 0.01 to 0.3 are truly bad and that enabled us to give such recordings negative super votes. A super vote about a recording's validity is always final and decides if a recording is valid or not, otherwise two votes are needed.

### Result
After a considerable time of researching methods to improve the quality of the verification we came upon the conclusion that the original Marosijo verification was the best we could do. We therefore defined some rules and conditions which the recordings must follow in order to get a negative vote, negative super vote, positive vote or no vote at all. We ran all of verified recordings' metadata through a script which decided, according to the rules and conditions, which recordings get what kind of votes. The output was a list of recording id's along with what kind of vote each recording gets. Afterwards, the data on that list was applied to the live database and many of the Samrómur recordings finally got their verification. The local metadata was updated soon after that.

#### Processing of the Marosijo output
As was mentioned above, a set of rules and conditions were defined and, for each recording, these rules and conditions were checked and based on that, its vote was decided.

##### Rules and score groups
The rules were as follows:
1. Recordings with a score of 0.9 and higher get a **positive vote**.
2. Recordings with a score in the range of 0.01 to 0.3 get a **negative vote**.
3. Recordings with a score in the range of 0.01 to 0.3 and are unalignable by Montreal Forced Aligner get a **negative super vote**.
4. Recordings with a score of 0.0 get a **negative super vote**.
5. Recordings which are empty get a **negative super vote**.*
6. Recordings which are not within the above score ranges, but rather within the complementary score range of 0.301 to 0.899 get **no vote**.
7. Recordings which have not been Marosijo verified and are not empty get **no vote**.

\* Empty recordings were detected and marked as such using a separate tool in the inspection process right after the recordings were downloaded with the GetRecordings module of samromur-tools. That is, Marosijo did not mark them as empty and neither were such recordings a subject to Marosijo verification as they were empty and therefore no need for Marosijo to check them.

Based on these rules, seven named score groups were identified.
1. **high**:            Recordings with high scores in the range of 0.9 to 1.0. (based on rule #1)
2. **low**:             Recordings with low scores in the range of 0.01 to 0.3. (based on rule #2)
3. **low_unalignable**: Recordings with low scores in the range of 0.01 to 0.3 and are *also* unalignable by Montreal Forced aligner. (based on rule #3)
4. **zero**:            Recordings with the lowest possible score of 0.0. (based on rule #4)
5. **empty**:           Recordings which have been marked as empty. (based on rule #5)
6. **between**:         Recordings which do not fall within the other defined scores ranges and are in the range of 0.301 to 0.899. (based on rule #6)
7. **nonverified**:     Recordings which have not been Marosijo verified and are not empty. (based on rule #7)

The reason why recordings in the groups *high* and *low* are not given super votes is because of the chances that there may be false positives or false negatives, as was discussed in the *Shortcomings* chapter. That is, we don't fully trust Marosijo to give definite votes for those reasons. More reassurance is needed, for instance if a recording is marked as empty or has a score of absolute zero, then it is okay to give a definite super vote.  

##### MFA's involvement
As was mentioned in the *Attempts at improvement* chapter, Montreal Forced Aligner produced a small byproduct which was of use to us. Its list of unalignable recordings proved to be always bad and we could use that list to take a subset from the score group *low* and create the score group *low_unalignable* and give its recordings negative super votes.

##### Unverified recordings
We did not feed Marosijo the recordings which had been marked empty by initial automated inspection of them. Because of that, such recordings lack Marosijo scores and are in the group *empty*. It is, however, known that somehow 64 empty recordings got Marosijo verified somehow. These scores, which should be very low, were not inspected and the empty tag decided these recordings' fates. The recordings in the group *nonverified* are recordings which have **not** been marked as empty but still lack Marosijo scores. These were only five recordings which Marosijo attempted to verify but failed for some reason.

##### Exclusion of already verified recordings
In the summer we had 12 summer students verifying Samrómur recordings. Each one had super vote privileges, so only one vote was needed to validate a recording. In total, they managed to verify 192.819 recordings from June 3rd to August 17th (hooray to them!). We, however, had already had Marosijo running through all of those recordings and the score summaries already contained scores for them. This simply meant that while processing the Marosijo score data, in order to generate the votes, we skipped recordings which had already been verified (had is_valid as non-null in the database).

##### Vote statistics
This table shows how the votes were divided between the different groups based on the rules:

| score_group     | vote_type      | marosijo_vote_amount | man_verification_amount | total         |
|-----------------|----------------|----------------------|-------------------------|---------------|
| high            | positive       | 435.550              | 266.354                 | 701.904       |
| between         | none           | 247.697              | 65.457                  | 313.154       |
| low             | negative       | 15.386               | 3.721                   | 19.107        |
| low_unalignable | negative_super | 1.132                | 247                     | 1.379         |
| zero            | negative_super | 13.122               | 20.191                  | 33.313        |
| empty           | negative_super | 46.109               | 1.386                   | 47.495        |
| nonverified     | none           | 4                    | 1                       | 5             |
|                 |                | **759.000**          | **357.357**             | **1.116.357** |
							
| Positive votes | Negative votes | Negative super votes | Total votes |
|----------------|----------------|----------------------|-------------|
| 435.550        | 15.386         | 60.363               | **511.299** |
|                |                |                      |             |
| No votes       |                |                      |             |
| 247.701        |                |                      |             |	

- The *total* column is the sum of the *marosijo_vote_amount* and *man_verification_amount* columns. That is, the total number of recordings which belong to each score group. They are then divided into the two sets:
  - *marosijo_vote_amount*: Recordings of a group which have **not** been manually verified and the number denotes how many votes will be given, one for each recording.
  - *man_verification_amount*: Recordings of a group which **have** been manually verified and don't require any votes.

- Note that the score groups *between* and *nonverified* do not determine any votes. The numbers in their *marosijo_vote_amount* column denote really how many recordings in their range have not been manually verified.

#### Applying the votes to the Samrómur database
By the beginning of September the votes were applied to the live database. Before that was done, a replica of it was created and a thorough test was run on it in order to make sure that the applying of the votes was a success. Everything looked well and the votes were applied to the live production database of Samrómur.

##### Results
After the votes had been applied:
- **4.070** recordings got complete validation as valid as a result of applying ordinary positive votes.
- **109** recordings got complete validation as invalid as a result of applying ordinary negative votes.
- **60.352** recordings got complete validation as invalid as a result of applying negative super votes. 
  - Note: This number is 11 votes lower than the amount of super votes applied because 11 of the recordings had already been manually verified since the machine votes were created. 

The first two numbers are much lower than was expected. For ordinary votes, two are required for a recording to get a complete validation (its *is_valid* value becomes non-null). This means that, for the positive ordinary votes, only 4.070 recordings in the database already had one positive vote and required a second one to complete the validation. On the bright side, however, this has reduced the work of manual verification by 50% by giving well over 430.000 recordings single positive votes so that only one human vote is required. Same goes for the negative ordinary votes.

##### The machine_verified column
For the convenience of whoever might use the Samrómur corpus for ASR training, a boolean column called *machine_verified* was added to the database. If a validated recording has a vote, super or not, based on a Marosijo score, its machine_verified value equals true, false otherwise. This is done because, as one would expect, machine votes are not as reliable as human votes as can be seen by the amount of false positives and negatives encountered while evaluation the quality of Marosijo. This way, people can at least know that, positively voted recordings for instance, are *most likely* fine if the machine verification says so.

##### The marosijo_score column
For a long time, this column has been present in the local metadata but it was decided to include it in the database as well. That way, anyone who downloads the data is able to see how confident Marosijo was about certain recordings.

#### Updating the local metadata
The local metadata on Terra was updated soon after the votes had been applied to the production database.

## Limitation of automated verification
As has been said before, one can never trust a machine verification as well as a human one. One of the reasons for that are the false positives and negatives which have been mentioned before. Where high scoring recordings are not good enough (false positives) and where low scoring recordings are actually good (false negatives). For this reason, it was decided to calculate confidence scores for the defined score groups. These scores tell, whoever that decides to use machine verified recordings for ASR training, how well they can trust them to be good.

To calculate a confidence score for a group, the high scoring group which got a score of 0.9 - 1.0 for instance, we look at the subset of it which has been manually verified and calculate the percentage of it which has been verified as valid. The confidence score roughly denotes, in percentage, how likely the given machine vote is to be trusted.

Here below are the confidence scores and their calculations for the largest groups of recordings which got Marosijo votes:

| Score group | Score range | Vote type        | Amount  | Machine verified | Manually verified | Manually verified as valid | Manually verified as invalid | Confidence score     |
|-------------|-------------|------------------|---------|------------------|-------------------|----------------------------|------------------------------|----------------------|
| high        | 0.9 - 1.0   | Positive         | 701.904 | 435.550 (62.1%)  | 266.354 (37.9%)   | **227.186 (85.3%)**        | 39.168 (14.7%)               | **85.3%**            |
| low         | 0.01 - 0.3  | Negative         | 20.486  | 16.518 (80.6%)   | 3.968 (19.4%)     | 380 (9.6%)                 | **3.588 (90.4%)**            | **90.4%**            |
| zero        | 0           | Negative (super) | 33.313  | 13.122 (39.4%)   | 20.191 (60.6%)    | 137 (0.7%)                 | **20.054 (99.3%)**           | **99.3%**            |

Bear in mind that the recordings that have been marked empty and given negative super votes, they are not Marosijo verified but inspected using another tool in the inspect_audio function of the GetRecordings module of the samromur-tools repo. Therefore, they do not have any scores but they have been proven to be truly empty and such recordings can safely be ignored while gathering recordings for training.

The biggest limitation of a machine verification like this is that there have to be recordings on some score range which we cannot reliably tell if are good or bad based on the Marosijo scores. These scores are on the range of 0.301 to 0.899 and fall under a score group called *between*. The recordings in this group have been observed to be somewhat equally likely to be good or bad. Therefore, it was decided not to let scores in this range determine any votes. The reason why this is the *biggest* limitation of machine verification is because this range will inevitably be quite large (0.301 to 0.899) and therefore it contains a large amount of recordings, or 247.697 in our case. They all need human verification.

## The tools
This package contains the tools that were used to process the Marosijo output. It outputs a list of votes which are ready to be put into the Samrómur database.

### generate_marosijo_votes.py
This is the main utility for Marosijo score processing and vote generation. You give a path to a metadata file where the marosijo_score column has been filled with values, a path to a list of Montreal Forced Aligner unalignable recordings and some filenames for the output files.

The output consists of two files:
- *output_votes.tsv*: For each recording which has not been validated (is_valid is null), a line is written into this file. Each line has information about the recording's id, whether it get a positive or negative vote, whether it is a super vote or not, which score group it belongs to, what its Marosijo score was and whether it is marked as empty or not. 
  - The most important columns here are **id**, **pos_vote** and **super** as they are the ones which are required for upload to Samrómur in order to apply the votes. In that case, if a recording is supposed to get a positive vote for instance, pos_vote is 1, else it is 0. So the neg_vote column is not necessary. It was included in the output for sanity checks.
  - These values can easily be isolated into new TSV files with *cut* and output piping. To get the three columns mentioned above, one can use this command:
    - `cut -f1,2,4,5 output_votes.tsv | awk -F" " '$4!="between"' | awk -F" " '$4!="nonverified"' | cut -f1,2,3 > machine_votes.tsv`
    - Note that this command excludes the score groups *between* and *nonverified* as no votes are applied for those groups.

### add_summary.py
Marosijo outputs score summaries which are TSV files with two unnamed columns: *id* and *score*. Sometimes it is necessary to feed Marosijo recordings in many batches. This produces many summary files. This script takes a list of paths to such files and combines them into a single big one for convenience.

## How to apply the votes
The Samrómur platform has an admin API that can be used to upload the votes to the database. The API has been designed to work with the output of the above-mentioned *output_votes.tsv* file. To upload the votes, sign in to [Samrómur.is]<www.samromur.is> as an admin and upload the votes using the admin interface (Mínar síður -> Stjórnandi). This does not add the marosijo_score values, they need to added separately. The suggested process for that is to create a temporary table containing the **clip_id** and **marosijo_score**, then to update the **clips** table with the **marosijo_score** matching the clips **id**.

# Important note
The verification and applying of votes was only performed on a large subset of the Samrómur corpus but not the entirety of it. The subset is comprised of all recordings which had been recorded on Samrómur by **February 5th 2021**. That is **1.116.357** recordings but when this is written (August 17th) that number has grown to 1.160.886 or 44.529 more recordings. 

Some time later, when desired, it is possible to download the new recordings which have been added since February, using the samromur-tools package to download and automatically verify and, finally, this module to process the Marosijo results in order to apply the votes to the database. 

# Authors and credit
Reykjavik University

Smári Freyr Guðmundsson <smarig@ru.is>
Staffan J.S. Hedström <staffanh@ru.is>
David Erik Mollberg <de14@ru.is>