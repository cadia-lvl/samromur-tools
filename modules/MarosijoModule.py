# Copyright 2016 The Eyra Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File author/s:
#     Róbert Kjaran <robert@kjaran.com>
#     Matthias Petursson <oldschool01123@gmail.com>
#     David Erik Mollberg

import json
import tempfile
import uuid


from sh import Command, ErrorReturnCode_1
from os.path import join
from modules.utils import errLog, log, isWavHeaderOnly
from modules.marosijoCommon import MarosijoCommon
from modules.marosijoAnalyzer import MarosijoAnalyzer

# Kudos to http://stackoverflow.com/users/95810/alex-martelli for
# http://stackoverflow.com/a/3233356 which this is based on


import collections
def update(d, u):
    """Recursively updates nested dicts. Lists are NOT updated, they are extended
    with new list value. MUTATES `d`.

    """
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        elif isinstance(v, list):
            r = d.get(k, []).extend(v)
        else:
            d[k] = u[k]
    return d

class MarosijoError(Exception):
    pass


class MarosijoTask():
    """_SimpleMarosijoTask
    ===============

    QC module/base task which uses custom decoding graphs, based on
    ideas from [1], and a monophone speech recognizer trained on a
    small (a few hrs) dataset of in-domain data. The results for each
    recording/utterance are a binary value, representing whether it is
    deemed valid or not. The findings are stored as a report in the
    redis datastore under the keys 'report/SimpleMarosijoTask'

    [1] Panayotov, V., Chen, G., Povey, D., & Khudanpur, S. (2015). Librispeech: An ASR corpus based on public domain audio books. In ICASSP, IEEE International Conference on Acoustics, Speech and Signal Processing - Proceedings (Vol. 2015-August, pp. 5206–5210). http://doi.org/10.1109/ICASSP.2015.7178964

    """

    abstract = True

    def __init__(self, downsample, modelPath):
        self.downsample = downsample
        self.modelPath = modelPath
        
    @property
    def common(self):
        """Data common to MarosijoModule and MarosijoGenGraphs  """
        if not hasattr(self, '_common'):
            self._common = MarosijoCommon(downsample=self.downsample, modelPath = self.modelPath)
        return self._common

    @property
    def decodedScpRefs(self):
        """
        Returns the reference part of graphs.scp contents in memory as a dict. Indexed
        by the tokenId.

        {'tokenId' -> 'reference in .ark file (corresponding to the data in a .scp file) '}
        so we can take from this the lines we need to form the partial
        .scp to pass into Kaldi scripts

        """
        if not hasattr(self, '_decodedScpRefs'):
            self._decodedScpRefs = dict()
            with open(self.common.graphsScpPath) as f:
                for line in f:
                    line = line.strip()
                    tokenKey = line.split()[0]
                    arkRef = line.split(' ')[1:]
                    self._decodedScpRefs[tokenKey] = ' '.join(arkRef)

        return self._decodedScpRefs

    def processBatch(self, recordings):
        """
        The main processing function of this module. This function
        is called to do processing on a batch of recordings from the session.

        Parameters:

            name        the name to use to write the report to redis datastore
                        at 'report/name/session_id'

        Return:
            False or raise an exception if something is wrong (and
            this should not be called again.)
        """

        computeMfccFeats = Command('{}/src/featbin/compute-mfcc-feats'
                                      .format(self.common.kaldiRoot))
        computeMfccFeats = computeMfccFeats.bake(
            '--sample-frequency={}'.format(self.common.sampleFreq),
            '--use-energy=false',
            '--snip-edges=false')
        gmmLatgenFaster = Command('{}/src/gmmbin/gmm-latgen-faster'
                                     .format(self.common.kaldiRoot))
        latticeBestPath = Command('{}/src/latbin/lattice-best-path'
                                      .format(self.common.kaldiRoot))

        with tempfile.TemporaryDirectory(prefix='qc') as tmpdir:
            tokensGraphsScpPath = join(tmpdir, 'graphs.scp')
            mfccFeatsScpPath = join(tmpdir, 'feats.scp')
            mfccFeatsPath = join(tmpdir, 'feats.ark')
            tokensPath = join(tmpdir, 'tokens')
            with open(tokensPath, 'w') as tokensF, \
                 open(mfccFeatsScpPath, 'w') as mfccFeatsTmp, \
                 open(tokensGraphsScpPath, 'w') as tokensGraphsScp:

                graphsScp = []
                for r in recordings:
                    if self.common.downsample:
                        print('{rec_id} sox {rec_path} -r{sample_freq} -t wav - |'
                              .format(
                                  rec_id=r['recId'],
                                  rec_path=r['recPath'],
                                  sample_freq=self.common.sampleFreq), file=mfccFeatsTmp)
                    else:
                        print('{} {}'.format(r['recId'], r['recPath']),
                              file=mfccFeatsTmp)

                    tokenInts = self.common.symToInt(r['token'])

                    print('{} {}'.format(r['recId'], tokenInts),
                          file=tokensF)
                    try:
                        graphsScp.append('{} {}'.format(r['recId'],
                                                        self.decodedScpRefs[str(r['tokenId'])]))
                    except KeyError as e:
                        log('Error, probably could not find key in MarosijoModule/local/graphs.scp, id: {}, prompt: {}'
                             .format(r['tokenId'], r['token']))
                        raise


                # make sure .scp file is sorted on keys
                graphsScp = sorted(graphsScp, key=lambda x: x.split()[0])
                for line in graphsScp:
                    print(line, file=tokensGraphsScp)

            try:
                # We save the features on disk (the ,p means permissive. Let kaldi ignore errors,
                # and handle missing recordings later)
                computeMfccFeats(
                    'scp,p:{}'.format(mfccFeatsScpPath),
                    'ark:{}'.format(mfccFeatsPath))

                computeCmvnCmd = ('{kaldi_root}/src/featbin/compute-cmvn-stats ' +
                                  'ark,p:{mfcc_feats_path} ' +
                                  'ark:- ').format(mfcc_feats_path=mfccFeatsPath,
                                                   kaldi_root=self.common.kaldiRoot)
                featsCmd = ('{kaldi_root}/src/featbin/apply-cmvn ' +
                            '"ark,p:{compute_cmvn_cmd} |" ' +
                            'ark:{mfcc_feats_path} ' +
                            '"ark:| {kaldi_root}/src/featbin/add-deltas ark,p:- ark:-" '
                           ).format(compute_cmvn_cmd=computeCmvnCmd,
                                    mfcc_feats_path=mfccFeatsPath,
                                    kaldi_root=self.common.kaldiRoot)        
                                            
                # create a pipe using sh, output of gmm_latgen_faster piped into lattice_oracle
                # piping in contents of tokens_graphs_scp_path and writing to edits_path
                # note: be careful, as of date sh seems to swallow exceptions in the inner pipe
                #   https://github.com/amoffat/sh/issues/309
                hypLines = latticeBestPath(
                    gmmLatgenFaster(
                        '--acoustic-scale=0.1',
                        '--beam=12',
                        '--max-active=1000',
                        '--lattice-beam=10.0',
                        '--max-mem=50000000',
                        self.common.acousticModelPath,
                        f'scp,p:{tokensGraphsScpPath}',  # fsts-rspecifier
                        f'ark,p:{featsCmd} |',           # features-rspecifier
                        'ark:-',                                 # lattice-wspecifier
                        _err=errLog,
                        _piped=True),
                    '--acoustic-scale=0.06',
                    f"--word-symbol-table={self.common.symbolTablePath}",
                    'ark,p:-',
                    'ark,t:-',
                    _iter=True,
                    _err=errLog
                )
            except ErrorReturnCode_1 as e:
                # No data (e.g. all wavs unreadable)
                hypLines = []
                log('e.stderr: ', e.stderr)

            def splitAlsoEmpty(s):
                cols = s.split(maxsplit=1)
                if len(cols) == 1:
                    return cols[0], ''
                elif len(cols) == 2:
                    return cols[0], cols[1]
                else:
                    raise ValueError('Unexpected')

            hyps = {str(recId): tok_ for recId, tok_ in
                    (splitAlsoEmpty(line.strip()) for line in hypLines)}

            refs = {str(recId): tok_ for recId, tok_ in
                    ((r['recId'], self.common.symToInt(r['token']))
                     for r in recordings)}
        
            #for r in recordings:
            #    print(r, self.common.symToInt(r['token']))
                     
            details = {hypKey: MarosijoAnalyzer(hypTok.split(), refs[hypKey].split(), self.common).details() for
                       hypKey, hypTok in hyps.items()}
            # 'empty' analysis in case Kaldi couldn't analyse recording for some reason
            # look at MarosijoAnalyzer.details() for format
            placeholderDetails = {
                'hybrid': 0.0,
                'phone_acc': 0.0,
                'wer': 0.0,
                'onlyInsOrSub': False,
                'correct': 0,
                'sub': 0,
                'ins': 0,
                'del': 0,
                'startdel': 0,
                'enddel': 0,
                'extraInsertions': 0,
                'empty': False,
                'distance': 0
            }

            edits = {hypKey: details[hypKey]['distance'] for
                     hypKey, hypTok in hyps.items()}

            qcReport = {"requestId": str(uuid.uuid4()), # just use a uuid
                        "totalStats": {"accuracy": 0.0},
                        "perRecordingStats": []}

            cumAccuracy = 0.0

            for r in recordings:
                error = ''
                try:
                    # this is the old wer where a single phoneme is treated as a single word
                    old_wer = edits[str(r['recId'])] / len(r['token'].split())
                except KeyError as e:
                    # Kaldi must have choked on this recording for some reason
                    if isWavHeaderOnly(r['recPath']):
                        error = 'wav_header_only'
                        log('Error, only wav header in recording: {} for session: {}; {}'
                            .format(r['recId'], repr(e)))
                    else:
                        # unknown error
                        error = 'unknown_error'
                        log('Error, unknown error processing recording: {} for session {}; {}'
                            .format(r['recId'], repr(e)))

                try:
                    hyp =  ' '.join([self.common.symbolTableToInt[x] 
                    for x in hyps[str(r['recId'])].split(' ')]) # hypothesis (words not ints)
                except KeyError as e:
                    if hyps[str(r['recId'])] == '':
                        hyp = ''
                    else:
                        if not error:
                            error = 'hyp_error'
                            log('Error, hypothesis error processing recording: {} for session {}; {}'
                                .format(r['recId'], repr(e)))

                if not error:
                    old_wer_norm = 0.0 if 1 - old_wer < 0 else 1 - old_wer
                else:
                    old_wer_norm = 0.0
                    hyp = ''

                prec = qcReport['perRecordingStats']
                if not error:
                    analysis = details[str(r['recId'])]
                    analysis.update(error='no_error')
                else:
                    analysis = placeholderDetails
                    analysis.update(error=error)

                analysis.update(old_wer_norm=old_wer_norm)
                analysis.update(hyp=hyp)

                # handle specific errors
                if error == 'wav_header_only':
                    analysis.update(empty=True)

                # use phone accuracy (seemed to give best results)
                accuracy = analysis['phone_acc']

                stats = {"accuracy": accuracy}
                cumAccuracy += accuracy

                stats.update(analysis)
                prec.append({"recordingId": r['recId'], "recPath": r['recPath'], "sentence": r['token'], "is valid?": r['valid'], "stats": stats})
                

            try:
                avgAccuracy = cumAccuracy / len(qcReport['perRecordingStats'])
            except ZeroDivisionError:
                avgAccuracy = 0.0
            else:
                qcReport['totalStats']['accuracy'] = avgAccuracy
                qcReport['totalStats']['avgAcc'] = avgAccuracy

            # If a report exists, we update it.
            # TODO: Do this more efficiently. Need to change how we store reports.
            strReport = None
            if strReport:
                oldReport = json.loads(strReport.decode('utf-8'))

                newAvgAccuracy = (oldReport['totalStats']['accuracy'] + qcReport['totalStats']['accuracy']) / 2
                recsDoneThisBatch = len(qcReport['perRecordingStats'])
                newLowerUtt = oldReport['totalStats']['lowerUtt'] + recsDoneThisBatch
                newUpperUtt = oldReport['totalStats']['upperUtt'] + recsDoneThisBatch

                qcReport = update(oldReport, qcReport)

                qcReport['totalStats']['accuracy'] = newAvgAccuracy
                qcReport['totalStats']['lowerUtt'] = newLowerUtt
                qcReport['totalStats']['upperUtt'] = newUpperUtt
            else:
                qcReport['totalStats']['lowerUtt'] = 0
                qcReport['totalStats']['upperUtt'] = len(qcReport['perRecordingStats'])
           
        return qcReport
