from sys import maxsize
import itertools

import numpy as np
from modules.utils import  log

class MarosijoError(Exception):
    pass


class MarosijoAnalyzer(object):
    """MarosijoAnalyzer
    ===================

    Does analysis of decoded output, given reference and hypothesis
    string.

    """
    def __init__(self, hypothesis, reference, common):
        self.reference = reference
        self.hypothesis = hypothesis
        self.common = common # used to grab info like symbolTable

    @staticmethod
    def _levenshteinDistance(hyp, ref, cost_sub=1, cost_del=1, cost_ins=1):
        '''
        Returns the minimum edit distance (Levenshtein distance) between
        sequences `ref` and `hyp`, and the corresponding Levenshtein matrix.

        '''
        m, n = len(hyp)+1, len(ref)+1
        d = np.zeros((m, n))
        d[1:, 0] = range(1, m)
        d[0, 1:] = range(1, n)

        edits = []
        for j in range(1, n):
            for i in range(1, m):
                del_ = d[i-1, j] + cost_del
                ins_ = d[i, j-1] + cost_ins
                sub_ = d[i-1, j-1]
                sub_ += cost_sub if hyp[i-1] != ref[j-1] else 0
                d[i, j] = min(del_, ins_, sub_)

        return int(d[-1, -1]), d

    @staticmethod
    def levenshteinDistance(a, b):
        d, _ = _levenshteinDistance(a, b)
        return d

    @staticmethod
    def shortestPath(d):
        """Returns the shortest sequence of edits in the levenshtein matrix `d`

        """
        SUBCORR, INS, DEL = 0, 1, 2
        nDel, nIns, nSub, nCor = 0, 0, 0, 0
        revEditSeq = []
        i, j = np.shape(d)
        i, j = i-1, j-1
        # Special case for only empty inputs
        if i == 0 and j != 0:
            nDel = j
            revEditSeq = ['D'] * nDel
        elif i != 0 and j == 0:
            nIns = i
            revEditSeq = ['I'] * nIns
        elif i != 0 and j != 0:
            outOfBounds = False
            while not outOfBounds:
                del_ = d[i, j-1] if i >= 0 and j > 0 else np.inf
                ins = d[i-1, j] if i > 0 and j >= 0 else np.inf
                subOrCor = d[i-1, j-1] if i > 0 and j > 0 else np.inf
                idxMin = np.argmin([subOrCor, ins, del_])
                if idxMin == DEL:
                    j -= 1
                    nDel += 1
                    revEditSeq.append('D')
                elif idxMin == INS:
                    i -= 1
                    nIns += 1
                    revEditSeq.append('I')
                elif idxMin == SUBCORR:
                    if d[i-1, j-1] != d[i, j]:
                        nSub += 1
                        revEditSeq.append('S')
                    else:
                        nCor += 1
                        revEditSeq.append('C')
                    i, j = i-1, j-1
                if i == 0 and j == 0:
                    outOfBounds = True
        return revEditSeq[::-1], nCor, nSub, nIns, nDel

    def _computeEdits(self):
        self._distance, self.d = self._levenshteinDistance(self.hypothesis, self.reference)
        self.seq, self.nC, self.nS, self.nI, self.nD = self.shortestPath(self.d)

    def _calculateHybridAccuracy(self) -> (float, float):
        """
        Hybrid accuracy is some sort of metric, attempts to locate correct words.
        E.g. ref: the dog jumped over the fence
             hyp: the /c/o/d/ ran over the tent
        would result in an accuracy of 3/6 + 1/3*1/6 = 0.555 for getting the, over, the and a 
        single phoneme from dog correct.
        Extra words are also treated as errors, e.g.
             ref: the dog jumped over the fence
             hyp: /i/n/s/e/r/t/i/o/n/ the dog jumped over the fence
        would divide insertion by the average phoneme count of words (if 5) and then
        accuracy would be 6 - 5/4 / 6 = 4.75/6 = 0.792
        TODO not make this average, but use an actual phoneme 2 grapheme and locate the words
        Words in middle, are compared to phonemes of the words from ref, and a ratio of correct
        phonemes calculated from that.

        accuracy c [0,1]

        also calculates regular WER (done here since the align hyp computation is needed and
        has already been done here) on a word level grouping hyp phonemes into words

        e.g. ref: the dog jumped over the fence
             hyp: the /c/o/d/ ran over the tent
        would result in a wer of 3/6 = 0.5 (3 substitutions)

        return:
            (hybrid, wer)
        """

        oovId = self.common.symbolTable['<UNK>']

        hyp = self.hypothesis
        ref = self.reference

        # convert all words in ref to phonemes
        try:
            ref_phones = [self.common.lexicon[self.common.symbolTableToInt[x]] for x in ref]

        except KeyError as e:
            # word in ref not in lexicon, abort trying to convert it to phonemes
            log('Warning: couldn\'t find prompt words in lexicon or symbol table (grading 0.0), prompt: {}'.format(self.common.intToSym(ref)), e=e)
            return (0.0, 0.0)

        aligned = self._alignHyp(hyp, ref)
        ali_no_oov = [x for x in aligned if x != -2] # remove oov for part of our analysis
        hyp_no_oov = [x for x in hyp if x != oovId]

        # mark positions of recognized words, e.g. rec_words = [0, 3, 5]
        rec_words = []
        # mark all strings of -1's (meaning we have phonemes inserted)
        minus_ones = [] # minus_ones = [(1,3), (4,5), ..], i.e. tuples of linked sequences of -1's
        inSequence = False
        seq = [] # partial sequence
        for i, a in enumerate(ali_no_oov):
            if a == -1 and not inSequence:
                inSequence = True
                seq.append(i)
            if a != -1 and inSequence:
                inSequence = False
                seq.append(i)
                minus_ones.append(seq)
                seq = []
            # if we have -1's at the end of ali_no_oov
            if i == len(ali_no_oov) - 1 and a == -1 and inSequence:
                seq.append(len(ali_no_oov))
                minus_ones.append(seq)
            if a >= 0:
                rec_words.append(a)

        # for each sequence of -1's calculate phoneme overlap with corresponding words.
        # e.g. if ref: the cat jumped
        #         hyp: the cat j u m p
        # we would calc the overlap of 'j u m p e d' with 'j u m p'
        ratios = [] # len(ratios) == len(minus_ones) ratios of each sequence phoneme overlap (contribution to word error rate)

        wer_insertions = 0

        for seq in minus_ones:
            # convert seq to phoneme list, grab e.g. !h from symbolTable and remove ! to match with lexicon
            seq_phones = [self.common.symbolTableToInt[x][1:] for x in hyp_no_oov[seq[0] : seq[1]]]
            ref_phones_range = () # which indices in ref_phones do we want to compare to? (which words)
            # figure out which words we should compare each phoneme sequence with
            # find out if we are a -1 sequence in the beginning, middle or end of the hyp
            if seq[0] == 0:
                # beginning, look at all words up to the first recognized word
                if rec_words:
                    ref_phones_range = (0, rec_words[0])
                else:
                    # no recognized words, compare to entire ref
                    ref_phones_range = (0, len(ref_phones))
            elif seq[-1] == len(hyp_no_oov):
                # end, look at words from last recognized word
                ref_phones_range = (rec_words[-1]+1, len(ref_phones))
            else:
                # middle, look at words between recognized words to the left&right of this sequence
                # since this is neither beginning or end, we know we have recognized words on both sides
                # e.g. aligned: [0, 1, -1, -1, -1, 4]
                # we want to look at words ref[2:4]
                ref_phones_range = (ali_no_oov[seq[0]-1]+1, ali_no_oov[seq[1]])
            
            hybridPenalty = 1.5
            if ref_phones_range[1] - ref_phones_range[0] > 0:
                # use formulaAccura more (e.g. our aligner inserted more phonemes than are in
                # the reference), we can get a penalty for at most (1-hybridPenalty)*ref word count
                # for the entire sequence.
                N = sum([len(ref_phones[i]) for i in range(ref_phones_range[0], ref_phones_range[1])])
                ed, _ = self._levenshteinDistance(seq_phones, 
                                                  list(
                                                    itertools.chain.from_iterable(
                                                        ref_phones[ref_phones_range[0] : ref_phones_range[1]])
                                                  ))

                ratio = 1 - min(ed / N, hybridPenalty)
                normalized_ratio = ratio*(ref_phones_range[1] - ref_phones_range[0])
                ratios.append(normalized_ratio)
            else:
                # no words to compare to (empty interval this seq compares to)
                # attempt to attempt to give some sort of minus penalty
                # in similar ratio to the one above (if hybridPenalty=1.5 then at most -1/2*wc)
                # use average phoneme count from lexicon, and give at most
                # an error of 1/2 that. For example if avg=5 and our seq has
                # 11 phonemes we give an error of -1/2 * floor(11/5) = -1
                ratios.append((1 - hybridPenalty) * int((seq[1]-seq[0]) / self.common.avgPhonemeCount))

                wer_insertions += 1

        hybrid = max((len(rec_words) + sum(ratios)) / len(ref) , 0)
        # WAcc = (H - I)/N
        # https://en.wikipedia.org/wiki/Word_error_rate
        wer    = (len([x for x in aligned if x >= 0]) - wer_insertions) / len(ref)

        return (hybrid, wer)


    def _calculatePhoneAccuracy(self):
        """
        Similar to _calculateHybridAccuracy, except uses phonemes only.
        Converts ref and hyp to phonemes and does a direct edit distance on the entire thing.
        phone_accuracy c [0,1]
        """
        oovId = self.common.symbolTable['<UNK>']

        hyp = self.hypothesis
        ref = self.reference

        # convert all words in ref to phonemes, excluding oov
        try:
            ref_phones = [self.common.lexicon[self.common.symbolTableToInt[x]] for x in ref if x != oovId]


        except KeyError as e:
            # word in ref not in lexicon, abort trying to convert it to phonemes
            log('Warning: couldn\'t find prompt words in lexicon or symbol table (grading with 0.0), prompt: {}'.format(self.common.intToSym(ref)))
            return 0.0

        # convert all words in hyp to phonemes
        hyp_phones = []
        for x in hyp:
            try:
                hyp_phones.append(self.common.lexicon[self.common.symbolTableToInt[x]])
            except KeyError as e:
                # word in hyp not in lexicon, must be a phoneme, in which case just append it and remove the !
                hyp_phones.append([self.common.symbolTableToInt[x][1:]])

        ref_phones = list(itertools.chain.from_iterable(ref_phones))
        hyp_phones = list(itertools.chain.from_iterable(hyp_phones))

        N = len(ref_phones)
        ed, _ = self._levenshteinDistance(hyp_phones, 
                                          ref_phones)

        try:
            ratio = 1 - min(ed / N, 1)
        except ZeroDivisionError as e:
            ratio = 0.0

        return ratio

    def _alignHyp(self, hyp, ref) -> list:
        """
        Attempts to enumerate the hypothesis in some smart manner. E.g.

        ref:    the dog jumped    across
        hyp:        dog /j/u/m/p/ across
        output:     1   -1-1-1-1  3

        Where /j/u/m/p/ represents 4 phonemes inserted instead of jumped and
        these would usually be the integer ids of the words.
        Output is the indices in ref the words in hyp correspond to.

        Parameters:
            hyp     list with the integer ids of the hyp words
            ref     same as hyp with the reference

        Pairs the hypotheses with the index of correct words in the reference. 
        -1 for hypotheses words not in ref (should only be phonemes)
        -2 if hyp word is oov <UNK>.

        Would have used align-text.cc from Kaldi, but it seemed to not perform well
        with all the inserted phonemes (on a very informal check).

        Better description of the algorithm used:
            TO DO WRITE DESC
        """

        # private functions to _alignHyp
        def _wordsBetween(aligned, idx):
            """
            Attempts to see if there are any words between
            the current idx and the last matched word in hyp, 
            and no word in between it in the ref.
            E.g.
                ref: joke about stuff
                hyp: joke and go to stuff

            With: aligned = [0, -1, -1, -1]
                  idx     = 2
            Would result in False, since "and go to" could be the aligners interpretation of about.

                ref: go to France
                hyp:    to five France

            With: aligned = [1, -1]
                  idx     = 2
            Would result in True, since "five" is between to and France
            """
            newAligned = [x for x in aligned if x != -1] # remove -1's
            try:
                lastMatch = newAligned[-1]
            except IndexError as e:
                return False # return false if no recognized word

            if idx - lastMatch > 1:
                return False

            # if we have some -1's after our last match, return true
            if aligned.index(lastMatch) != len(aligned) - 1:
                return True

            return False

        def _isLater(idx, ref):
            """
            Checks to see if ref[idx] is repeated in ref somewhere later,
            and in which case return the later idx.

            Returns -1 if ref[idx] is not repeated.
            """
            refSlice = ref[idx:]
            refSlice[0] = -1
            try:
                return refSlice.index(ref[idx]) + idx
            except ValueError as e:
                return -1

        def _isEarlier(idx, ref):
            """
            Checks to see if ref[idx] is repeated in ref somewhere earlier,
            and in which case return the earlier idx.

            Returns -1 if ref[idx] is not earlier.
            """
            upToIdx = ref[0:idx+1]
            isEarlier = _isLater(0, upToIdx[::-1]) # isEarlier === isLater(new idx, reversed list)
            return len(upToIdx) - isEarlier - 1 if isEarlier != -1 else -1

        oovId = self.common.symbolTable['<UNK>']
        refC = list(ref) # ref copy
        aligned = []
        for h in hyp:
            try:
                if h == oovId:
                    aligned.append(-2)
                    continue

                idx = refC.index(h)
                # handle cases with multiple instances of the same word
                # in case our hypothesised index in the hyp is lower than 
                # some idx in aligned, we know that cannot be, so the only
                # chance is that it is the same word later in the hyp (or not there)
                # In addition, if we see 1 or more words (like dung in the example)
                # which could have been the interpretation of dog, we assume it is the
                # second instance of the word (if present, otherwise assume first instance).
                # e.g. 
                #    ref: the dog ate the dog
                #    hyp: the dung dog
                #    res:   0   -1   4
                refC[idx] = -1 # remove word from ref if we match, in case we have multiple of the same
                while True:
                    try:
                        if any(idx < x for x in aligned) or _wordsBetween(aligned, idx):
                            idx = refC.index(h)
                            refC[idx] = -1
                        else:
                            break
                    except ValueError as e:
                        break
            except ValueError as e:
                idx = -1
            aligned.append(idx)
        # do a second pass
        # if the aligned array is not strictly non-decreasing, fix it
        # e.g. if aligned = [0, -1, -1, 3, 2]
        # see if the one marked 2 isn't supposed to be the same word later in ref
        # this could be problematic if the same 2 words are repeated twice,
        # and possibly if the same word is repeated 3 times as well
        prevA = -maxsize
        for i, a in enumerate(aligned):
            if a < 0:
                continue
            if a <= prevA:
                # we have decreasing
                newIdx = _isLater(a, ref)
                if newIdx != -1:
                    aligned[i] = newIdx
                else:
                    # now see if the 3 in the example above shouldn't be earlier
                    newIdx = _isEarlier(prevA, ref)
                    if newIdx != -1 and newIdx not in aligned:
                        aligned[i-1] = newIdx
                    else:
                        raise MarosijoError('Error: couldn\'t align {} with hyp: {} and ref: {} and aligned: {}'
                            .format(ref[a], hyp, ref, aligned))
            prevA = a

        return aligned

    def editSequence(self):
        """Returns sequence of edits as an iterable

        'C' for correct, 'S' for substitution, 'I' for insertion and
        'D' for deletions.

        """
        if not hasattr(self, 'seq'):
            self._computeEdits()
        return self.seq

    def edits(self):
        """Returns dict with edit counts

        """
        if not hasattr(self, 'nC'):
            self._computeEdits()
        return {'correct': self.nC, 'sub': self.nS, 'ins': self.nI,
                'del': self.nD, 'distance': self._distance}

    def details(self) -> '{hybrid: int\
            phone_acc: int\
            wer: int\
            onlyInsOrSub: bool\
            correct: int\
            sub: int\
            ins: int\
            del: int\
            startdel: int\
            enddel: int\
            extraInsertions: int\
            empty: bool\
            distance: int}':
        """Returns dict with details of analysis

        Distance (and the rest of the stats excluding hybrid) is calculated on a 
        mixture of word/phoneme level, since phonemes are words from this aligner.
        """

        res = self.edits()
        seq = self.editSequence()
        details = {'empty': False, 'onlyInsOrSub': False,
                   'enddel': 0, 'startdel': 0, 'extraInsertions': 0}
        details.update(res)
        #details.update(ops=seq)

        details['hybrid'], details['wer'] = self._calculateHybridAccuracy()
        details['phone_acc'] = self._calculatePhoneAccuracy()

        if not any([res['correct'], res['sub'], res['ins']]):
            # 1. Only deletions (hyp empty)?
            details['empty'] = True
        elif (any([res['ins'], res['sub']]) and not
              any([res['correct'], res['ins']])):
            # 2. Only insertions/substitutions?
            details['onlyInsOrSub'] = True
        else:
            # 2. Start/end deletions?
            for op in seq[::-1]:
                if op.upper() == 'D':
                    details['enddel'] += 1
                else: break
            for op in seq:
                if op.upper() == 'D':
                    details['startdel'] += 1
                else: break
            if (len(self.reference) == res['correct'] and res['ins'] and
                not any([res['sub'], res['del']])):
                details['extraInsertions'] = res['ins']

        return details

    def distance(self):
        if not hasattr(self, '_distance'):
            self._computeEdits()
        return self._distance
