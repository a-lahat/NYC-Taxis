
import networkx as nx
import statistics
import pandas as pd
from sodapy import Socrata
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from pandas.tseries.holiday import USFederalHolidayCalendar
from random import randrange
from fuzzywuzzy import fuzz
from urllib.request import urlopen
import json
from shapely.geometry import shape, mapping
from shapely.geometry import Point
import sys

#check rank
def addLocationIdToRealEstate(df, df_taxiArea):
    dict = {
        "KINGSBRIDGE HTS/UNIV HTS": "Kingsbridge Heights",
        "OLD MILL BASIN": "Marine Park/Mill Basin",
        "AIRPORT LA GUARDIA": "LaGuardia Airport",
        "ST. ALBANS": "Saint Albans",
        "CASTLETON CORNERS": "Charleston/Tottenville",
        "RICHMONDTOWN-LIGHTHS HILL": "Richmond Hill",
        "ROSSVILLE-CHARLESTON": "Charleston/Tottenville",
        "CASTLE HILL/UNIONPORT": "Soundview/Castle Hill",
        "OLD MILL BASIN": "Marine Park/Mill Basin",
        "ARROCHAR-SHORE ACRES": "Arrochar/Fort Wadsworth",
        "UPPER WEST SIDE (79-96)": "Upper West Side South",
        "UPPER EAST SIDE (79-96)": "Upper East Side North",
        "CASTLE HILL/UNIONPORT": "Soundview/Castle Hill"
    }

    # add location id to df from df_taxi
    tuples_list = []
    for i in df['neighborhood']:
        maxToken = 0
        neighborhood_name = ""
        for j in df_taxiArea['zone']:
            fuzzT = fuzz.token_set_ratio(i, j)
            if fuzz.token_set_ratio(i, j) > maxToken:
                maxToken = fuzzT
                neighborhood_name = j
        if maxToken < 90:
            if i in dict:
                neighborhood_name = dict[i]
            else:
                neighborhood_name = ""
        tuples_list.append(neighborhood_name)
    # tuples_list = [max([(fuzz.token_set_ratio(i,j),j) for j in df_taxiArea['zone']]) for i in df['neighborhood']]
    # tuples_list = [i[1] for i in tuples_list]
    location_id = []
    for i in tuples_list:
        x = df_taxiArea.loc[df_taxiArea["zone"] == i]
        if x.empty:
            location_id.append(0)
        else:
            x.reset_index()
            location_id.append(x.iloc[0]['location_id'])
    df['location_id'] = location_id
    # df.to_csv('check.csv')


client = Socrata("data.cityofnewyork.us", "ghD7sxmh9I7Ud8yq8Au5YKort", timeout=100000)
results = client.get("5ebm-myj7",
                     where="type_of_home = '01 ONE FAMILY HOMES' OR type_of_home = '01 ONE FAMILY DWELLINGS'",
                    select='borough, neighborhood, median_sale_price, year', limit=100000
                    )
df = pd.DataFrame.from_records(results)
df['median_sale_price'] = pd.to_numeric(df['median_sale_price'])

df['year'] = pd.to_numeric(df['year'])

taxiAreaResult = client.get("755u-8jsi",
                    select='location_id, zone, borough', limit=100000
                    )
df_taxiArea = pd.DataFrame.from_records(taxiAreaResult)
df_taxiArea['location_id'] = pd.to_numeric(df_taxiArea['location_id'])
# df_taxiArea.set_index('location_id')

# add location id to df from df_taxi
addLocationIdToRealEstate(df, df_taxiArea)

d2017 = {'161': 0.017775496848995324, '162': 0.014979487502253313, '138': 0.008832840692553117, '163': 0.011551387873180583, '246': 0.008706212311358964, '233': 0.007620563201906263, '230': 0.015140458798998864, '239': 0.01265908023788349, '100': 0.007793328069112116, '263': 0.009873950753690342, '237': 0.01638481789444713, '211': 0.004692862849068119, '231': 0.010168985505658631, '140': 0.009447207082273831, '158': 0.0056880400391352125, '113': 0.007035753456267856, '4': 0.0032481513640951957, '170': 0.015080832105318123, '141': 0.011420156988165403, '186': 0.012973482818393809, '236': 0.018217152013544603, '90': 0.007276739661098146, '142': 0.01269151789632563, '264': 0.011139245273172903, '125': 0.0033009898609022204, '107': 0.010470821124658651, '145': 0.004922596800775683, '50': 0.0059924806543083745, '143': 0.006258083122664338, '249': 0.008121680764316777, '132': 0.010651616294134447, '75': 0.009062217489483763, '164': 0.010428263831815365, '234': 0.012926136139895916, '43': 0.006205624568343613, '48': 0.01343960508991485, '68': 0.010674245769871917, '137': 0.007373324651414092, '98': 0.0012567099676302792, '261': 0.0036267530672365357, '144': 0.005577049153948785, '229': 0.009039752485848639, '15': 0.0012303288599980254, '166': 0.0066505802140304285, '88': 0.003071237759255461, '42': 0.006971999369132727, '238': 0.011483158410565202, '235': 0.0023578683862389765, '265': 0.03460717463795205, '116': 0.0042914133536395595, '256': 0.0045387753761646065, '33': 0.004527189285135794, '24': 0.002756935244677161, '151': 0.005477320187222164, '255': 0.00466371762342002, '148': 0.006912796904560904, '79': 0.01236355772635263, '114': 0.0057505191576755176, '87': 0.005349771135812377, '82': 0.004116094655686329, '196': 0.0017506800059768001, '133': 0.0022752664544536073, '262': 0.006863373786945331, '74': 0.008679920611415348, '127': 0.002783293580241809, '65': 0.0036672394292859797, '177': 0.002141465113533002, '13': 0.0059766390536411616, '257': 0.0019382324845548075, '80': 0.004041069900968551, '45': 0.002654048664953874, '223': 0.0041290187831570895, '159': 0.0026591596627297182, '179': 0.002924663227569609, '244': 0.005782408355290383, '25': 0.004015697642398706, '66': 0.002531340997726116, '131': 0.001409517564818389, '209': 0.0021753261260774003, '1': 0.011189570636289196, '7': 0.007443114178595982, '117': 0.002388967537076599, '217': 0.001708056968226397, '112': 0.004910172809405604, '14': 0.004005070594253169, '95': 0.003801199801880798, '181': 0.00818556317754244, '189': 0.002736479422114918, '224': 0.002734799840982845, '175': 0.001308956241698034, '226': 0.0049723714554350575, '260': 0.0036005624832559993, '202': 0.0011205916565108164, '171': 0.0013202684257810978, '228': 0.003382464731717604, '17': 0.005392523142274003, '49': 0.004708384539503447, '232': 0.0036555512416593596, '64': 0.0012377410902328677, '102': 0.0014992125390887142, '188': 0.004057135088542411, '136': 0.0018222429343124121, '41': 0.007269518728973112, '200': 0.0015325738861992817, '54': 0.0010891173061143063, '28': 0.0016278783808367358, '146': 0.002578012956316793, '37': 0.0046838950430059, '152': 0.0028664914893312965, '70': 0.001545812074587443, '178': 0.001868478293009995, '160': 0.0015439209832453092, '129': 0.005405056133237203, '193': 0.0028920203339165827, '26': 0.003006095706767936, '225': 0.004198327466524397, '97': 0.004724142178935284, '194': 0.0008234329736065019, '40': 0.002590598709286524, '106': 0.0018353571978105639, '220': 0.0021301313891455955, '195': 0.001697642728094971, '61': 0.007373198326036038, '135': 0.001522759395661841, '56': 0.001903603465021065, '254': 0.0021571486334164176, '203': 0.0011680123072490116, '215': 0.0009895163457985948, '52': 0.0017053107259901129, '121': 0.001734279753731056, '168': 0.00413286620887501, '89': 0.004530121377210455, '134': 0.0015465783450817592, '216': 0.0021554101253443616, '18': 0.0027168896009367493, '130': 0.0022630278678314165, '12': 0.000938060027901785, '69': 0.0027429056914451523, '21': 0.0019328656964549338, '248': 0.0018098933142054968, '124': 0.0014453132640685966, '83': 0.0017786438759501352, '71': 0.0019447040340921191, '243': 0.003903876241969501, '22': 0.002403005382085458, '210': 0.0019395559663264758, '36': 0.0031372766032152738, '86': 0.0014234555226094743, '108': 0.001935892259087034, '39': 0.0026511739132130023, '205': 0.0013366200071710092, '247': 0.003614934538041258, '206': 0.0018998864594526347, '92': 0.0031944385890657744, '55': 0.0022666555670085194, '208': 0.0021361321372756013, '76': 0.003081663768222175, '219': 0.0012632318581835365, '153': 0.0008651690981440167, '173': 0.002137849380929811, '250': 0.0016978943112398114, '63': 0.002507153996334206, '93': 0.0015102805217531955, '101': 0.0014648886898658408, '10': 0.0012054030357405692, '122': 0.0011831560569419825, '118': 0.0019010155970426643, '155': 0.0016627587382856681, '197': 0.001979030698688148, '32': 0.0015721042893269814, '157': 0.001572220554867318, '53': 0.0013917605240031813, '242': 0.0024552930815865135, '72': 0.0018197514144895235, '218': 0.0011322006885768512, '67': 0.0013896026118427082, '169': 0.002482235456053511, '252': 0.0016922808602958547, '198': 0.002839870628785536, '62': 0.0022256759488063537, '190': 0.0012275945516787043, '57': 0.0009301100775131265, '213': 0.0028099284632052504, '182': 0.0017603639246979086, '51': 0.002408305025163096, '81': 0.0015840757044071304, '91': 0.002057578233369795, '192': 0.0011634263847489276, '139': 0.0009748144185677992, '259': 0.0015444054180393661, '11': 0.002363663613865136, '47': 0.002026186728185578, '38': 0.0010171130415147834, '123': 0.0023911202766068998, '165': 0.002101784487885547, '227': 0.001829243735478062, '149': 0.0014956044542748389, '185': 0.0018946222207166055, '119': 0.0022962636789426584, '253': 0.0007025079740101376, '128': 0.000831031903913454, '180': 0.0010587209469627738, '126': 0.0019575991427976465, '85': 0.0016767810259737872, '34': 0.0009537039583948294, '191': 0.0016235239896371667, '29': 0.0021552220156143683, '147': 0.0014100706238589326, '16': 0.0017433348372545771, '115': 0.004162976220465431, '258': 0.001647022001661538, '201': 0.002038645292470713, '35': 0.002029425884571461, '19': 0.0016323819287127272, '3': 0.0012996610904207027, '9': 0.0013717250917506829, '212': 0.001810989851304925, '73': 0.0011561957100733357, '58': 0.0008247427469923801, '111': 0.0006867662303176173, '167': 0.002096816390650294, '60': 0.0014671302418222134, '78': 0.0022835732302321915, '183': 0.001115406831289919, '241': 0.002370150792027379, '31': 0.00102065921255507, '222': 0.0008657590796217957, '150': 0.0011806211624974072, '8': 0.000622738611040423, '174': 0.0023809548058570263, '20': 0.0020024146039130455, '251': 0.0036073480401874907, '23': 0.002152171291699192, '172': 0.00137184485025398, '154': 0.000973426401145528, '6': 0.0021538308857089947, '77': 0.0014026046540701043, '120': 0.0007878176642802572, '245': 0.001823790359474836, '109': 0.0028364633877051948, '221': 0.0040410411288972, '94': 0.0014658201438298366, '204': 0.003985995737662595, '214': 0.0015418354020961733, '240': 0.0011708252547095095, '27': 0.00092423125145765, '207': 0.0020023396574341233, '187': 0.0011765194206811694, '2': 0.0006285270508104514, '156': 0.0037520683658669824, '46': 0.0006852249618773363, '176': 0.0010935067931703516, '5': 0.003708424818022463, '44': 0.0017322352039620258, '96': 0.0008949420231881126, '59': 0.0007295557455205556, '84': 0.0021316561506483263, '110': 0.000567866065523238, '30': 0.0007625139494045906, '184': 0.0008098044342421006, '105': 0.0006728331870686867, '99': 0.0009135485192529917, '199': 0.0006076918331551529, '103': 0.0005678592012193443, '104': 0.0005678686167731461}
d2019 =  {'230': 0.017273011533698517, '68': 0.013602811349594264, '238': 0.014485774398570293, '262': 0.008308104507539172, '236': 0.02413577769408758, '132': 0.008491355243271152, '170': 0.018719254014464157, '162': 0.01755021495382774, '107': 0.01279362865595983, '43': 0.0080820739970359, '138': 0.00783788369505811, '50': 0.007285545614103073, '186': 0.014923610620452703, '114': 0.006373362692186718, '158': 0.006112215848785583, '125': 0.0035816556029319912, '79': 0.013685882586623241, '148': 0.007303692237226153, '164': 0.012195194513321662, '90': 0.009148728899975514, '249': 0.009478637825801342, '231': 0.011906365396492428, '24': 0.0033026201362981915, '137': 0.00975775760685611, '166': 0.00800629454641519, '143': 0.008601520289887348, '48': 0.016521893455530335, '87': 0.006428581566534549, '261': 0.004082174366636344, '246': 0.011329041397389897, '52': 0.0018724564600798872, '33': 0.005009160454782695, '163': 0.013404357950484627, '41': 0.009082692362924291, '234': 0.014830966222440066, '144': 0.00590720947995142, '237': 0.022004363507711178, '113': 0.008095656390487786, '239': 0.015742426436454172, '142': 0.016061299918238403, '141': 0.0150183777030871, '140': 0.012981859283613395, '161': 0.021551572439104428, '211': 0.005170730845454401, '74': 0.010824320683286934, '75': 0.012619352181558623, '263': 0.012361318714253411, '224': 0.002960105778657376, '220': 0.0016388346895005652, '88': 0.0037542131115094212, '89': 0.003733148155332004, '10': 0.001626332274161708, '7': 0.006349998036368856, '257': 0.0016429722312551768, '145': 0.00535151837325702, '17': 0.003843862316649132, '209': 0.003337010074081342, '13': 0.006271632393695065, '264': 0.022977647464097053, '100': 0.009503133786199562, '49': 0.004027298469715619, '232': 0.004289609869590431, '66': 0.002481363386063523, '151': 0.007107747368698941, '229': 0.011593190896939297, '233': 0.009599422107645724, '45': 0.003262488066372573, '40': 0.0021456960972323553, '160': 0.0012231086149506085, '4': 0.0035460561550500493, '129': 0.004364810061265166, '216': 0.002424004453851318, '93': 0.0014714808670963039, '195': 0.0017264384590022098, '42': 0.008502122524177041, '181': 0.006501640551913948, '112': 0.0035088590140261357, '71': 0.0018939276770685554, '179': 0.00261661532828565, '218': 0.0014036753986618987, '25': 0.004688841415368473, '189': 0.0021330579862215084, '250': 0.0013791704733159104, '193': 0.0039432728659711605, '255': 0.0034866020920975302, '165': 0.001822001570443712, '260': 0.0028640387342328314, '152': 0.003156294094468307, '198': 0.0019306523654213223, '226': 0.00475533951045639, '95': 0.0031440524027000075, '97': 0.004484248035656174, '65': 0.0038317997257193235, '210': 0.001938274647764228, '244': 0.0060512683330548826, '171': 0.0012226590995276262, '80': 0.003066333978415772, '215': 0.0014732642668814021, '265': 0.011810190252178644, '256': 0.0035516972142148814, '11': 0.0010425140914630847, '217': 0.0016095104035564662, '196': 0.001744066163284856, '130': 0.002352221774815514, '82': 0.0031317254956840543, '225': 0.003474740888366789, '61': 0.005818913937070238, '55': 0.001661537804848259, '23': 0.0018703309197591728, '219': 0.0012577787802528944, '116': 0.004620125327277817, '213': 0.0019112230163754987, '19': 0.0012297224733967699, '167': 0.0015511941743241815, '223': 0.003354902322503594, '188': 0.003429643768591593, '134': 0.001642493106308995, '131': 0.001278127988796729, '28': 0.0016012336432922715, '243': 0.0034452421722383953, '70': 0.0015818069631094666, '9': 0.0011136298692923981, '92': 0.0022296589584349428, '15': 0.0011217187668188405, '168': 0.0033065269168658074, '254': 0.0017813908201793041, '128': 0.0008230888716987695, '14': 0.003137255767563106, '177': 0.001981652481334085, '159': 0.0019874883357915403, '185': 0.0013313526127497809, '202': 0.0011252486622147758, '35': 0.0024302337029764413, '76': 0.003581402140254165, '133': 0.001771604178956868, '39': 0.002424809140877693, '91': 0.0019846752493111143, '36': 0.002158325359113199, '106': 0.0017730452992772384, '12': 0.0009520504307377877, '121': 0.0014369523471782157, '37': 0.0033072649178151623, '51': 0.0019588789284184856, '182': 0.0013507848293275514, '252': 0.0010998833509516877, '258': 0.0014469391031236736, '127': 0.0021856657212760357, '27': 0.0007648089582864559, '191': 0.0015062719192139471, '136': 0.0015241264430596387, '259': 0.001237284052987404, '146': 0.002576659272749604, '21': 0.001474383819970588, '83': 0.001611914221145534, '22': 0.0017165923944816885, '81': 0.0013393677832752927, '169': 0.001681082655195256, '34': 0.0008629945849077386, '62': 0.002070876362190211, '102': 0.0011725007692824287, '228': 0.0024491738510259735, '20': 0.0011454080401654388, '203': 0.001080746097623904, '54': 0.0010349765153143088, '1': 0.006798905938254835, '29': 0.0014230470473944917, '197': 0.0024451442696629046, '205': 0.0018014784509179094, '77': 0.001430919881878355, '149': 0.001433010385497742, '26': 0.0024577527873618876, '178': 0.0010831972307725822, '119': 0.0015261619119145947, '175': 0.0009626777894405422, '98': 0.0010612408928327875, '85': 0.0014828607154332657, '18': 0.001482457390144192, '69': 0.0023144375681726508, '16': 0.0013897756994732348, '180': 0.0010883097981159826, '194': 0.0009563318672856424, '56': 0.0016513727299221083, '124': 0.0011313755650033436, '173': 0.0017940581854747487, '135': 0.0023765461365675205, '207': 0.0019166688508275155, '72': 0.0019947204321700673, '67': 0.001250047666749804, '208': 0.001288542378286863, '32': 0.0012627476279257147, '3': 0.001176242415355158, '101': 0.001074538679583675, '157': 0.0013927672721680334, '174': 0.0016754408102632058, '212': 0.0012702710984877847, '126': 0.0012241021718845074, '73': 0.0008567832282818687, '147': 0.0011654179145118011, '63': 0.0012216665732050738, '227': 0.0015369781594040018, '122': 0.0009438530052567941, '200': 0.0012246293684416761, '241': 0.0014178548827665756, '64': 0.0009557462694027958, '118': 0.0013542148563279919, '242': 0.002173060323914622, '111': 0.0006849729380302241, '155': 0.0016286999608974401, '57': 0.000753921018508912, '247': 0.002077376674451582, '201': 0.0009795025151189871, '109': 0.0013470807697799026, '60': 0.0011785680384249456, '108': 0.0011672587696375954, '176': 0.0007446476569103845, '8': 0.0006296475187774981, '120': 0.0007418152619025345, '139': 0.0010247955489744377, '190': 0.0010789609284844804, '38': 0.0009555672432106429, '53': 0.0009894879972996574, '117': 0.0017896627085602192, '153': 0.0007805773347349759, '94': 0.0010470692152822186, '248': 0.0011731209063978864, '235': 0.0018383217927599284, '96': 0.0007297801643014184, '240': 0.0008180445485038333, '154': 0.0007886822387669387, '192': 0.0010413038911987827, '183': 0.0008981001888400781, '214': 0.0010447003807684866, '123': 0.0017411100291113567, '78': 0.0015311977304729267, '86': 0.0013339138518826804, '253': 0.0006415987266070816, '150': 0.0010854787516604118, '221': 0.0010713811065109946, '47': 0.001471874776125199, '59': 0.000670830348880731, '251': 0.0008811124080846495, '206': 0.0011024221882961916, '31': 0.0008458659028772386, '6': 0.001267435793648606, '46': 0.0006833976950405536, '115': 0.0009975601997101874, '222': 0.0012919101918242284, '58': 0.0006975159043897407, '84': 0.0013189624451127844, '172': 0.0008404900269081647, '156': 0.0009932326667979935, '44': 0.0009039183793893061, '245': 0.0008585457257239317, '187': 0.0007639795627960853, '30': 0.0006433638223565035, '5': 0.0007629109041112159, '99': 0.0006654938176764145, '184': 0.0007617944397631667, '204': 0.0008231539417869632, '105': 0.0005940162844186497, '2': 0.0006814567389477821, '199': 0.0011872964082228253, '110': 0.0005721976779242666}
d2017 = {int(k): v for k,v in d2017.items()}
d2019 = {int(k): v for k,v in d2019.items()}


ranks = []
appreciations = []
location_id = []
for index, row in df.loc[df['year'] == 2019].iterrows():
    if row['location_id'] == 0:
        continue
    neighb = row['neighborhood']
    x = df.loc[(df['neighborhood'] == neighb) & (df['year'] == 2017)]
    if x.empty:
        continue
    x.reset_index()
    price_2017 = x.iloc[0]['median_sale_price']
    price_2019 = row['median_sale_price']
    apprec = price_2017 / price_2019 * 100
    if row['location_id'] not in d2019.keys():
        d2019[row['location_id']] = 0
    if row['location_id'] not in d2019.keys():
        continue
    rank_2017 =  d2017[row['location_id']]
    rank_2019 =  d2019[row['location_id']]
    rank = rank_2019 - rank_2017
    ranks.append(rank)
    appreciations.append(apprec)
    location_id.append(row['location_id'])


print(mean(ranks))
print(mean(appreciations))
print(sorted(ranks, reverse=True)[:10])
print(sorted(ranks)[:10])

df = pd.DataFrame(list(zip(ranks, appreciations)),
               columns =['rank', 'appreciation'])
#remove outliners
df = df.loc[df['appreciation'] > 60]
df = df.loc[(df['rank'] > 0.0005) ^ (df['rank'] < -0.0005)]

df.plot.scatter(x="rank", y="appreciation")
plt.show()
sns.set_style('whitegrid')
sns.lmplot(x ='rank', y ='appreciation', data = df, fit_reg=True)