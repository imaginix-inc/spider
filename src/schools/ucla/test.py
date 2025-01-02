import json
import time
import httpx
import asyncio

base_url = "https://sa.ucla.edu/ro/public/soc/Results/GetCourseSummary"

# Construct model from course data
model = {
"Term": "25W",
"SubjectAreaCode": "AERO ST",
"CatalogNumber": "0001B   ",
"IsRoot": True,
"SessionGroup": "%",
"ClassNumber": "%",
"SequenceNumber": None,
"Path": "AEROST0001B",
"MultiListedClassFlag": "n",
"Token": "MDAwMUIgICBBRVJPU1QwMDAxQg=="
}

# Construct filter flags
filter_flags = {
    "enrollment_status": "O,W,C,X,T,S",
    "advanced": "y",
    "meet_days": "F",
    "start_time": "8:00 am",
    "end_time": "3:00 pm",
    "meet_locations": None,        # Will be converted to null in JSON
    "meet_units": None,           # Will be converted to null in JSON
    "instructor": None,           # Will be converted to null in JSON
    "class_career": None,         # Will be converted to null in JSON
    "impacted": "N",
    "enrollment_restrictions": None,  # Will be converted to null in JSON
    "enforced_requisites": None,     # Will be converted to null in JSON
    "individual_studies": "n",
    "summer_session": None           # Will be converted to null in JSON
}

# Create query parameters
params = {
"model": json.dumps(model, separators=(',', ':'), ensure_ascii=False),
"FilterFlags": json.dumps(filter_flags, separators=(',', ':'), ensure_ascii=False),
"_": str(int(time.time() * 1000))
}
print(params)

async def fetch_course_data():
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(
                base_url,
                params=params,
            )
            print(response.text)
        except Exception as e:
            print(f"Request error: {e}")

# Run the async function
asyncio.run(fetch_course_data())
