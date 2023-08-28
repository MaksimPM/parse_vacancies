from configparser import ConfigParser


def config(filename="config.ini", section="postgresql"):
    parser = ConfigParser()  # create a parser
    parser.read(filename)  # read config file
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} is not found in the {1} file.'.format(section, filename))
    return db


def format_salary_description(vac):
    if vac['snippet']['requirement'] is None:
        requirement = ''
    else:
        requirement = vac['snippet']['requirement']
    if vac['snippet']['responsibility'] is None:
        responsibility = ''
    else:
        responsibility = vac['snippet']['responsibility']
    description = requirement + responsibility
    edit_description = description.replace('\'', '')
    if vac['salary'] is None:
        salary_from = None
        salary_to = None
    else:
        if vac['salary']['from'] is not None:
            salary_from = vac['salary']['from']
        else:
            salary_from = None

        if vac['salary']['to'] is not None:
            salary_to = vac['salary']['to']
        else:
            salary_to = None
    args_vacancy = [vac['id'], vac['employer']['id'], vac['name'], salary_from, salary_to,
                    vac['alternate_url'], edit_description]
    return args_vacancy
