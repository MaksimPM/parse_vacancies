from src.classes import Parser, DBCreator, DBManager
from src.utils import format_salary_description

def main():
    url = "https://api.hh.ru/employers"
    employers = ['СБЕР', 'Яндекс', 'Тинькофф', 'МТС', 'Банк ВТБ (ПАО)', 'WILDBERRIES', 'МегаФон',
                 'Альфа-Банк', 'VK', 'Ozon']

    db_name = input("Введите имя новой базы данных: ")
    new_bd = DBCreator(db_name)
    new_bd.create_employers_table()
    new_bd.create_vacancies_table()
    print(f"Создана новая база данных '{db_name}'\n")

    for employer in employers:
        hh_parser = Parser(url, employer)
        args_employer = hh_parser.get_employers()
        new_bd.into_table_employers(*args_employer[:3], name='employers')
        print(f"Работодатель '{employer}' успешно добавлен в базу данных")
        vacancies_lst = hh_parser.get_vacancies()

        for vac in vacancies_lst:
            args_vacancy = format_salary_description(vac)
            new_bd.into_table_vacancies(args_vacancy)
        print(f"Вакансии '{vac['employer']['name']}' успешно добавлены в базу данных\n")

    queryes = DBManager(db_name)
    while True:
        query = input('''Выберете действие: 1 - Вывести список всех компаний и количество вакансий у каждой компании.
                    2 - Вывести список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию.
                    3 - Вывести среднюю зарплату по вакансиям.
                    4 - Вывести список всех вакансий, у которых зарплата выше средней по всем вакансиям.
                    5 - Вывести список всех вакансий, в названии которых содержится ключевое слово.

                    0 - Выход.''')
        if query == '1':
            queryes.get_companies_and_vacancies_count()

        elif query == '2':
            queryes.get_all_vacancies()
        elif query == '3':
            queryes.get_avg_salary()
        elif query == '4':
            queryes.get_vacancies_with_higher_salary()
        elif query == '5':
            keyword = input('Введите ключевое слово: ')
            queryes.get_vacancies_with_keyword(keyword)
#        elif query == '6':
#            query = input("Введите запрос к базе данных")
#            queryes.user_query(query)
        elif query == '0':
            print('До свидания!')
            new_bd.cur_close()
            new_bd.conn_close()
            queryes.cur_close()
            queryes.conn_close()
            break
        else:
            print('Нет такого запроса, попробуйте еще раз...')


if __name__ == '__main__':
    main()
