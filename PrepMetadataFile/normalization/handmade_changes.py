from re import sub


def rules(s):    
    if s == 'ljósin dofna og þættir 2 og 3 tengjast með instrumental tónlist':
        s = 'ljósin dofna og þættir tvö og þrjú tengjast með instrumental tónlist'

    elif s == 'atriði 10 og 11 tengjast með instrumental tónlist':
        s = 'atriði tíu og ellefu tengjast með instrumental tónlist'

    elif s == 'stekkjarsnoppur innri fróðárdalur bakki 1 oddnýjargil':
        s = 'stekkjarsnoppur innri fróðárdalur bakki eitt oddnýjargil'

    elif s == 'langamýri nær langamýri fjær helga 1 surtteigshólar':
        s = 'langamýri nær langamýri fjær helga eitt surtteigshólar'

    elif s == 'strandarþúfa dys brúðgumagjá 1 hafnir':
        s = 'strandarþúfa dys brúðgumagjá eitt hafnir'     

    elif s == 'minnst tvær a 4 síður með 1½ línubili leturstærð':
        s = 'minnst tvær a fjórir síður með einu og hálfu línubili leturstærð'

    elif s == 'lambaflá bygg 1 dýjateigur karlsteigur':
        s = 'lambaflá bygg eitt dýjateigur karlsteigur'   

    elif s == 'tóttarhóll fyrir neðan fell skútugrafir 2 bolakinn':
        s = 'tóttarhóll fyrir neðan fell skútugrafir tvö bolakinn'   

    elif s == 'katatorfa neðri draghóll könguhólsbrekka jaðrar 1':
        s = 'katatorfa neðri draghóll könguhólsbrekka jaðrar eitt'   

    elif s == 'það sem ég ætla að verða þegar ég verð orðinn stór; d':
        s = 'það sem ég ætla að verða þegar ég verð orðinn stór'   

    elif s == 'k2 ytra volgurófartún borgarásmýri einbúalágar':
        s = 'k tveir ytra volgurófartún borgarásmýri einbúalágar'   

    elif s == 'fold 2 helga 2 mýrartún nær hundsöxl':
        s = 'fold tvö helga tvö mýrartún nær hundsöxl'

    elif s == "hann opna'i dyrnar inn í eldhúsið og dásamleg matarlyktin tók á móti honum":
        s = "hann opnaði dyrnar inn í eldhúsið og dásamleg matarlyktin tók á móti honum"

    elif s == 'oddleifsmýri syðsti háls bil/beggja litlastrýta':
        s = 'oddleifsmýri syðsti háls bil beggja litlastrýta'

    elif s == '﻿þetta er eintakið':
        s = 'þetta er eintakið'
    
    elif s == 'í t mellon og mj':
        s = 'i t mellon og m punktur j punktur'

    elif s == 'i og ii':
        s = 'fyrsti og annar'
    
    elif s == 'kirk gs je':
        s = 'kirk g punktur s j punktur e'

    elif s == "a ii b ii":
        s = "a tveir b tveir"

    elif s == "patrik fer líka á bar inn":
        s = "patrik fer líka á barinn"
    
    elif s == "má þar nefna freebsd":
        s = "má þar nefna free b s d"

    elif s == 'sandeyri 2 hlaupakvörn stórisjónarhóll gataklöpp':
	    s = 'sandeyri tvö hlaupakvörn stórisjónarhóll gataklöpp'

    elif s == 'efstidalur eyri 1 hjallkárseyri finnshús':
        s = 'efstidalur eyri einn hjallkárseyri finnshús'

    elif s == 'markgrófarás þverárskarð fögrugrös/neðri flathöfðalækur':
        s = 'markgrófarás þverárskarð fögrugrös neðri flathöfðalækur'

    elif s == 'hann tók fram rafrænu leiðbeiningabókina og sló inn spurninguna;':
        s = 'hann tók fram rafrænu leiðbeiningabókina og sló inn spurninguna'

    elif s == 'hverir gestreiðarstaðavatn stekkur/ þverhæðargreni':
        s = 'hverir gestreiðarstaðavatn stekkur þverhæðargreni'

    elif s == 'hvaða sjónvarpsþættir gerast í bænum quahog':
        s = 'hvaða sjónvarpsþættir gerast í bænum quahog'

    elif s == 'mýrartún fjær hríslutún kringlumýri 2 ármótsheiði':
        s = 'mýrartún fjær hríslutún kringlumýri tvö ármótsheiði'

    elif s == 'gilbúi hrútanefjaurð þjófaskúti 080618':
        s = 'gilbúi hrútanefjaurð þjófaskúti núll átta núll sex átján'

    elif s == 'selbalar tóubrekkur mýrarvöllur brúðgumagjá 2':
        s = 'selbalar tóubrekkur mýrarvöllur brúðgumagjá tvö'

    elif s == 'sigurhylur aquarium þjótur svartaflös':
        s = 'sigurhylur aquarium þjótur svartaflös'

    elif s == 'fjóstún vestur 1 hellisvöllur lambafit':
        s = 'fjóstún vestur einn hellisvöllur lambafit'

    elif s == 'bótaborgarlækir syðstuvegabrýr veraldadarofsi 1 álftadráttur':
        s = 'bótaborgarlækir syðstuvegabrýr veraldadarofsi tvö álftadráttur'

    elif s == 'hvað ef hann hafði rangt fyrir ‚ser og truflaði undirbúning jólahátíðarinnar':
        s = 'hvað ef hann hafði rangt fyrir sér og truflaði undirbúning jólahátíðarinnar'

    elif s == 'snjóölduver syðra viðvíkurbjörg skorarhlíðar fögrugrös/hærri':
        s = 'snjóölduver syðra viðvíkurbjörg skorarhlíðar fögrugrös hærri'

    elif s == 'jón ólafur var 12 ára og hét í höfuðið á báðum öfum sínum':
        s = 'jón ólafur var tólf ára og hét í höfuðið á báðum öfum sínum'

    elif s == 'hvort var á undan; sex daga stríðið eða jom kippur stríðið':
        s = 'hvort var á undan sex daga stríðið eða jom kippur stríðið'

    elif s == 'breiðflöt fold 1 ytrivík heimastanes':
        s = 'breiðflöt fold eitt ytrivík heimastanes'

    elif s == 'syllur brúarhylur koddi 1930':
        s = 'syllur brúarhylur koddi nítján hundruð og þrjátíu'

    elif s == 'hnúksdalur veraldarofsi 2 bylta kattartunga':
        s = 'hnúksdalur veraldarofsi tvö bylta kattartunga'

    elif s == 'villavað hellur 1 fjósakot minniborg':
        s = 'villavað hellur eitt fjósakot minniborg'

    elif s == 'bættu góðri fitu í matinn; örlítil lárpera fræ hnetur eða góð ólífuolía':
        s = 'bættu góðri fitu í matinn örlítil lárpera fræ hnetur eða góð ólífuolía'

    elif s == 'en það sem mér sýnist á öllu og er lílega 99% öruggt er að':
        s = 'en það sem mér sýnist á öllu og er lílega níutíu og níu prósent öruggt er að'       
    
    elif s == 'jú hann er ástæðan fyrir þv´iað við erum hérna sagði jón ólafur og hneigði sig að japönskum sið':
        s = 'jú hann er ástæðan fyrir því að við erum hérna sagði jón ólafur og hneigði sig að japönskum sið'

    elif s == 'rauða eplið gengur/hleypur yfir sviðið':
        s = 'rauða eplið gengur hleypur yfir sviðið'

    elif s == 'hann var nú enn líkari jólasveininum—eins og maður ímyndaði sér hann—en áður':
        s = 'hann var nú enn líkari jólasveininum eins og maður ímyndaði sér hann en áður'

    elif s == 'vertu lastvar – þá lasta þig færri':
        s = 'vertu lastvar þá lasta þig færri'
    
    elif s == 'hvor er þyngri; grágæs eða smyrill':
        s = 'hvor er þyngri grágæs eða smyrill'    

    elif s == 'en viltu vera vinur eða hvaðvers 2 sem endar á hep tú':
        s = 'en viltu vera vinur eða hvaðvers tveir sem endar á hep tú'  

    return s
