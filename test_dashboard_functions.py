from dashboard_functions import calc_interval, create_app, render_index_page

events = []
updates = []


def test_create_app():
    app = create_app
    print(type(app))

