from bs4 import BeautifulSoup
import requests
from src.models import UCSFCourseDB, BaseDB
from typing import List
from src.process import post_process
from tqdm.asyncio import tqdm
import httpx
import aiohttp
import asyncio

base_url = "https://catalog.ucsf.edu/course-catalog"
subjects = {
    "anatomy": "Anatomy",
    "ane_periop": "Anesthesia and Perioperative Care",
    "anthropol": "Anthropology",
    "aicompdrug": "Artificial Intelligence and Computational Drug Discovery and Development",
    "biochem": "Biochemistry",
    "bioengr": "Bioengineering",
    "biomed_img": "Biomedical Imaging",
    "bio_md_inf": "Biomedical Informatics",
    "biomed_sci": "Biomedical Sciences",
    "biophrm_sc": "Biopharmaceutical Sciences",
    "biophysics": "Biophysics",
    "biostat": "Biostatistics",
    "cell_biol": "Cell Biology",
    "chemistry": "Chemistry",
    "cl_pharm": "Clinical Pharmacy",
    "comp_hlth": "Computational Precision Health",
    "cran_anom": "Craniofacial Anomalies",
    "datasci": "Data Science",
    "den_pub_hl": "Dental Public Health",
    "dentalsci": "Dental Sciences",
    "dermatol": "Dermatology",
    "dev_stmcel": "Developmental and Stem Cell Biology",
    "emerg_med": "Emergency Medicine",
    "endicrinol": "Endocrinology",
    "epidemiol": "Epidemiology",
    "eqbraihlth": "Equity in Brain Health",
    "fam_cm_med": "Family and Community Medicine",
    "gencounsel": "Genetic Counseling",
    "genetics": "Genetics",
    "globl_hlth": "Global Health Sciences",
    "grad": "Graduate Studies",
    "hlth_admin": "Healthcare Administration",
    "hist_hl_sc": "History of Health Sciences",
    "implmt_sci": "Implementation Science",
    "interdept": "Interdepartmental Studies",
    "lab_med": "Laboratory Medicine",
    "medicine": "Medicine",
    "microbiol": "Microbiology",
    "neuro_surg": "Neurological Surgery",
    "neurology": "Neurology",
    "neurosci": "Neurosciences",
    "nursing": "Nursing",
    "skills_lab": "Nursing Skills Lab",
    "nursadvpr": "Nursing, Advanced Practice",
    "nutrition": "Nutrition",
    "ob_gyn_r_s": "Obstetrics, Gynecology, and Reproductive Science",
    "ophthalmol": "Ophthalmology",
    "or_cra_fac": "Oral and Craniofacial Sciences",
    "or_mx_surg": "Oral and Maxillofacial Surgery",
    "oral_med": "Oral Medicine",
    "oral_rad": "Oral Radiology",
    "orthodont": "Orthodontics",
    "ortho_surg": "Orthopaedic Surgery",
    "otolaryn": "Otolaryngology",
    "pathology": "Pathology",
    "pt_cn_care": "Patient-Centered Care",
    "ped_dent": "Pediatric Dentistry",
    "pediatrics": "Pediatrics",
    "periodont": "Periodontics",
    "pharm_chem": "Pharmaceutical Chemistry",
    "pharmgenom": "Pharmacogenomics",
    "pharmacol": "Pharmacology",
    "pharmis": "Pharmacy Integrated Sciences",
    "phys_ther": "Physical Therapy",
    "prv_rs_den": "Preventive and Restorative Dental Sciences",
    "psychiatry": "Psychiatry",
    "psychology": "Psychology",
    "rad_oncol": "Radiation Oncology",
    "radiology": "Radiology",
    "rehab_sci": "Rehabilitation Science",
    "restor_den": "Restorative Dentistry",
    "scimethods": "Scientific Methods",
    "sociology": "Sociology",
    "surgery": "Surgery",
    "urology": "Urology"
}


async def fetch_course_info(url, subject):
    async with aiohttp.ClientSession() as session:
        # Retry up to 3 times if request fail
        for _ in range(3):
            try:
                async with session.get(url) as resp:
                    resp_text = await resp.text()
                    if resp_text:
                        break
            except Exception as ex:
                print(ex)
                continue
        if not resp_text:
            return []
        soup = BeautifulSoup(resp_text, 'html.parser')
        courseblocks = soup.find_all('div', class_='courseblock')

        courses = []
        for block in courseblocks:
            course_code = block.find('span', class_="detail-code").get_text(strip=True)
            splitted_course_code = course_code.split(" ")
            course_prefix = splitted_course_code[0]
            course_number = splitted_course_code[-1]

            course_title = block.find('span', class_="detail-title").get_text(strip=True)
            course_unit = block.find('span', class_="detail-hours_html").get_text(strip=True).split(" ")[0][1:]
            course_term = block.find('span', class_="detail-offering").get_text(strip=True)

            instructor_blocks = block.select('div > p > span.skip-makebubbles > span > a')
            course_instructor = instructor_blocks[0].get_text(strip=True) if instructor_blocks else None

            activity_tag = block.find('p', class_="detail-activities")
            if activity_tag:
                course_activities = ''.join(str(item).strip() for item in activity_tag.contents if not hasattr(item, 'contents')).strip()
                course_description = activity_tag.find_parent('div').next_sibling.find('p').get_text(strip=True)
            else:
                course_activities, course_description = None, None

            course = UCSFCourseDB(
                remark=course_description, term=course_term, units=course_unit,
                activity=course_activities, prefix=course_prefix, number=course_number,
                instructor_name=course_instructor, course_name=course_title, source_url=url,
                subject=subject
            )
            courses.append((course, course_title))

        return courses

async def main() -> List[UCSFCourseDB]:
    course_titles = []
    courses_db = []
    tasks = []

    async with aiohttp.ClientSession() as session:
        for key, value in tqdm(subjects.items()):
            url = f"{base_url}/{key}"
            tasks.append(fetch_course_info(url, value))

        results = await asyncio.gather(*tasks)

        for l in results:
            if not l:
                continue
            for db, title in l:
                course_titles.append(title)
                courses_db.append(db)

    print(len(courses_db))
    # Assuming post_process is also async
    courses_db = await post_process(courses_db, course_titles, course_titles)
    return courses_db
