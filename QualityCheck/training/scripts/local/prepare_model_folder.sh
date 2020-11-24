#!/bin/bash -eu
#
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
#     David Erik Mollberg <davidemollberg@gmail.com>


help_message="Usage: $0 <lang-dir> <exp-dir> <phone-lm-fst> <sample-freq> <lexicon> <out>"

err() {
  msg=$1
  code=${2:-1}
  echo "$msg" >&2
  exit $code
}

msg() {
  echo "$1" >&2
}

if [ $# -ne 6 ]; then
  err "$help_message"
fi

lang=$1
exp=$2
phone_lm_fst=$3
sample_freq=$4
lexicon=$5
out=$6

mkdir -p $out


msg "Copying files from $lang"
cp $lang/L_disambig.fst $out/lexicon_fst \
  || err "Lexicon FST missing from $lang"
cp $lang/oov.int $out/oov_int \
  || err "oov.int missing from $lang"
cp $lang/words.txt $out/symbol_tbl \
  || err "words.txt missing from $lang"
cp $lang/phones/disambig.int $out/disambig_int \
  || err "phones/disambig.int missing from $lang"

msg "Copying files from $exp"
cp $exp/tree $out/tree \
  || err  "tree missing from $exp"
cp $exp/final.mdl $out/acoustic_mdl \
  || err "final.mdl missing from $exp"

msg "Using Phoneme LM from $phone_lm_fst"
cp $phone_lm_fst $out/phone_lm \
  || err "$phone_lm_fst missing"

msg "Copying lexicon as is."
cp $lexicon $out/lexicon.txt \
 || err "$lexicon missing"


msg "Done"
msg "Output in $out"
