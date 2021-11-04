from uk_covid19 import Cov19API


def parse_csv_data(csv_filename):
    """Take in data and process rows as list"""
    list = []
    with open(csv_filename, "r") as file:
        for line in file:
            line = line.strip()
            list.append(line)
    return list


# TODO: ask Matt if you can create your own functions to reuse code
# example below...
def process_covid_csv_data(covid_csv_data):
    """Pass data from parse_csv_data and process it"""
    list = []
    total_deaths = 0
    current_hospital_cases = 0
    last7days_cases = 0

# TODO: add check (assert?) that the number is descending as it is iterating
    for line in covid_csv_data[1:]:
        list = line.split(",")
        if list[4] != "":
            total_deaths = int(list[4])
            break

# TODO: add check (assert?) that the number is descending as it is iterating
    for line in covid_csv_data[1:]:
        list = line.split(",")
        if list[5] != "":
            current_hospital_cases = int(list[5])
            break

    for line in covid_csv_data[1:8]:
        list = line.split(",")
        if list[6] != "":
            last7days_cases += int(list[6])

    return last7days_cases, current_hospital_cases, total_deaths


# TODO check with Matt if "default values" means default
#  constructor; and if so, change function to class and set
#  default constructor to exeter and ltla
def covid_API_request(location, location_type):
    """Pull data from the API"""
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
        filters=use_filters,
        structure=get_structure,
        # latest_by = "newCasesBySpecimenDate"
        )

    data = use_api.get_csv()
    print(data)

covid_API_request("Exeter", "ltla")