import time
import psycopg2
import requests
from src.utils import config


class Parser:
    def __init__(self, url: str, employer: str):
        self.employer_url = None
        self.url = url
        self.employer = employer

    def get_employers(self):
        employers_lst = []
        for page in range(20):
            params = {'per_page': 100,
                      'page': page,
                      'text': self.employer,
                      'search_field': 'name',
                      'order_by': "publication_time",
                      'archived': False,
                      }
            vacancies = requests.get(self.url, params=params).json()
            employers_lst.extend(vacancies['items'])
            for el in employers_lst:
                if el['name'] == self.employer and el['open_vacancies'] > 10:
                    self.employer_url = el['vacancies_url']
                    return [el['id'], el['name'], el['open_vacancies'], el['vacancies_url']]

    def get_vacancies(self):
        vacancies_lst = []
        for page in range(20):
            params = {'per_page': 100,
                      'page': page,
                      'search_field': 'name',
                      'area': 1,
                      'order_by': "publication_time",
                      'archived': False,
                      }
            vacancies = requests.get(self.employer_url, params=params).json()
            vacancies_lst.extend(vacancies['items'])
            if (vacancies['pages'] - page) <= 1:
                break
            time.sleep(0.5)
        return vacancies_lst


class DBCreator:
    def __init__(self, db_name: str):
        self.__params = config()
        self.conn = psycopg2.connect(dbname='postgres', **self.__params)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()
        self.cur.execute(f"DROP DATABASE IF EXISTS {db_name}")
        self.cur.execute(f"CREATE DATABASE {db_name}")
        self.conn.close()
        self.__params.update({'dbname': db_name})
        self.conn = psycopg2.connect(**self.__params)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

    def create_employers_table(self):
        self.cur.execute('''CREATE TABLE employers
                            (
                                company_id int PRIMARY KEY,
                                company_name varchar(100) NOT NULL,
                                open_vacancies int
                            )'''
                         )

    def create_vacancies_table(self):
        self.cur.execute('''CREATE TABLE vacancies (
                                                    vacancy_id int NOT NULL,
                                                    company_id int NOT NULL,
                                                    title varchar(100),
                                                    salary_from int,
                                                    salary_to int,
                                                    vacancy_url varchar(100),
                                                    description text
                                                    )''')
        self.cur.execute("""ALTER TABLE vacancies ADD CONSTRAINT fk_company_id 
                            FOREIGN KEY(company_id) REFERENCES employers(company_id)""")

    def into_table_employers(self, *args, name):
        self.cur.execute(f"INSERT INTO {name} VALUES {args}")

    def into_table_vacancies(self, vac):
        self.cur.execute(f"INSERT INTO vacancies VALUES(%s, %s, %s, %s, %s, %s, %s)", vac)

    def cur_close(self):
        return self.cur.close()

    def conn_close(self):
        return self.conn.close()


class DBManager:
    def __init__(self, db_name: str):
        self.__params = config()
        self.__params.update({'dbname': db_name})
        self.conn = psycopg2.connect(**self.__params)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

    def cur_close(self):
        return self.cur.close()

    def conn_close(self):
        return self.conn.close()

    def get_companies_and_vacancies_count(self):
        self.cur.execute("SELECT * FROM employers")
        result = self.cur.fetchall()
        for row in result:
            print(f'Компания "{row[1]}", открыто вакансий: {row[2]}')
        print('')

    def get_all_vacancies(self):
        self.cur.execute("""SELECT company_name, title, salary_from, salary_to, vacancy_url FROM employers
                            FULL JOIN vacancies USING(company_id)""")
        result = self.cur.fetchall()
        for row in result:
            if row[2] is None and row[3] is None:
                salary = 'Не указана'
            elif row[2] is None and row[3] is not None:
                salary = f'до {row[3]}'
            elif row[2] is not None and row[3] is None:
                salary = f'от {row[2]}'
            elif row[2] == row[3]:
                salary = row[2]
            else:
                salary = f'{row[2]} - {row[3]}'
            print(f'Компания "{row[0]}", Вакансия: "{row[1]}", зарплата: {salary}, ссылка на вакансию: "{row[4]}"')
        print('')

    def get_avg_salary(self):
        self.cur.execute("SELECT CEIL((AVG(salary_from) + AVG(salary_to))/2) AS average_salary FROM vacancies")
        result = str(self.cur.fetchall())
        avg_salary = ''
        for el in result:
            if el.isdigit():
                avg_salary += el

        print(f'Средняя зарплата: {avg_salary} рублей')
        print('')

    def get_vacancies_with_higher_salary(self):
        self.cur.execute("""SELECT company_name, title, salary_from, salary_to, description, vacancy_url FROM employers
                            FULL JOIN vacancies USING(company_id) 
                            WHERE salary_to > (SELECT CEIL((AVG(salary_from) + AVG(salary_to))/2) FROM vacancies) 
                            OR salary_from > (SELECT CEIL((AVG(salary_from) + AVG(salary_to))/2) FROM vacancies)""")
        result = self.cur.fetchall()

        for row in result:
            if row[2] is None and row[3] is None:
                salary = 'Не указана'
            elif row[2] is None and row[3] is not None:
                salary = f'до {row[3]}'
            elif row[2] is not None and row[3] is None:
                salary = f'от {row[2]}'
            elif row[2] == row[3]:
                salary = row[2]
            else:
                salary = f'{row[2]} - {row[3]}'
            print(f'Компания "{row[0]}", Вакансия: "{row[1]}", зарплата: {salary}, описание: "{row[4]}",'
                  f'ссылка на вакансию: "{row[5]}"')
        print('')

    def get_vacancies_with_keyword(self, keyword):
        self.cur.execute(f"""SELECT company_name, title, vacancy_url FROM employers
                            FULL JOIN vacancies USING(company_id) WHERE title LIKE '%{keyword}%'""")
        result = self.cur.fetchall()
        if result == []:
            print('Нет вакансий, удовлетворяющих условиям поиска.')

        for row in result:
            print(f'Компания "{row[0]}", вакансия: {row[1]}, ссылка на вакансию: {row[2]}')
        print('')

    def user_query(self, query):
        self.cur.execute(query)
        result = self.cur.fetchall()
        for row in result:
            print(row)
        print('')