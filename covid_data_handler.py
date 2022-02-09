from __future__ import annotations
import logging
import sched
import time
import uk_covid19
import load_config

s = sched.scheduler(time.time, time.sleep)

covid_stats = {
    'deaths_total': "Total national deaths: ?",
    'hospital_cases': "National hospital cases: ?",
    'local_7day_infections': "?",
    'national_7day_infections': "?",
}


def parse_csv_data(csv_filename: str) -> list[str]:
    """ Take in CSV format data and process rows into a list

   :param csv_filename: Filename of CSV file to be parsed into a list
   :type csv_filename: str
   :return: Returns a list of strings of the lines in the loaded CSV file
   :rtype: list
    """
    logging.debug("Entered parse_csv_data")
    csv_data_lines = []
    with open(csv_filename, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            csv_data_lines.append(line)
    logging.debug("Return value is: %s", csv_data_lines)
    return csv_data_lines


def process_covid_csv_data(covid_csv_data: list) -> tuple[int, int, int]:
    """Take in CSV list data from parse_csv_data and processes it
        into a tuple of ints.

   :param covid_csv_data: Filename of CSV file to be parsed into a list
   :type covid_csv_data: str
   :return: Returns a tuple of int types
   :rtype: tuple[int, int, int]
    """

    logging.debug("Entered process_covid_csv_data")
    csv_data_values = []
    total_deaths = 0
    current_hospital_cases = 0
    last7days_cases = 0

    for line in covid_csv_data[1:]:
        csv_data_values = line.split(",")
        if csv_data_values[4] != "":
            total_deaths = int(csv_data_values[4])
            break

    for line in covid_csv_data[1:]:
        csv_data_values = line.split(",")
        if csv_data_values[5] != "":
            current_hospital_cases = int(csv_data_values[5])
            break

    cnt = 0
    for index, line in enumerate(covid_csv_data[1:]):
        csv_data_values = line.split(",")
        if cnt == 7:
            break
        if csv_data_values[6] != "":
            csv_data_values = covid_csv_data[index+2].split(",")
            last7days_cases += int(csv_data_values[6])
            cnt += 1

    logging.debug(
        "Return value is: last7days_cases=%s, "
        "current_hospital_cases=%s, "
        "total_deaths%s",
        last7days_cases, current_hospital_cases, total_deaths
        )
    return last7days_cases, current_hospital_cases, total_deaths


def covid_API_request(
        location: str = "Exeter", location_type: str = "ltla") -> dict:
    """Pull data from the API

   :param location: Name of the location that is to  besent off to the news
        api to grab covid-19 stats.
   :type location: str
   :param location_type: Name of the type of location that is to be sent
        off to the news api to grab covid-19 stats.
   :type location_type: str
   :return: Returns a dictionary of statical figures ordered by date
   :rtype: dictionary
    """

    logging.debug("Entered covid_API_request")
    logging.debug("location value is: %s", location)
    logging.debug("location_type value is: %s", location_type)
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

    use_api = uk_covid19.Cov19API(
        filters=use_filters,
        structure=get_structure
    )

    data = use_api.get_csv()
    data = data.splitlines()
    firstline = data[1].strip()
    firstline_list = firstline.split(",")

    # Initialising dictionary
    dictionary = {
        "areaCode": firstline_list[0],
        "areaName": firstline_list[1],
        "areaType": firstline_list[2],
        f"{firstline_list[3]}": {
            "cumDailyNsoDeathsByDeathDate": firstline_list[4],
            "hospitalCases": firstline_list[5],
            "newCasesBySpecimenDate": firstline_list[6]}
    }

    # Filling in data starting from the line after initial
    for line in data[2:]:
        line = line.strip()
        line = line.split(",")
        dictionary[f"{line[3]}"] = {
            "cumDailyNsoDeathsByDeathDate": line[4],
            "hospitalCases": line[5],
            "newCasesBySpecimenDate": line[6]}

    logging.debug("Return value is: %s", dictionary)
    return dictionary


def process_covid_json_data(json_dict: dict) -> tuple[int, int, int]:
    """ Takes in the dictionary found by covid_API_request
        and returns total_deaths, current_hospital_cases and
        last7days_cases in a tuple of integer types.
        For each of these values, the function will look past
        empty values to get the most up-to-date and valid data.

   :param json_dict: Dictionary of covid-19 stats ordered by date
        and returns total_deaths, current_hospital_cases and
        last7days_cases in a tuple of integer types.
   :type json_dict: dict
   :return: Returns a tuple of statical figures
   :rtype: tuple[int, int, int]
    """

    logging.debug("Entered process_covid_json_data")
    total_deaths = 0
    current_hospital_cases = 0
    last7days_cases = 0

    for num in range(3, len(json_dict), 1):
        date = list(json_dict.keys())[num]
        if json_dict[date]['cumDailyNsoDeathsByDeathDate'] != "":
            total_deaths = int(json_dict[date]['cumDailyNsoDeathsByDeathDate'])
            break

    for num in range(3, len(json_dict), 1):
        date = list(json_dict.keys())[num]
        if json_dict[date]['hospitalCases'] != "":
            current_hospital_cases = int(json_dict[date]['hospitalCases'])
            break

    cnt = 0
    for num in range(3, len(json_dict), 1):
        date = list(json_dict.keys())[num]
        if cnt == 7:
            break
        if json_dict[date]['newCasesBySpecimenDate'] != "":
            date = list(json_dict.keys())[num+1]
            last7days_cases += int(json_dict[date]['newCasesBySpecimenDate'])
            cnt += 1
    logging.debug(
        "Return value is: total_deaths=%s, "
        "current_hospital_cases=%s, "
        "last7days_cases=%s",
        total_deaths, current_hospital_cases, last7days_cases
        )
    return total_deaths, current_hospital_cases, last7days_cases


def update_covid_stats(update_name: str) -> None:
    """ Triggered by 'schedule_covid_updates' when a scheduled
        update is set to update at a certain time.
        Will populate/update the covid stats on the dashboard.

   :param update_name: Name of the update which the user set
   :type update_name: str
   :return: Doesnt return anything.
   :rtype: None
    """

    logging.debug("Entered update_covid_stats")
    logging.debug("update_name value is: %s", update_name)
    config = load_config.open_user_config()
    error_msg = (
            "Invalid search parameters. Request for data from"
            " the 'uk_covid19' API has failed."
            " Check config values and retry."
    )

    try:
        local_covid_dict = covid_API_request(
            config['covid_minor'],
            config['covid_minor_id'])
        nation_covid_dict = covid_API_request(
            config['covid_major'],
            config['covid_major_id'])
        covid_stats['deaths_total'] = "Total national deaths: " + \
            str(process_covid_json_data(nation_covid_dict)[0])
        covid_stats['hospital_cases'] = "National hospital cases: " + \
            str(process_covid_json_data(nation_covid_dict)[1])
        covid_stats['local_7day_infections'] = process_covid_json_data(
            local_covid_dict)[2]
        covid_stats['national_7day_infections'] = process_covid_json_data(
            nation_covid_dict)[2]
        covid_stats['from_update_event'] = update_name
        logging.info(
            "Data request to 'uk_covid19' API"
            " was successful."
        )
    except uk_covid19.exceptions.FailedRequestError:
        logging.error(error_msg, exc_info=True)
    except IndexError:
        logging.error(error_msg, exc_info=True)


def schedule_covid_updates(
        update_interval: int, update_name: str) -> sched.Event:
    """ Used to set updates to populate data on dashboard

   :param update_interval: Seconds until update triggeres
   :type update_interval: int
   :param update_name: Name of the update which the user set
   :type update_name: str
   :return: Returns a scheduled event
   :rtype: sched.Event
    """

    logging.debug("Entered schedule_covid_updates")
    logging.debug("update_interval value is: %s", update_interval)
    logging.debug("Scheduled update_name is: %s", update_name)
    return s.enter(
        update_interval, 1, update_covid_stats, {update_name: update_name})


def cancel_covid_update(item: dict[str]) -> None:
    """Cancels covid updates in the updates list.

   :param item: Name of the update so it can be used to
        itentify the update to remove it
   :type item: dictionary
   :return: Doesn't return anything
   :rtype: None
    """
    logging.debug("Entered cancel_covid_update")
    logging.debug("Cancelled covid event is: %s", str(item))
    s.cancel(item['event'])


def run_scheduled_covid_updates() -> None:
    """ Run updates as defined by schedule_covid_updates

   :return: Doesn't return anything
   :rtype: None
    """

    logging.debug("Entered run_scheduled_covid_updates")
    logging.debug("Current covid scheduler queue is: \n%s", str(s.queue))
    s.run(blocking=False)
