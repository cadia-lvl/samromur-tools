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

    if s  == 'sandeyri 2 hlaupakvörn stórisjónarhóll gataklöpp':
	    s = 'sandeyri tvö hlaupakvörn stórisjónarhóll gataklöpp'

    if s  == 'efstidalur eyri 1 hjallkárseyri finnshús':
        s = 'efstidalur eyri einn hjallkárseyri finnshús'

    if s  == 'markgrófarás þverárskarð fögrugrös/neðri flathöfðalækur':
        s = 'markgrófarás þverárskarð fögrugrös neðri flathöfðalækur'

    if s  == 'hann tók fram rafrænu leiðbeiningabókina og sló inn spurninguna;':
        s = 'hann tók fram rafrænu leiðbeiningabókina og sló inn spurninguna'

    if s  == 'hverir gestreiðarstaðavatn stekkur/ þverhæðargreni':
        s = 'hverir gestreiðarstaðavatn stekkur þverhæðargreni'

    if s  == 'hvaða sjónvarpsþættir gerast í bænum quahog':
        s = 'hvaða sjónvarpsþættir gerast í bænum quahog'

    if s  == 'mýrartún fjær hríslutún kringlumýri 2 ármótsheiði':
        s = 'mýrartún fjær hríslutún kringlumýri tvö ármótsheiði'

    if s  == 'gilbúi hrútanefjaurð þjófaskúti 080618':
        s = 'gilbúi hrútanefjaurð þjófaskúti núll átta núll sex átján'

    if s  == 'selbalar tóubrekkur mýrarvöllur brúðgumagjá 2':
        s = 'selbalar tóubrekkur mýrarvöllur brúðgumagjá tvö'

    if s  == 'sigurhylur aquarium þjótur svartaflös':
        s = 'sigurhylur aquarium þjótur svartaflös'

    if s  == 'fjóstún vestur 1 hellisvöllur lambafit':
        s = 'fjóstún vestur einn hellisvöllur lambafit'

    if s  == 'bótaborgarlækir syðstuvegabrýr veraldadarofsi 1 álftadráttur':
        s = 'bótaborgarlækir syðstuvegabrýr veraldadarofsi tvö álftadráttur'

    if s  == 'hvað ef hann hafði rangt fyrir ‚ser og truflaði undirbúning jólahátíðarinnar':
        s = 'hvað ef hann hafði rangt fyrir sér og truflaði undirbúning jólahátíðarinnar'

    if s  == 'snjóölduver syðra viðvíkurbjörg skorarhlíðar fögrugrös/hærri':
        s = 'snjóölduver syðra viðvíkurbjörg skorarhlíðar fögrugrös hærri'

    if s  == 'jón ólafur var 12 ára og hét í höfuðið á báðum öfum sínum':
        s = 'jón ólafur var tólf ára og hét í höfuðið á báðum öfum sínum'

    if s  == 'hvort var á undan; sex daga stríðið eða jom kippur stríðið':
        s = 'hvort var á undan sex daga stríðið eða jom kippur stríðið'

    if s  == 'breiðflöt fold 1 ytrivík heimastanes':
        s = 'breiðflöt fold eitt ytrivík heimastanes'

    if s  == 'syllur brúarhylur koddi 1930':
        s = 'syllur brúarhylur koddi nítján hundruð og þrjátíu'

    if s  == 'hnúksdalur veraldarofsi 2 bylta kattartunga':
        s = 'hnúksdalur veraldarofsi tvö bylta kattartunga'

    if s  == 'villavað hellur 1 fjósakot minniborg':
        s = 'villavað hellur eitt fjósakot minniborg'

    if s == 'bættu góðri fitu í matinn; örlítil lárpera fræ hnetur eða góð ólífuolía':
        s = 'bættu góðri fitu í matinn örlítil lárpera fræ hnetur eða góð ólífuolía'

    return s
