import sys
from pathlib import Path
from urllib.parse import urlencode
import json

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

import httpx
import asyncio
from bs4 import BeautifulSoup
from typing import  List
from src.models import BaseDB, UCSDCourseDB

departments = [
    {"text": "Aerospace Studies (AERO ST)", "value": "AERO ST"},
    {"text": "African American Studies (AF AMER)", "value": "AF AMER"},
    {"text": "American Indian Studies (AM IND)", "value": "AM IND"},
    {"text": "American Sign Language (ASL)", "value": "ASL"},
    {"text": "Ancient Near East (AN N EA)", "value": "AN N EA"},
    {"text": "Anthropology (ANTHRO)", "value": "ANTHRO"},
    {"text": "Applied Chemical Sciences (APP CHM)", "value": "APP CHM"},
    {"text": "Arabic", "value": "ARABIC"},
    {"text": "Archaeology (ARCHEOL)", "value": "ARCHEOL"},
    {"text": "Architecture and Urban Design (ARCH&UD)", "value": "ARCH&UD"},
    {"text": "Armenian (ARMENIA)", "value": "ARMENIA"},
    {"text": "Art", "value": "ART"},
    {"text": "Art History (ART HIS)", "value": "ART HIS"},
    {"text": "Arts Education (ARTS ED)", "value": "ARTS ED"},
    {"text": "Asian", "value": "ASIAN"},
    {"text": "Asian American Studies (ASIA AM)", "value": "ASIA AM"},
    {"text": "Astronomy (ASTR)", "value": "ASTR"},
    {"text": "Atmospheric and Oceanic Sciences (A&O SCI)", "value": "A&O SCI"},
    {"text": "Bioengineering (BIOENGR)", "value": "BIOENGR"},
    {"text": "Bioinformatics (Graduate) (BIOINFO)", "value": "BIOINFO"},
    {"text": "Biological Chemistry (BIOL CH)", "value": "BIOL CH"},
    {"text": "Biomathematics (BIOMATH)", "value": "BIOMATH"},
    {"text": "Biomedical Research (BMD RES)", "value": "BMD RES"},
    {"text": "Biostatistics (BIOSTAT)", "value": "BIOSTAT"},
    {"text": "Central and East European Studies (C&EE ST)", "value": "C&EE ST"},
    {"text": "Chemical Engineering (CH ENGR)", "value": "CH ENGR"},
    {"text": "Chemistry and Biochemistry (CHEM)", "value": "CHEM"},
    {"text": "Chicana/o and Central American Studies (CCAS)", "value": "CCAS"},
    {"text": "Chinese (CHIN)", "value": "CHIN"},
    {"text": "Civil and Environmental Engineering (C&EE)", "value": "C&EE"},
    {"text": "Classics (CLASSIC)", "value": "CLASSIC"},
    {"text": "Clusters (CLUSTER)", "value": "CLUSTER"},
    {"text": "Communication (COMM)", "value": "COMM"},
    {"text": "Community Engagement and Social Change (CESC)", "value": "CESC"},
    {"text": "Community Health Sciences (COM HLT)", "value": "COM HLT"},
    {"text": "Comparative Literature (COM LIT)", "value": "COM LIT"},
    {"text": "Computational and Systems Biology (C&S BIO)", "value": "C&S BIO"},
    {"text": "Computer Science (COM SCI)", "value": "COM SCI"},
    {"text": "Conservation of Cultural Heritage (CLT HTG)", "value": "CLT HTG"},
    {"text": "Dance", "value": "DANCE"},
    {"text": "Data Science in Biomedicine (DS BMED)", "value": "DS BMED"},
    {"text": "Design / Media Arts (DESMA)", "value": "DESMA"},
    {"text": "Digital Humanities (DGT HUM)", "value": "DGT HUM"},
    {"text": "Disability Studies (DIS STD)", "value": "DIS STD"},
    {"text": "Dutch", "value": "DUTCH"},
    {"text": "Earth, Planetary, and Space Sciences (EPS SCI)", "value": "EPS SCI"},
    {"text": "East Asian Studies (EA STDS)", "value": "EA STDS"},
    {"text": "Ecology and Evolutionary Biology (EE BIOL)", "value": "EE BIOL"},
    {"text": "Economics (ECON)", "value": "ECON"},
    {"text": "Education (EDUC)", "value": "EDUC"},
    {"text": "Electrical and Computer Engineering (EC ENGR)", "value": "EC ENGR"},
    {"text": "Engineering (ENGR)", "value": "ENGR"},
    {"text": "English (ENGL)", "value": "ENGL"},
    {"text": "English as A Second Language (ESL)", "value": "ESL"},
    {"text": "English Composition (ENGCOMP)", "value": "ENGCOMP"},
    {"text": "Environment (ENVIRON)", "value": "ENVIRON"},
    {"text": "Environmental Health Sciences (ENV HLT)", "value": "ENV HLT"},
    {"text": "Epidemiology (EPIDEM)", "value": "EPIDEM"},
    {"text": "Ethnomusicology (ETHNMUS)", "value": "ETHNMUS"},
    {"text": "European Languages and Transcultural Studies (ELTS)", "value": "ELTS"},
    {"text": "Filipino (FILIPNO)", "value": "FILIPNO"},
    {"text": "Film and Television (FILM TV)", "value": "FILM TV"},
    {"text": "Food Studies (FOOD ST)", "value": "FOOD ST"},
    {"text": "French (FRNCH)", "value": "FRNCH"},
    {"text": "Gender Studies (GENDER)", "value": "GENDER"},
    {"text": "Geography (GEOG)", "value": "GEOG"},
    {"text": "German", "value": "GERMAN"},
    {"text": "Gerontology (GRNTLGY)", "value": "GRNTLGY"},
    {"text": "Global Health (GLB HLT)", "value": "GLB HLT"},
    {"text": "Global Jazz Studies (GJ STDS)", "value": "GJ STDS"},
    {"text": "Global Studies (GLBL ST)", "value": "GLBL ST"},
    {"text": "Graduate Student Professional Development (GRAD PD)", "value": "GRAD PD"},
    {"text": "Greek", "value": "GREEK"},
    {"text": "Health Policy and Management (HLT POL)", "value": "HLT POL"},
    {"text": "Healthcare Administration (HLT ADM)", "value": "HLT ADM"},
    {"text": "Hebrew", "value": "HEBREW"},
    {"text": "Hindi-Urdu (HIN-URD)", "value": "HIN-URD"},
    {"text": "History (HIST)", "value": "HIST"},
    {"text": "Honors Collegium (HNRS)", "value": "HNRS"},
    {"text": "Human Genetics (HUM GEN)", "value": "HUM GEN"},
    {"text": "Hungarian (HNGAR)", "value": "HNGAR"},
    {"text": "Indigenous Languages of the Americas (IL AMER)", "value": "IL AMER"},
    {"text": "Indo-European Studies (I E STD)", "value": "I E STD"},
    {"text": "Indonesian (INDO)", "value": "INDO"},
    {"text": "Information Studies (INF STD)", "value": "INF STD"},
    {"text": "International and Area Studies (I A STD)", "value": "I A STD"},
    {"text": "International Development Studies (INTL DV)", "value": "INTL DV"},
    {"text": "International Migration Studies (I M STD)", "value": "I M STD"},
    {"text": "Iranian", "value": "IRANIAN"},
    {"text": "Islamic Studies (ISLM ST)", "value": "ISLM ST"},
    {"text": "Italian", "value": "ITALIAN"},
    {"text": "Japanese (JAPAN)", "value": "JAPAN"},
    {"text": "Korean (KOREA)", "value": "KOREA"},
    {"text": "Labor Studies (LBR STD)", "value": "LBR STD"},
    {"text": "Latin", "value": "LATIN"},
    {"text": "Latin American Studies (LATN AM)", "value": "LATN AM"},
    {"text": "Law", "value": "LAW"},
    {"text": "Lesbian, Gay, Bisexual, Transgender, and Queer Studies (LGBTQS)", "value": "LGBTQS"},
    {"text": "Life Sciences (LIFESCI)", "value": "LIFESCI"},
    {"text": "Linguistics (LING)", "value": "LING"},
    {"text": "Management (MGMT)", "value": "MGMT"},
    {"text": "Management-Executive MBA (MGMTEX)", "value": "MGMTEX"},
    {"text": "Management-Full-Time MBA (MGMTFT)", "value": "MGMTFT"},
    {"text": "Management-Fully Employed MBA (MGMTFE)", "value": "MGMTFE"},
    {"text": "Management-Global Executive MBA Asia Pacific (MGMTGEX)", "value": "MGMTGEX"},
    {"text": "Management-Master of Financial Engineering (MGMTMFE)", "value": "MGMTMFE"},
    {"text": "Management-Master of Science in Business Analytics (MGMTMSA)", "value": "MGMTMSA"},
    {"text": "Management-PhD (MGMTPHD)", "value": "MGMTPHD"},
    {"text": "Materials Science and Engineering (MAT SCI)", "value": "MAT SCI"},
    {"text": "Mathematics (MATH)", "value": "MATH"},
    {"text": "Mechanical and Aerospace Engineering (MECH&AE)", "value": "MECH&AE"},
    {"text": "Microbiology, Immunology, and Molecular Genetics (MIMG)", "value": "MIMG"},
    {"text": "Middle Eastern Studies (M E STD)", "value": "M E STD"},
    {"text": "Military Science (MIL SCI)", "value": "MIL SCI"},
    {"text": "Molecular and Medical Pharmacology (M PHARM)", "value": "M PHARM"},
    {"text": "Molecular Biology (MOL BIO)", "value": "MOL BIO"},
    {"text": "Molecular Toxicology (MOL TOX)", "value": "MOL TOX"},
    {"text": "Molecular, Cell, and Developmental Biology (MCD BIO)", "value": "MCD BIO"},
    {"text": "Molecular, Cellular, and Integrative Physiology (MC&IP)", "value": "MC&IP"},
    {"text": "Music (MUSC)", "value": "MUSC"},
    {"text": "Music Industry (MSC IND)", "value": "MSC IND"},
    {"text": "Musicology (MUSCLG)", "value": "MUSCLG"},
    {"text": "Naval Science (NAV SCI)", "value": "NAV SCI"},
    {"text": "Near Eastern Languages (NR EAST)", "value": "NR EAST"},
    {"text": "Neurobiology (NEURBIO)", "value": "NEURBIO"},
    {"text": "Neuroscience (Graduate) (NEURO)", "value": "NEURO"},
    {"text": "Neuroscience (NEUROSC)", "value": "NEUROSC"},
    {"text": "Nursing", "value": "NURSING"},
    {"text": "Oral Biology (ORL BIO)", "value": "ORL BIO"},
    {"text": "Pathology and Laboratory Medicine (PATH)", "value": "PATH"},
    {"text": "Philosophy (PHILOS)", "value": "PHILOS"},
    {"text": "Physics", "value": "PHYSICS"},
    {"text": "Physics and Biology in Medicine (PBMED)", "value": "PBMED"},
    {"text": "Physiological Science (PHYSCI)", "value": "PHYSCI"},
    {"text": "Polish (POLSH)", "value": "POLSH"},
    {"text": "Political Science (POL SCI)", "value": "POL SCI"},
    {"text": "Portuguese (PORTGSE)", "value": "PORTGSE"},
    {"text": "Program in Computing (COMPTNG)", "value": "COMPTNG"},
    {"text": "Psychiatry and Biobehavioral Sciences (PSYCTRY)", "value": "PSYCTRY"},
    {"text": "Psychology (PSYCH)", "value": "PSYCH"},
    {"text": "Public Affairs (PUB AFF)", "value": "PUB AFF"},
    {"text": "Public Health (PUB HLT)", "value": "PUB HLT"},
    {"text": "Public Policy (PUB PLC)", "value": "PUB PLC"},
    {"text": "Quantum Science and Technology (QNT SCI)", "value": "QNT SCI"},
    {"text": "Religion, Study of (RELIGN)", "value": "RELIGN"},
    {"text": "Research Practice (RES PRC)", "value": "RES PRC"},
    {"text": "Romanian (ROMANIA)", "value": "ROMANIA"},
    {"text": "Russian (RUSSN)", "value": "RUSSN"},
    {"text": "Scandinavian (SCAND)", "value": "SCAND"},
    {"text": "Science Education (SCI EDU)", "value": "SCI EDU"},
    {"text": "Semitic", "value": "SEMITIC"},
    {"text": "Serbian/Croatian (SRB CRO)", "value": "SRB CRO"},
    {"text": "Slavic (SLAVC)", "value": "SLAVC"},
    {"text": "Social Science (SOC SC)", "value": "SOC SC"},
    {"text": "Social Welfare (SOC WLF)", "value": "SOC WLF"},
    {"text": "Society and Genetics (SOC GEN)", "value": "SOC GEN"},
    {"text": "Sociology (SOCIOL)", "value": "SOCIOL"},
    {"text": "South Asian (S ASIAN)", "value": "S ASIAN"},
    {"text": "Southeast Asian (SEASIAN)", "value": "SEASIAN"},
    {"text": "Spanish (SPAN)", "value": "SPAN"},
    {"text": "Statistics (STATS)", "value": "STATS"},
    {"text": "Swahili", "value": "SWAHILI"},
    {"text": "Thai", "value": "THAI"},
    {"text": "Theater", "value": "THEATER"},
    {"text": "Turkic Languages (TURKIC)", "value": "TURKIC"},
    {"text": "Ukrainian (UKRN)", "value": "UKRN"},
    {"text": "University Studies (UNIV ST)", "value": "UNIV ST"},
    {"text": "Urban Planning (URBN PL)", "value": "URBN PL"},
    {"text": "Vietnamese (VIETMSE)", "value": "VIETMSE"},
    {"text": "World Arts and Cultures (WL ARTS)", "value": "WL ARTS"},
    {"text": "Yiddish (YIDDSH)", "value": "YIDDSH"}
]


async def get_courses_list(department, YearTerm="25W") -> List[UCSDCourseDB]:
    """Get all courses for a given department and term."""
    base_url = "https://sa.ucla.edu/ro/public/soc/Results/GetCourseTitlesPage"
    
    # Create the model and filterFlags dictionaries
    model = {"term_cd":"25W","ses_grp_cd":"%","class_no":None,"crs_catlg_no":None,"subj_area_cd":"AERO ST","subj_area_name":"Aerospace Studies (AERO ST)","class_prim_act_fl":"y"}
    
    filter_flags = {"enrollment_status":"O,W,C,X,T,S","advanced":"y","meet_days":"F","start_time":"8:00 am","end_time":"3:00 pm","meet_locations":None,"meet_units":None,"instructor":None,"class_career":None,"impacted":"N","enrollment_restrictions":None,"enforced_requisites":None,"individual_studies":"n","summer_session":None}

    # Convert dictionaries to JSON strings with double quotes
    model_json = json.dumps(model, separators=(',', ':'))  # Remove spaces
    filter_flags_json = json.dumps(filter_flags, separators=(',', ':'))  # Remove spaces

    # Create params dictionary with raw JSON strings
    params = {
        "search_by": "subject",
        "model": model,
        "filterFlags": filter_flags,
        "isFilter": "false",
        "_": "1735626498227"
    }

    # Create full URL with encoded parameters
    full_url = f"{base_url}?{urlencode(params)}"
    print(f"Generated URL: {full_url}")

    async with httpx.AsyncClient() as client:
        response = await client.get(full_url)
    
    return []

async def get_all_courses() -> List:
    """Get all courses for all departments."""
    all_courses = []

    return all_courses

async def main() -> List[BaseDB]:
    """Main entry point for UCSD course scraping."""
    all_courses = await get_all_courses()
    return all_courses

if __name__ == "__main__":
    asyncio.run(get_courses_list(departments[0]))
