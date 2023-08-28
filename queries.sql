--Получает список всех компаний и количество вакансий у каждой компании.
        SELECT * FROM employers

--Получает список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию.
        SELECT company_name, title, salary_from, salary_to, vacancy_url FROM employers
        FULL JOIN vacancies USING(company_id)

--Получает среднюю зарплату по вакансиям.
        SELECT CEIL((AVG(salary_from) + AVG(salary_to))/2) AS average_salary FROM vacancies

--Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.
        SELECT company_name, title, salary_from, salary_to, description, vacancy_url FROM employers
        FULL JOIN vacancies USING(company_id)
        WHERE salary_to > (SELECT CEIL((AVG(salary_from) + AVG(salary_to))/2) FROM vacancies)
           OR salary_from > (SELECT CEIL((AVG(salary_from) + AVG(salary_to))/2) FROM vacancies

--Получает список всех вакансий, в названии которых содержатся переданные в метод слова, например 'python'
        SELECT company_name, title, vacancy_url FROM employers
        FULL JOIN vacancies USING(company_id) WHERE title LIKE '%keyword%'