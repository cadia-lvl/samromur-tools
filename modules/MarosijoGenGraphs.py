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

import sh
from os import  environ, mkdir, remove
from os.path import join, dirname,  exists
from multiprocessing import Process
from config import conf

from modules.marosijoCommon import MarosijoCommon

def genGraphs(prompts:list):
    """
    Generate decoding graphs for each token for our Marosijo module.
    Only needs to be run once (for each version of the tokens).
    Parameters:
        prompts      path to the promtps list on format "tokId token"
    """

    output_folder = conf['model']

    if not exists(output_folder):
        mkdir(output_folder)

    graphsArkPath = join(output_folder, 'graphs.ark')
    graphsScpPath = join(output_folder, 'graphs.scp')

    if exists(graphsArkPath):
       remove(graphsArkPath)

    if exists(graphsScpPath):
       remove(graphsScpPath) 
       
    common = MarosijoCommon(join('modules', 'local'), graphs=False)

    #: Shell commands
    makeUtteranceFsts = sh.Command(join(dirname(__file__),'./marosijo_make_utterance_fsts.sh'))
    
    fstEnv = environ.copy()
    fstEnv['PATH'] = '{}/tools/openfst/bin:{}'.format(conf['kaldi_root'], fstEnv['PATH'])

    makeUtteranceFsts = makeUtteranceFsts.bake(_env=fstEnv)
    compileTrainGraphsFsts = sh.Command(f"{conf['kaldi_root']}/src/bin/compile-train-graphs-fsts")

    tokensLines = []
    if type(prompts) == list:
        tokensF = prompts
    else:
        tokensF = [p.rstrip('\n') for p in open(prompts)]
    for line in tokensF:
        tokenKey, token = line.split('\t')
        tokenInts = common.symToInt(token.lower())
        tokensLines.append('{} {}'.format(tokenKey, tokenInts))
            
    #simpleLog('Compiling the decoding graphs (files {} and {}).This step can take some time.'
    #          .format(graphsArkPath, graphsScpPath))

    compileTrainGraphsFsts(
        makeUtteranceFsts(
            common.phoneLmPath,
            common.symbolTablePath,
            _in='\n'.join(tokensLines) + '\n',
            _piped=True
        ),
        '--verbose=4',
        '--batch-size=1',
        '--transition-scale=1.0',
        '--self-loop-scale=0.1',
        '--read-disambig-syms={}'.format(common.disambigIntPath),
        '{tree}'.format(tree=common.treePath),
        common.acousticModelPath,
        common.lexiconFstPath,
        'ark:-',
        'ark,scp:{ark},{scp}'.format(ark=graphsArkPath,
                                     scp=graphsScpPath)
    )

