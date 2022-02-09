import json
import logging

def use_log() -> None:
    """ Opens the logger to keep track of errors and
            debug messages

    :return: Doesn't return anything
    :rtype: None
    """
    format_ = '%(levelname)s: %(message)s (%(asctime)s)'
    date_format = '%Y-%m-%d %H:%M:%S'

    logging.basicConfig(
        filename='app.log',
        filemode='w',
        level=logging.DEBUG,
        format=format_,
        datefmt=date_format
        )


def open_user_config() -> dict:
    """ Opens a config.json file to keep track of constants
        that are potentially customisable or changeable
        outside of the program.
        Also it handles any errors that might incur when 
        reading the config. If it detects that the config
        might have been tampered with, corrupted or
        deleted, then it will create a new config.json
        file with defaults pre-loaded.

    :return: Returns a dictionary which can be used by
        other parts of the program.
    :rtype: dict
    """
    try:
        with open('config.json', "r", encoding="utf-8") as file:
            config = json.load(file)
            file.close()
        test = (
            config['covid_minor'] +
            config['covid_minor_id'] +
            config['covid_major'] +
            config['covid_major_id'] +
            config['news_api_url_stub'] +
            config['news_keywords'] +
            config['news_API_key'] +
            config['news_lang'] +
            config['domains'] +
            config['sort'] +
            config['image'] +
            config['max_articles'] +
            config['max_article_age']
        )
        if test:
            pass

        if config['max_articles']:
            int(config['max_articles'])
        if config['max_article_age']:
            int(config['max_article_age'])
        return config

    except KeyError:
        print(
            "Data entries in config.json missing or corrupted. "
            "Reinitialising config.json file using default values."
            )
        with open('config.json', 'w', encoding="utf-8") as file:
            file.write(
                '{\n'
                '\t"covid_minor": "Exeter",\n'
                '\t"covid_minor_id": "ltla",\n'
                '\t"covid_major": "England",\n'
                '\t"covid_major_id": "nation",\n'
                '\t"news_api_url_stub": '
                '"https://newsapi.org/v2/everything?",\n'
                '\t"news_keywords": "Covid COVID-19 coronavirus",\n'
                '\t"news_API_key": "",\n'
                '\t"news_lang": "en",\n'
                '\t"domains": "",\n'
                '\t"sort": "relevancy",\n'
                '\t"max_articles": "5",\n'
                '\t"max_article_age": "",\n'
                '\t"image": "covid.png"\n'
                '}'
            )
            file.close()
        with open('config.json', "r", encoding="utf-8") as file:
            config = json.load(file)
            file.close()
            return config

    except FileNotFoundError:
        print(
            "Config file not found. "
            "config.json file created using default values."
            )
        with open('config.json', 'w', encoding="utf-8") as file:
            file.write(
                '{\n'
                '\t"covid_minor": "Exeter",\n'
                '\t"covid_minor_id": "ltla",\n'
                '\t"covid_major": "England",\n'
                '\t"covid_major_id": "nation",\n'
                '\t"news_api_url_stub": '
                '"https://newsapi.org/v2/everything?",\n'
                '\t"news_keywords": "Covid COVID-19 coronavirus",\n'
                '\t"news_API_key": "",\n'
                '\t"news_lang": "en",\n'
                '\t"domains": "",\n'
                '\t"sort": "relevancy",\n'
                '\t"max_articles": "5",\n'
                '\t"max_article_age": "",\n'
                '\t"image": "covid.png"\n'
                '}'
            )
            file.close()
        with open('config.json', "r", encoding="utf-8") as file:
            config = json.load(file)
            file.close()
            return config

    except ValueError:
        print(
            "Unknown character(s) in config.json where integer expected."
            " Please check max_articles and max_article_age. "
            "config.json file created using default values."
            )
        with open('config.json', 'w', encoding="utf-8") as file:
            file.write(
                '{\n'
                '\t"covid_minor": "Exeter",\n'
                '\t"covid_minor_id": "ltla",\n'
                '\t"covid_major": "England",\n'
                '\t"covid_major_id": "nation",\n'
                '\t"news_api_url_stub": '
                '"https://newsapi.org/v2/everything?",\n'
                '\t"news_keywords": "Covid COVID-19 coronavirus",\n'
                '\t"news_API_key": "",\n'
                '\t"news_lang": "en",\n'
                '\t"domains": "",\n'
                '\t"sort": "relevancy",\n'
                '\t"max_articles": "5",\n'
                '\t"max_article_age": "",\n'
                '\t"image": "covid.png"\n'
                '}'
            )
            file.close()
        with open('config.json', "r", encoding="utf-8") as file:
            config = json.load(file)
            file.close()
