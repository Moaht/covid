import sched
import time
from covid_data_handler import parse_csv_data
from covid_data_handler import process_covid_csv_data
from covid_data_handler import covid_API_request
from covid_data_handler import schedule_covid_updates
from covid_data_handler import process_covid_json_data
from covid_data_handler import cancel_covid_update

def test_parse_csv_data():
    data = parse_csv_data('nation_2021-10-28.csv')
    assert len(data) == 639
    print(len(data) == 639)


def test_process_covid_csv_data():
    last7days_cases, current_hospital_cases, total_deaths = \
        process_covid_csv_data(
            parse_csv_data('nation_2021-10-28.csv')
            )
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544


def test_covid_API_request():
    data = covid_API_request()
    assert isinstance(data, dict)


def test_schedule_covid_updates():
    test_event = schedule_covid_updates(
        update_interval=20, update_name='update test'
        )
    assert isinstance(test_event, sched.Event)


def test_process_covid_json_data():
    data = process_covid_json_data(covid_API_request())
    assert isinstance(data, tuple)


def test_cancel_covid_update():
    test_scheduler = sched.scheduler(time.time, time.sleep)
    test_event = test_scheduler.enter(
        200, 1, print, argument="Don't print this."
        )
    event_dict = {'event': test_event}
    print(len(test_scheduler.queue))
    cancel_covid_update(event_dict)
    assert (len(test_scheduler.queue)) == 0
