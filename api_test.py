from uk_covid19 import Cov19API

location_type = "ltla"
location = "Exeter"

use_filters = [
    f"areaType={location_type}",
    f"areaName={location}"
    ]

get_structure = {

    "areaCode": "areaCode",
    "areaName": "areaName",
    "areaType": "areaType",
    "date": "date",
    "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
    "hospitalCases": "hospitalCases",
    "newCasesBySpecimenDate": "newCasesBySpecimenDate"
    }

use_api = Cov19API(
    filters = use_filters,
    structure = get_structure,
    # latest_by = "newCasesBySpecimenDate"
    )

data = use_api.get_csv()
print(data)