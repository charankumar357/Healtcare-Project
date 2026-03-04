#!/usr/bin/env python3
"""
Generator script for Symptom Knowledge Graph (Task M3-01)
Rural Health Pre-Screening System - India
Generates symptom_knowledge_graph.json
"""
import json, os

def build_symptom(base_weight, body_system, is_red_flag, red_flag_combos, common_names,
                  sev=None, dur=None):
    sev = sev or {"mild": 0.5, "moderate": 1.0, "severe": 1.8}
    dur = dur or {"acute": 1.0, "subacute": 1.2, "chronic": 1.6}
    return {
        "base_weight": base_weight,
        "body_system": body_system,
        "is_red_flag": is_red_flag,
        "red_flag_combinations": red_flag_combos,
        "common_names": common_names,
        "severity_multipliers": sev,
        "duration_multipliers": dur
    }

symptoms = {}

# ============ RESPIRATORY (12 symptoms) ============
symptoms["cough"] = build_symptom(5, "respiratory", False,
    ["cough+blood_in_sputum", "cough+weight_loss+night_sweats"],
    {"hi": ["khansi", "khasi"], "te": ["daggu", "dabbhu"], "ta": ["irumal"], "en": ["cough", "coughing"]})

symptoms["shortness_of_breath"] = build_symptom(14, "respiratory", True,
    ["shortness_of_breath+chest_pain", "shortness_of_breath+fever"],
    {"hi": ["saans phoolna", "saans lene mein takleef"], "te": ["uppiri", "swasa istam"], "ta": ["moochu vaangu", "moochu thinaural"], "en": ["shortness of breath", "breathlessness", "dyspnea"]})

symptoms["wheezing"] = build_symptom(8, "respiratory", False,
    ["wheezing+shortness_of_breath"],
    {"hi": ["seeti ki awaaz", "ghargharahat"], "te": ["relakattu", "seeti"], "ta": ["moochu seelal"], "en": ["wheezing", "whistling breath"]})

symptoms["blood_in_sputum"] = build_symptom(16, "respiratory", True,
    ["blood_in_sputum+weight_loss", "blood_in_sputum+cough"],
    {"hi": ["khoon wali balgam", "balgam mein khoon"], "te": ["rakthpu thummu", "netturu kapha"], "ta": ["ratham kalappu irumal"], "en": ["blood in sputum", "hemoptysis", "coughing blood"]})

symptoms["sore_throat"] = build_symptom(4, "respiratory", False, [],
    {"hi": ["gala dard", "gale mein kharash"], "te": ["gonthu noppi", "gonthu manta"], "ta": ["thondai vali"], "en": ["sore throat", "throat pain"]})

symptoms["nasal_congestion"] = build_symptom(3, "respiratory", False, [],
    {"hi": ["naak band", "naak jam"], "te": ["mukku banda", "jalabu"], "ta": ["mookku adaipu"], "en": ["nasal congestion", "stuffy nose", "blocked nose"]})

symptoms["runny_nose"] = build_symptom(2, "respiratory", False, [],
    {"hi": ["naak bahna", "naak se paani"], "te": ["mukku kaaru", "jalabu"], "ta": ["mookku ozhukal"], "en": ["runny nose", "rhinorrhea"]})

symptoms["chest_tightness"] = build_symptom(10, "respiratory", False,
    ["chest_tightness+shortness_of_breath"],
    {"hi": ["seene mein jakdan", "chhati mein bharipan"], "te": ["chhati lo baram", "gundee baram"], "ta": ["maarbil irukkam"], "en": ["chest tightness", "tight chest"]})

symptoms["rapid_breathing"] = build_symptom(12, "respiratory", True,
    ["rapid_breathing+fever", "rapid_breathing+chest_pain"],
    {"hi": ["tez saans", "jaldi jaldi saans"], "te": ["vegamga swasa", "egirey swasa"], "ta": ["vegamaana moochu"], "en": ["rapid breathing", "tachypnea"]})

symptoms["difficulty_swallowing"] = build_symptom(7, "respiratory", False,
    ["difficulty_swallowing+fever+sore_throat"],
    {"hi": ["nigalne mein takleef", "khaana nigalna mushkil"], "te": ["mingu ivvadam kashtam"], "ta": ["vizhunguvathu kashtam"], "en": ["difficulty swallowing", "dysphagia"]})

symptoms["snoring"] = build_symptom(3, "respiratory", False, [],
    {"hi": ["kharrate", "kharrate lena"], "te": ["gorka", "gorke petatam"], "ta": ["kuraattai"], "en": ["snoring", "loud snoring"]})

symptoms["stridor"] = build_symptom(15, "respiratory", True,
    ["stridor+fever", "stridor+shortness_of_breath"],
    {"hi": ["saans mein awaaz", "saans ki seeti"], "te": ["swasa lo seeti", "seeti swasa"], "ta": ["moochu osai"], "en": ["stridor", "noisy breathing"]})

# ============ SYSTEMIC (12 symptoms) ============
symptoms["fever"] = build_symptom(8, "systemic", False,
    ["fever+shortness_of_breath", "fever+stiff_neck", "fever+rash"],
    {"hi": ["bukhar", "tap", "jwar"], "te": ["jwaram", "veyyi", "jvaram"], "ta": ["kaaichal", "suuram"], "en": ["fever", "high temperature", "pyrexia"]})

symptoms["fatigue"] = build_symptom(4, "systemic", False,
    ["fatigue+weight_loss+night_sweats"],
    {"hi": ["thakan", "kamzori"], "te": ["alasata", "badhakam"], "ta": ["soarvu", "kalappu"], "en": ["fatigue", "tiredness", "exhaustion"]})

symptoms["weight_loss"] = build_symptom(9, "systemic", False,
    ["weight_loss+night_sweats", "weight_loss+blood_in_sputum"],
    {"hi": ["vajan kam hona", "vajan girna"], "te": ["baruvu taggadam"], "ta": ["edai kuraital"], "en": ["weight loss", "losing weight", "unintentional weight loss"]})

symptoms["night_sweats"] = build_symptom(7, "systemic", False,
    ["night_sweats+weight_loss+cough"],
    {"hi": ["raat ko paseena", "raat mein paseena"], "te": ["raathri chema", "raatri chema pattu"], "ta": ["iravu viyarvai"], "en": ["night sweats", "sweating at night"]})

symptoms["chills"] = build_symptom(6, "systemic", False,
    ["chills+fever+joint_pain"],
    {"hi": ["thand lagna", "kamp", "jhurjhuri"], "te": ["chali", "vankara"], "ta": ["kulir", "nadukkal"], "en": ["chills", "shivering", "rigors"]})

symptoms["loss_of_appetite"] = build_symptom(4, "systemic", False, [],
    {"hi": ["bhookh na lagna", "bhookh kam hona"], "te": ["aakali ledu", "aakali taggadam"], "ta": ["pasi illaamai"], "en": ["loss of appetite", "no appetite", "anorexia"]})

symptoms["dehydration"] = build_symptom(10, "systemic", False,
    ["dehydration+diarrhea+vomiting"],
    {"hi": ["paani ki kami", "sharer mein paani kam"], "te": ["neellu taggadam", "neerasam"], "ta": ["neer izhappu"], "en": ["dehydration", "fluid loss", "dry mouth"]})

symptoms["swollen_lymph_nodes"] = build_symptom(7, "systemic", False,
    ["swollen_lymph_nodes+fever+weight_loss"],
    {"hi": ["giltiyan", "gaath soojana"], "te": ["gandalu vaapu", "gandalu puduthayi"], "ta": ["naeer kazhalaigal veekkam"], "en": ["swollen lymph nodes", "swollen glands"]})

symptoms["generalized_weakness"] = build_symptom(5, "systemic", False, [],
    {"hi": ["kamzori", "shareer mein takat nahin"], "te": ["balaveenam", "shareer balaheenata"], "ta": ["udal balaveenam"], "en": ["weakness", "body weakness", "general weakness"]})

symptoms["body_aches"] = build_symptom(5, "systemic", False,
    ["body_aches+fever+headache"],
    {"hi": ["badan dard", "shareer mein dard"], "te": ["votilu noppu", "shareer lo noppi"], "ta": ["udal vali"], "en": ["body aches", "body pain", "myalgia"]})

symptoms["loss_of_consciousness"] = build_symptom(20, "systemic", True,
    ["loss_of_consciousness+fever", "loss_of_consciousness+head_injury"],
    {"hi": ["behosh hona", "hosh na rehna"], "te": ["spruha lekunda", "maigam kolapovadam"], "ta": ["mayakkam", "ninaivizhattal"], "en": ["loss of consciousness", "fainting", "passing out", "unresponsive"]})

symptoms["excessive_thirst"] = build_symptom(5, "systemic", False,
    ["excessive_thirst+frequent_urination"],
    {"hi": ["bahut pyaas lagna", "zyaada pyaas"], "te": ["ekkuva daham", "daham ekkuva avuta"], "ta": ["athiga thaagam"], "en": ["excessive thirst", "polydipsia", "very thirsty"]})

# ============ GASTROINTESTINAL (12 symptoms) ============
symptoms["abdominal_pain"] = build_symptom(8, "gastrointestinal", False,
    ["abdominal_pain+vomiting+fever", "abdominal_pain+blood_in_stool"],
    {"hi": ["pet dard", "pet mein dard"], "te": ["kadupu noppi", "potta noppi"], "ta": ["vayiru vali"], "en": ["abdominal pain", "stomach ache", "tummy pain"]})

symptoms["diarrhea"] = build_symptom(7, "gastrointestinal", False,
    ["diarrhea+vomiting+dehydration", "diarrhea+blood_in_stool"],
    {"hi": ["dast", "loose motion", "pet kharab"], "te": ["virechanalu", "loose motions"], "ta": ["vayiru pokku", "kazhichal"], "en": ["diarrhea", "loose motions", "watery stools"]})

symptoms["vomiting"] = build_symptom(7, "gastrointestinal", False,
    ["vomiting+severe_headache", "vomiting+abdominal_pain+fever"],
    {"hi": ["ulti", "ulti hona", "qay"], "te": ["vantulu", "vakallu"], "ta": ["vaanthi"], "en": ["vomiting", "throwing up", "emesis"]})

symptoms["nausea"] = build_symptom(4, "gastrointestinal", False, [],
    {"hi": ["ji machlana", "ulti jaisa lagna"], "te": ["vakaluga anipinchatam"], "ta": ["kumattal"], "en": ["nausea", "feeling sick", "queasy"]})

symptoms["constipation"] = build_symptom(4, "gastrointestinal", False, [],
    {"hi": ["kabz", "qabz", "pet saaf na hona"], "te": ["malabadhakam", "motion raadu"], "ta": ["malaccikkal"], "en": ["constipation", "hard stools"]})

symptoms["blood_in_stool"] = build_symptom(15, "gastrointestinal", True,
    ["blood_in_stool+abdominal_pain", "blood_in_stool+weight_loss"],
    {"hi": ["khoon wali potty", "latrine mein khoon"], "te": ["motion lo rakthamu", "netturu motion"], "ta": ["ratham kalappu malam"], "en": ["blood in stool", "bloody stool", "rectal bleeding"]})

symptoms["bloating"] = build_symptom(3, "gastrointestinal", False, [],
    {"hi": ["pet phoolna", "gas banna"], "te": ["uddaram", "kadupu vubbaram"], "ta": ["vayiru oombal"], "en": ["bloating", "gas", "distension"]})

symptoms["heartburn"] = build_symptom(4, "gastrointestinal", False, [],
    {"hi": ["seene mein jalan", "khatti dakar"], "te": ["gunde manta", "pulupu teenapulu"], "ta": ["nenjerichal"], "en": ["heartburn", "acid reflux", "acidity"]})

symptoms["jaundice"] = build_symptom(13, "gastrointestinal", True,
    ["jaundice+fever", "jaundice+abdominal_pain"],
    {"hi": ["peeliya", "piliya"], "te": ["kamalamu", "pasupu kamalamu"], "ta": ["mancal kaamalai"], "en": ["jaundice", "yellow eyes", "yellow skin"]})

symptoms["difficulty_eating"] = build_symptom(6, "gastrointestinal", False, [],
    {"hi": ["khaana na kha paana", "khaane mein dikkat"], "te": ["thinalekapovadam"], "ta": ["unavu unavillamai"], "en": ["difficulty eating", "cannot eat", "food refusal"]})

symptoms["rectal_pain"] = build_symptom(5, "gastrointestinal", False, [],
    {"hi": ["malaashay mein dard", "pichhe dard"], "te": ["maladdari noppi"], "ta": ["malavay vali"], "en": ["rectal pain", "pain during bowel movement"]})

symptoms["black_tarry_stools"] = build_symptom(16, "gastrointestinal", True,
    ["black_tarry_stools+abdominal_pain", "black_tarry_stools+vomiting"],
    {"hi": ["kaali potty", "tar jaisi potty"], "te": ["nalla motion", "tar lanti motion"], "ta": ["karuppu malam"], "en": ["black tarry stools", "melena", "dark stools"]})

# ============ CARDIOVASCULAR (10 symptoms) ============
symptoms["chest_pain"] = build_symptom(16, "cardiovascular", True,
    ["chest_pain+shortness_of_breath", "chest_pain+sweating", "chest_pain+left_arm_pain"],
    {"hi": ["seene mein dard", "chhati mein dard"], "te": ["chhati noppi", "gunde noppi"], "ta": ["nenju vali", "maarbhu vali"], "en": ["chest pain", "heart pain", "angina"]})

symptoms["palpitations"] = build_symptom(8, "cardiovascular", False,
    ["palpitations+shortness_of_breath", "palpitations+chest_pain"],
    {"hi": ["dil ki dhadkan tez", "dhadkan badhna"], "te": ["gunde vega veega kottadam"], "ta": ["padapadappu", "idhaya thudippu"], "en": ["palpitations", "heart racing", "fast heartbeat"]})

symptoms["swelling_in_legs"] = build_symptom(9, "cardiovascular", False,
    ["swelling_in_legs+shortness_of_breath"],
    {"hi": ["pair mein sujan", "pair soojana"], "te": ["kallu vaapu", "kallu ubbaram"], "ta": ["kaal veekkam"], "en": ["swelling in legs", "leg edema", "swollen feet"]})

symptoms["dizziness"] = build_symptom(6, "cardiovascular", False,
    ["dizziness+chest_pain", "dizziness+loss_of_consciousness"],
    {"hi": ["chakkar aana", "sir ghoomna"], "te": ["tala tiragadam", "tala tiruguddi"], "ta": ["thalai suttral"], "en": ["dizziness", "lightheadedness", "feeling faint"]})

symptoms["high_blood_pressure_symptoms"] = build_symptom(10, "cardiovascular", False,
    ["high_blood_pressure_symptoms+headache+vision_changes"],
    {"hi": ["BP badha hua", "ucch raktchap"], "te": ["BP ekkuva", "rakta pottudu ekkuva"], "ta": ["uyar rattha azhuththam"], "en": ["high BP symptoms", "hypertension symptoms"]})

symptoms["left_arm_pain"] = build_symptom(14, "cardiovascular", True,
    ["left_arm_pain+chest_pain", "left_arm_pain+sweating"],
    {"hi": ["bayen haath mein dard", "bayen baazu mein dard"], "te": ["edama cheiyi noppi"], "ta": ["idathu kai vali"], "en": ["left arm pain", "pain in left arm"]})

symptoms["irregular_heartbeat"] = build_symptom(10, "cardiovascular", False,
    ["irregular_heartbeat+shortness_of_breath", "irregular_heartbeat+dizziness"],
    {"hi": ["dhadkan aniyamit", "dil ki dhadkan gadbad"], "te": ["gunde asaadhaarana kottadam"], "ta": ["othungaatra idhaya thudippu"], "en": ["irregular heartbeat", "arrhythmia"]})

symptoms["cold_extremities"] = build_symptom(5, "cardiovascular", False, [],
    {"hi": ["haath pair thande", "haath pair thand"], "te": ["cheetulu kallu challa"], "ta": ["kulir kaigal kaalkal"], "en": ["cold hands and feet", "cold extremities"]})

symptoms["cyanosis"] = build_symptom(17, "cardiovascular", True,
    ["cyanosis+shortness_of_breath"],
    {"hi": ["hoth neele padna", "neela rang"], "te": ["pedavulu neelam", "pedhavulu neelam avadam"], "ta": ["neela niram udal"], "en": ["blue lips", "cyanosis", "bluish skin"]})

symptoms["fainting"] = build_symptom(12, "cardiovascular", True,
    ["fainting+chest_pain", "fainting+seizure"],
    {"hi": ["behosh hona", "gir padna"], "te": ["maigam povadam", "maigam kolupovadam"], "ta": ["mayakkam adaithal"], "en": ["fainting", "syncope", "blacking out"]})

# ============ NEUROLOGICAL (11 symptoms) ============
symptoms["headache"] = build_symptom(5, "neurological", False,
    ["headache+fever+stiff_neck", "headache+vomiting+vision_changes"],
    {"hi": ["sir dard", "sar dard"], "te": ["tala noppi", "talakai noppi"], "ta": ["thalai vali"], "en": ["headache", "head pain"]})

symptoms["seizure"] = build_symptom(18, "neurological", True,
    ["seizure+fever", "seizure+loss_of_consciousness"],
    {"hi": ["mirgi", "daurey padna", "jhatkay"], "te": ["fits", "moorccha"], "ta": ["valippu"], "en": ["seizure", "convulsion", "fits", "epileptic attack"]})

symptoms["stiff_neck"] = build_symptom(13, "neurological", True,
    ["stiff_neck+fever+headache"],
    {"hi": ["gardan akad jaana", "gardan mein dard"], "te": ["meda biddhanam", "meda gattibadatam"], "ta": ["kazhuththu virappu"], "en": ["stiff neck", "neck stiffness", "neck rigidity"]})

symptoms["numbness"] = build_symptom(8, "neurological", False,
    ["numbness+weakness+facial_drooping"],
    {"hi": ["sunn padna", "jhunjhunahat"], "te": ["janum lekundam", "moratadam"], "ta": ["maratthuppu"], "en": ["numbness", "tingling", "pins and needles"]})

symptoms["sudden_paralysis"] = build_symptom(20, "neurological", True,
    ["sudden_paralysis+facial_drooping", "sudden_paralysis+slurred_speech"],
    {"hi": ["achanak lakwa", "paralysis ho jaana"], "te": ["hathaattu paksha vaatam"], "ta": ["thirukku vaatham"], "en": ["sudden paralysis", "cannot move limbs", "stroke symptoms"]})

symptoms["facial_drooping"] = build_symptom(19, "neurological", True,
    ["facial_drooping+slurred_speech", "facial_drooping+sudden_paralysis"],
    {"hi": ["chehra latakna", "mooh tedha hona"], "te": ["mukhamu vaalipotundi"], "ta": ["mugam saaivu"], "en": ["facial drooping", "face drooping", "droopy face"]})

symptoms["slurred_speech"] = build_symptom(18, "neurological", True,
    ["slurred_speech+facial_drooping", "slurred_speech+sudden_paralysis"],
    {"hi": ["bolne mein dikkat", "zuban ladkhadana"], "te": ["matalu kalipi chepadam", "matalu raavu"], "ta": ["thudumaaral peechchu"], "en": ["slurred speech", "difficulty speaking", "speech problems"]})

symptoms["confusion"] = build_symptom(12, "neurological", False,
    ["confusion+fever", "confusion+headache"],
    {"hi": ["gehraaan", "samajh na aana", "confuse hona"], "te": ["gadabida", "artham kaadu"], "ta": ["kuzhappam", "manam azhiyum"], "en": ["confusion", "disorientation", "altered mental state"]})

symptoms["memory_loss"] = build_symptom(7, "neurological", False, [],
    {"hi": ["yaaddasht kamzor", "bhool jaana"], "te": ["gnaapakasakti taggadam"], "ta": ["niyaabakam kuraital"], "en": ["memory loss", "forgetfulness"]})

symptoms["tremors"] = build_symptom(6, "neurological", False, [],
    {"hi": ["kaampna", "haath kaampna"], "te": ["vadakadam", "cheyyi vadakadam"], "ta": ["nadhukkam"], "en": ["tremors", "shaking", "trembling"]})

symptoms["vertigo"] = build_symptom(7, "neurological", False,
    ["vertigo+vomiting+hearing_loss"],
    {"hi": ["chakkar aana", "duniya ghoomti hui"], "te": ["tala tiragadam", "bhramanamu"], "ta": ["thalai suttral"], "en": ["vertigo", "spinning sensation", "room spinning"]})

# ============ MUSCULOSKELETAL (10 symptoms) ============
symptoms["joint_pain"] = build_symptom(6, "musculoskeletal", False,
    ["joint_pain+fever+rash"],
    {"hi": ["jodon mein dard", "gathiya"], "te": ["keelulanoppi"], "ta": ["moottu vali"], "en": ["joint pain", "arthralgia", "joint ache"]})

symptoms["back_pain"] = build_symptom(5, "musculoskeletal", False,
    ["back_pain+numbness+leg_weakness"],
    {"hi": ["kamar dard", "peeth dard"], "te": ["nadumu noppi", "veepu noppi"], "ta": ["muthuhu vali"], "en": ["back pain", "backache", "lower back pain"]})

symptoms["muscle_cramps"] = build_symptom(4, "musculoskeletal", False, [],
    {"hi": ["ainthan", "maaspeshi mein dard"], "te": ["kallu nookuludam", "kandallu"], "ta": ["thachai pidippu"], "en": ["muscle cramps", "cramps", "spasms"]})

symptoms["swollen_joints"] = build_symptom(8, "musculoskeletal", False,
    ["swollen_joints+fever"],
    {"hi": ["jod soojana", "jod mein sujan"], "te": ["keellu vaakadam", "keellu vaapu"], "ta": ["moottu veekkam"], "en": ["swollen joints", "joint swelling"]})

symptoms["bone_pain"] = build_symptom(8, "musculoskeletal", False,
    ["bone_pain+fever+weight_loss"],
    {"hi": ["haddi mein dard", "haddi dard"], "te": ["yemuka noppi"], "ta": ["elumbu vali"], "en": ["bone pain", "deep bone ache"]})

symptoms["limited_mobility"] = build_symptom(6, "musculoskeletal", False, [],
    {"hi": ["hilne dhulne mein dikkat", "chal nahin paate"], "te": ["kadalika kashdam"], "ta": ["iyakkam kuraivu"], "en": ["limited mobility", "difficulty moving", "stiffness"]})

symptoms["leg_weakness"] = build_symptom(9, "musculoskeletal", False,
    ["leg_weakness+numbness+back_pain"],
    {"hi": ["pair mein kamzori", "pair mein takat nahi"], "te": ["kallu balaheenata"], "ta": ["kaal balaveenam"], "en": ["leg weakness", "weak legs", "legs giving way"]})

symptoms["neck_pain"] = build_symptom(5, "musculoskeletal", False, [],
    {"hi": ["gardan mein dard"], "te": ["meda noppi"], "ta": ["kazhuththu vali"], "en": ["neck pain", "cervical pain"]})

symptoms["hip_pain"] = build_symptom(5, "musculoskeletal", False, [],
    {"hi": ["kulhe mein dard", "koolhe ka dard"], "te": ["totu noppi"], "ta": ["idupu vali"], "en": ["hip pain"]})

symptoms["fracture_suspected"] = build_symptom(14, "musculoskeletal", True,
    ["fracture_suspected+swelling"],
    {"hi": ["haddi tootna", "fracture hona"], "te": ["yemuka bhangadam", "yemuka virigindi"], "ta": ["elumbu murivu"], "en": ["suspected fracture", "broken bone", "fracture"]})

# ============ DERMATOLOGICAL (10 symptoms) ============
symptoms["rash"] = build_symptom(5, "dermatological", False,
    ["rash+fever", "rash+joint_pain"],
    {"hi": ["daane", "khujli wale daane"], "te": ["doddalu", "charma vikaram"], "ta": ["thol azhichchi", "thol porukkal"], "en": ["rash", "skin rash", "eruption"]})

symptoms["itching"] = build_symptom(3, "dermatological", False, [],
    {"hi": ["khujli", "kharish"], "te": ["durada", "gadda"], "ta": ["arippu"], "en": ["itching", "pruritus", "itchy skin"]})

symptoms["wound_not_healing"] = build_symptom(8, "dermatological", False,
    ["wound_not_healing+fever"],
    {"hi": ["ghav theek na hona", "zaakhm na bharna"], "te": ["ghaayam manadamu"], "ta": ["pun aaramai"], "en": ["wound not healing", "non-healing wound", "chronic wound"]})

symptoms["skin_discoloration"] = build_symptom(5, "dermatological", False, [],
    {"hi": ["chamdi ka rang badalna", "daag"], "te": ["charma varna maarpulu"], "ta": ["thol niram maatram"], "en": ["skin discoloration", "skin patches", "pigmentation"]})

symptoms["boils_abscess"] = build_symptom(7, "dermatological", False,
    ["boils_abscess+fever"],
    {"hi": ["phoda", "phunsi"], "te": ["guddalu", "puggulu"], "ta": ["katti", "kozhuppu katti"], "en": ["boils", "abscess", "skin abscess"]})

symptoms["burns"] = build_symptom(12, "dermatological", True,
    ["burns+fever", "burns+wound_not_healing"],
    {"hi": ["jalna", "jalane ka nishaan"], "te": ["kaalu", "kaallindi"], "ta": ["theekkaayam", "veppukkaayam"], "en": ["burns", "burn injury", "scalding"]})

symptoms["swelling"] = build_symptom(5, "dermatological", False,
    ["swelling+redness+fever"],
    {"hi": ["sujan", "soojana"], "te": ["vaapu"], "ta": ["veekkam"], "en": ["swelling", "edema", "puffiness"]})

symptoms["hair_loss"] = build_symptom(2, "dermatological", False, [],
    {"hi": ["baal jharna", "baal tootna"], "te": ["juuttu raalatam"], "ta": ["mudi kodal"], "en": ["hair loss", "alopecia", "balding"]})

symptoms["skin_ulcers"] = build_symptom(9, "dermatological", False,
    ["skin_ulcers+fever+wound_not_healing"],
    {"hi": ["chamdi ka nasoor", "ghav"], "te": ["charma puttlu"], "ta": ["thol pun"], "en": ["skin ulcers", "open sores"]})

symptoms["excessive_sweating"] = build_symptom(3, "dermatological", False, [],
    {"hi": ["bahut paseena aana", "zyada paseena"], "te": ["ekkuva chema padam"], "ta": ["athiga viyarvai"], "en": ["excessive sweating", "hyperhidrosis"]})

# ============ REPRODUCTIVE (10 symptoms) ============
symptoms["vaginal_bleeding"] = build_symptom(14, "reproductive", True,
    ["vaginal_bleeding+abdominal_pain", "vaginal_bleeding+pregnancy"],
    {"hi": ["yoni se khoon", "bleeding hona"], "te": ["yonu nundi rakthamu"], "ta": ["pirappu uruppu rathapokupu"], "en": ["vaginal bleeding", "abnormal bleeding"]})

symptoms["missed_period"] = build_symptom(5, "reproductive", False,
    ["missed_period+abdominal_pain"],
    {"hi": ["mahwari na aana", "periods na aana"], "te": ["netthuru raaledu", "periods raaledu"], "ta": ["maathavitai thavariythu"], "en": ["missed period", "amenorrhea", "late period"]})

symptoms["pelvic_pain"] = build_symptom(8, "reproductive", False,
    ["pelvic_pain+fever", "pelvic_pain+vaginal_bleeding"],
    {"hi": ["pet ke neeche dard", "kokh mein dard"], "te": ["moddu noppi", "kalodu noppi"], "ta": ["idipu vali"], "en": ["pelvic pain", "lower abdominal pain"]})

symptoms["painful_urination"] = build_symptom(7, "reproductive", False,
    ["painful_urination+fever+back_pain"],
    {"hi": ["peshab mein jalan", "peshab mein dard"], "te": ["moothram lo manta"], "ta": ["siruneer erichal"], "en": ["painful urination", "burning urination", "dysuria"]})

symptoms["frequent_urination"] = build_symptom(5, "reproductive", False,
    ["frequent_urination+excessive_thirst"],
    {"hi": ["baar baar peshab aana"], "te": ["marumaaru moothram raavadam"], "ta": ["adikaadi siruneer"], "en": ["frequent urination", "polyuria"]})

symptoms["breast_lump"] = build_symptom(11, "reproductive", True,
    ["breast_lump+skin_discoloration"],
    {"hi": ["sthan mein gilti", "chhati mein gaanth"], "te": ["rolu lo gaddalu"], "ta": ["maarbu katti"], "en": ["breast lump", "lump in breast"]})

symptoms["pregnancy_complications"] = build_symptom(15, "reproductive", True,
    ["pregnancy_complications+vaginal_bleeding", "pregnancy_complications+high_blood_pressure_symptoms"],
    {"hi": ["garbhavastha mein dikkat", "pregnancy problem"], "te": ["garbham lo samasyalu"], "ta": ["karpakaala pinaivu"], "en": ["pregnancy complications", "pregnancy problem"]})

symptoms["penile_discharge"] = build_symptom(8, "reproductive", False,
    ["penile_discharge+painful_urination"],
    {"hi": ["ling se paani aana", "ling se discharge"], "te": ["lingamu nundi sravamu"], "ta": ["aaan uruppu ozhukal"], "en": ["penile discharge", "urethral discharge"]})

symptoms["testicular_pain"] = build_symptom(10, "reproductive", False,
    ["testicular_pain+swelling+fever"],
    {"hi": ["andkosh mein dard"], "te": ["vrushanu noppi"], "ta": ["vidhaipal vali"], "en": ["testicular pain", "pain in testicles"]})

symptoms["menstrual_cramps_severe"] = build_symptom(6, "reproductive", False, [],
    {"hi": ["mahwari mein bahut dard", "periods mein dard"], "te": ["netthuru samayam lo noppi"], "ta": ["maathavitai vali"], "en": ["severe menstrual cramps", "dysmenorrhea", "period pain"]})

# ============ OPHTHALMOLOGICAL (8 symptoms) ============
symptoms["eye_pain"] = build_symptom(7, "ophthalmological", False,
    ["eye_pain+vision_changes+headache"],
    {"hi": ["aankh mein dard"], "te": ["kannu noppi"], "ta": ["kan vali"], "en": ["eye pain", "pain in eye"]})

symptoms["vision_changes"] = build_symptom(10, "ophthalmological", True,
    ["vision_changes+headache", "vision_changes+eye_pain"],
    {"hi": ["nazar kamzor hona", "dhundhla dikhna"], "te": ["choopu maardindi", "kannu andham"], "ta": ["paarvai maatram"], "en": ["vision changes", "blurred vision", "vision loss"]})

symptoms["eye_redness"] = build_symptom(4, "ophthalmological", False,
    ["eye_redness+eye_pain+fever"],
    {"hi": ["aankh laal hona"], "te": ["kannu errabadatam"], "ta": ["kan sivappu"], "en": ["red eye", "eye redness", "conjunctivitis"]})

symptoms["eye_discharge"] = build_symptom(4, "ophthalmological", False, [],
    {"hi": ["aankh se paani aana", "keechad"], "te": ["kannu nundi neeru"], "ta": ["kan ozhukal"], "en": ["eye discharge", "watery eyes", "eye pus"]})

symptoms["sudden_vision_loss"] = build_symptom(19, "ophthalmological", True,
    ["sudden_vision_loss+headache", "sudden_vision_loss+eye_pain"],
    {"hi": ["achanak dikhna band hona", "aankh ki roshni jaana"], "te": ["hathaattu chopu povadam"], "ta": ["thirukku paarvai izhappu"], "en": ["sudden vision loss", "sudden blindness"]})

symptoms["itchy_eyes"] = build_symptom(2, "ophthalmological", False, [],
    {"hi": ["aankhon mein khujli"], "te": ["kannu lo durada"], "ta": ["kan arippu"], "en": ["itchy eyes", "eye itching"]})

symptoms["double_vision"] = build_symptom(10, "ophthalmological", False,
    ["double_vision+headache+vomiting"],
    {"hi": ["do do dikhna"], "te": ["rendu rendu chopu"], "ta": ["irattu paarvai"], "en": ["double vision", "diplopia", "seeing double"]})

symptoms["sensitivity_to_light"] = build_symptom(5, "ophthalmological", False,
    ["sensitivity_to_light+headache+stiff_neck"],
    {"hi": ["roshni se takleef", "dhoop mein dikkat"], "te": ["veligilo baadhaa"], "ta": ["olippadam"], "en": ["light sensitivity", "photophobia"]})

# ============ ENT (10 symptoms) ============
symptoms["ear_pain"] = build_symptom(5, "ent", False,
    ["ear_pain+fever+ear_discharge"],
    {"hi": ["kaan mein dard", "kaan dard"], "te": ["chevi noppi"], "ta": ["kaathu vali"], "en": ["ear pain", "earache", "otalgia"]})

symptoms["hearing_loss"] = build_symptom(8, "ent", False,
    ["hearing_loss+ear_pain", "hearing_loss+vertigo"],
    {"hi": ["sunai na dena", "kaan se kam sunna"], "te": ["vinabadu taggadam"], "ta": ["kaathu kelamai"], "en": ["hearing loss", "deafness", "hard of hearing"]})

symptoms["ear_discharge"] = build_symptom(7, "ent", False,
    ["ear_discharge+fever"],
    {"hi": ["kaan se paani aana", "kaan bahna"], "te": ["chevi nundi neeru"], "ta": ["kaathu ozhukal"], "en": ["ear discharge", "fluid from ear"]})

symptoms["tinnitus"] = build_symptom(4, "ent", False, [],
    {"hi": ["kaan mein awaaz", "kaan baj rahe hain"], "te": ["chevi lo gundrandam"], "ta": ["kaathu oosai"], "en": ["ringing in ears", "tinnitus"]})

symptoms["nosebleed"] = build_symptom(7, "ent", False,
    ["nosebleed+headache", "nosebleed+high_blood_pressure_symptoms"],
    {"hi": ["naak se khoon", "nakseer"], "te": ["mukku nundi rakthamu"], "ta": ["mookku rathapokupu"], "en": ["nosebleed", "epistaxis", "nose bleeding"]})

symptoms["sinus_pain"] = build_symptom(5, "ent", False,
    ["sinus_pain+fever+nasal_congestion"],
    {"hi": ["sinus dard", "naak ke upar dard"], "te": ["sinus noppi"], "ta": ["mookku kuthi vali"], "en": ["sinus pain", "sinusitis", "facial pressure"]})

symptoms["hoarseness"] = build_symptom(4, "ent", False, [],
    {"hi": ["awaaz baith jaana", "gala baithna"], "te": ["gonthu maaripovadam"], "ta": ["kural maatram"], "en": ["hoarseness", "raspy voice", "voice change"]})

symptoms["mouth_ulcers"] = build_symptom(3, "ent", False, [],
    {"hi": ["muh mein chhale", "chhale"], "te": ["nootti puttlu"], "ta": ["vaai pun"], "en": ["mouth ulcers", "canker sores", "mouth sores"]})

symptoms["toothache"] = build_symptom(5, "ent", False, [],
    {"hi": ["daant mein dard", "daant dard"], "te": ["pantu noppi"], "ta": ["pal vali"], "en": ["toothache", "dental pain", "tooth pain"]})

symptoms["swollen_face"] = build_symptom(8, "ent", False,
    ["swollen_face+fever+toothache"],
    {"hi": ["chehra soojana", "mooh soojana"], "te": ["mukhamu vaapu"], "ta": ["mugam veekkam"], "en": ["swollen face", "facial swelling"]})

# ============ RED FLAG COMBINATIONS ============
red_flag_combinations = [
    {"symptoms": ["chest_pain", "shortness_of_breath"], "override_score": 90,
     "reason": "Possible acute coronary syndrome or pulmonary embolism"},
    {"symptoms": ["chest_pain", "left_arm_pain", "sweating"], "override_score": 95,
     "reason": "Classic presentation of myocardial infarction (heart attack)"},
    {"symptoms": ["sudden_paralysis", "facial_drooping", "slurred_speech"], "override_score": 95,
     "reason": "Strong indicators of acute stroke — FAST protocol activation required"},
    {"symptoms": ["fever", "stiff_neck", "headache"], "override_score": 90,
     "reason": "Possible meningitis — requires immediate lumbar puncture and antibiotics"},
    {"symptoms": ["loss_of_consciousness", "seizure"], "override_score": 92,
     "reason": "Status epilepticus or severe neurological emergency"},
    {"symptoms": ["severe_difficulty_breathing", "cyanosis"], "override_score": 95,
     "reason": "Severe respiratory failure — immediate oxygen and intubation may be required"},
    {"symptoms": ["vaginal_bleeding", "abdominal_pain"], "override_score": 88,
     "reason": "Possible ectopic pregnancy or obstetric emergency"},
    {"symptoms": ["blood_in_stool", "abdominal_pain", "vomiting"], "override_score": 85,
     "reason": "Possible GI hemorrhage or bowel obstruction"},
    {"symptoms": ["headache", "vision_changes", "vomiting"], "override_score": 87,
     "reason": "Possible raised intracranial pressure or hypertensive emergency"},
    {"symptoms": ["fever", "rash", "joint_pain"], "override_score": 82,
     "reason": "Possible dengue, chikungunya, or other arboviral infection"},
    {"symptoms": ["diarrhea", "vomiting", "dehydration"], "override_score": 85,
     "reason": "Severe gastroenteritis with risk of hypovolemic shock — common in rural India"},
    {"symptoms": ["shortness_of_breath", "fever", "cough"], "override_score": 82,
     "reason": "Possible severe pneumonia or acute respiratory infection"},
    {"symptoms": ["blood_in_sputum", "weight_loss", "night_sweats"], "override_score": 88,
     "reason": "Classic triad for pulmonary tuberculosis — immediate sputum test required"},
    {"symptoms": ["jaundice", "fever", "abdominal_pain"], "override_score": 86,
     "reason": "Possible acute hepatitis, cholangitis, or liver abscess"},
    {"symptoms": ["sudden_vision_loss", "headache"], "override_score": 90,
     "reason": "Possible retinal artery occlusion, optic neuritis, or stroke"},
    {"symptoms": ["seizure", "fever"], "override_score": 88,
     "reason": "Febrile seizure or CNS infection — especially dangerous in children"},
    {"symptoms": ["pregnancy_complications", "high_blood_pressure_symptoms", "headache"], "override_score": 92,
     "reason": "Possible pre-eclampsia or eclampsia — life-threatening obstetric emergency"},
    {"symptoms": ["black_tarry_stools", "dizziness", "fainting"], "override_score": 90,
     "reason": "Possible upper GI bleed with hemodynamic instability"},
    {"symptoms": ["burns", "shortness_of_breath"], "override_score": 88,
     "reason": "Possible inhalational burn injury — airway compromise risk"},
    {"symptoms": ["confusion", "fever", "stiff_neck"], "override_score": 92,
     "reason": "Possible bacterial meningitis or encephalitis"}
]

# ============ BUILD FINAL STRUCTURE ============
knowledge_graph = {
    "version": "1.0",
    "metadata": {
        "description": "Symptom Knowledge Graph for Rural Health Pre-Screening System - India",
        "total_symptoms": len(symptoms),
        "body_systems": ["respiratory", "systemic", "gastrointestinal", "cardiovascular",
                         "neurological", "musculoskeletal", "dermatological", "reproductive",
                         "ophthalmological", "ent"],
        "languages_supported": ["hi", "te", "ta", "en"],
        "base_weight_range": "1-20 (20 = most severe in isolation)",
        "guidelines_reference": "WHO Emergency Triage Assessment and Treatment (ETAT)",
        "created_for": "Task M3-01 — Hackathon Healthcare Project"
    },
    "symptoms": symptoms,
    "red_flag_combinations": red_flag_combinations
}

# Write to file
output_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(output_dir, "symptom_knowledge_graph.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(knowledge_graph, f, indent=2, ensure_ascii=False)

# Print summary
print(f"✅ Symptom Knowledge Graph generated successfully!")
print(f"📄 Output: {output_path}")
print(f"📊 Total symptoms: {len(symptoms)}")

system_counts = {}
red_flag_count = 0
for name, data in symptoms.items():
    sys = data["body_system"]
    system_counts[sys] = system_counts.get(sys, 0) + 1
    if data["is_red_flag"]:
        red_flag_count += 1

print(f"🚩 Red flag symptoms: {red_flag_count}")
print(f"⚠️  Red flag combinations: {len(red_flag_combinations)}")
print("\n📋 Symptoms per body system:")
for sys, count in sorted(system_counts.items()):
    print(f"   {sys}: {count}")
