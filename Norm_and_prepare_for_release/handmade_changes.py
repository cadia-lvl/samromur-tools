from re import sub


def rules(s):    
    if s == 'ljósin dofna og þættir 2 og 3 tengjast með instrumental tónlist':
        s = 'ljósin dofna og þættir tvö og þrjú tengjast með instrumental tónlist'

    if s == 'atriði 10 og 11 tengjast með instrumental tónlist':
        s = 'atriði tíu og ellefu tengjast með instrumental tónlist'

    if s == 'stekkjarsnoppur innri fróðárdalur bakki 1 oddnýjargil':
        s = 'stekkjarsnoppur innri fróðárdalur bakki eitt oddnýjargil'

    if s == 'langamýri nær langamýri fjær helga 1 surtteigshólar':
        s = 'langamýri nær langamýri fjær helga eitt surtteigshólar'

    if s == 'strandarþúfa dys brúðgumagjá 1 hafnir':
        s = 'strandarþúfa dys brúðgumagjá eitt hafnir'     

    if s == 'minnst tvær a 4 síður með 1½ línubili leturstærð':
        s = 'minnst tvær a fjórir síður með einu og hálfu línubili leturstærð'

    if s == 'lambaflá bygg 1 dýjateigur karlsteigur':
        s = 'lambaflá bygg eitt dýjateigur karlsteigur'   

    if s == 'tóttarhóll fyrir neðan fell skútugrafir 2 bolakinn':
        s = 'tóttarhóll fyrir neðan fell skútugrafir tvö bolakinn'   

    if s == 'katatorfa neðri draghóll könguhólsbrekka jaðrar 1':
        s = 'katatorfa neðri draghóll könguhólsbrekka jaðrar eitt'   

    if s == 'það sem ég ætla að verða þegar ég verð orðinn stór; d':
        s = 'það sem ég ætla að verða þegar ég verð orðinn stór'   

    if s == 'k2 ytra volgurófartún borgarásmýri einbúalágar':
        s = 'k tveir ytra volgurófartún borgarásmýri einbúalágar'   

    if s == 'fold 2 helga 2 mýrartún nær hundsöxl':
        s = 'fold tvö helga tvö mýrartún nær hundsöxl'

    if s == "hann opna'i dyrnar inn í eldhúsið og dásamleg matarlyktin tók á móti honum":
        s = "hann opnaði dyrnar inn í eldhúsið og dásamleg matarlyktin tók á móti honum"

    if s == 'oddleifsmýri syðsti háls bil/beggja litlastrýta':
        s = 'oddleifsmýri syðsti háls bil beggja litlastrýta'

    if s == '﻿þetta er eintakið':
        s = 'þetta er eintakið'
    
    if s == 'í t mellon og mj':
        s = 'i t mellon og m punktur j punktur'

    if s == 'i og ii':
        s = 'fyrsti og annar'
    
    if s == 'kirk gs je':
        s = 'kirk g punktur s j punktur e'

    if s == "a ii b ii":
        s = "a tveir b tveir"

    if s == "patrik fer líka á bar inn":
        s = "patrik fer líka á barinn"
    
    if s == "má þar nefna freebsd":
        s = "má þar nefna free b s d"

    return s
