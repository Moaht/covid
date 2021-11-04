from uk_covid19 import Cov19API
import sched, time


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


def parse_api_data(data):
    """Parses data from the API and returns as a dictionary"""
    line = data.splitlines()[1]
    line = line.strip()
    recent = line.split(",")

    # Change to nested dictionaries (or list[] for some keys) 
    # if you need to keep data from all dates
    dictionary = {
            "areaCode": recent[0],
            "areaName": recent[1],
            "areaType": recent[2],
            "date": recent[3],
            "cumDailyNsoDeathsByDeathDate": recent[4],
            "hospitalCases": recent[5],
            "newCasesBySpecimenDate": recent[6]
            }
    return dictionary


def covid_API_request(location="Exeter", location_type="ltla"):
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
        structure=get_structure
        )

    data = use_api.get_csv()

    return parse_api_data(data)


# TODO make sure that update interval is set to correct value
# we are assuming that update interval is in seconds
# can change interval to a particular time of day later on if necessary
def schedule_covid_updates(update_interval=10, update_name="thing"):
    """Get periodical updates from API"""
    while True:
        update_api = sched.scheduler()
        update_api.enter(update_interval, 1, covid_API_request)
        update_api.run()
