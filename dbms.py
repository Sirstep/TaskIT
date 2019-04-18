import sqlite3
from sqlite3 import Error
from datetime import date, datetime


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None


def create_table(conn, table):
    try:
        c = conn.cursor()
        c.execute(table)
    except Error as e:
        print(e, "OOPS")


def fill_database(conn):
    tables = []
    tables.append(""" CREATE TABLE IF NOT EXISTS days (
                                        date text PRIMARY KEY,
                                        dow integer NOT NULL,
                                        doy integer NOT NULL,
                                        status text
                                    ); """)

    tables.append(""" CREATE TABLE IF NOT EXISTS tasks (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        note text,
                                        date text,
                                        type text REFERENCES _types(name),
                                        deadline bool,
                                        reminder bool,
                                        exclusive bool, 
                                        start_time text,
                                        end_time text,
                                        every_amt integer,
                                        every_unit text,
                                        for_amt integer,
                                        for_unit text,
                                        _group text REFERENCES _groups(name),
                                        project text REFERENCES projects(name),
                                        cal_compat bool
                                    ); """)

    tables.append(""" CREATE TABLE IF NOT EXISTS projects (
                                        project_id integer PRIMARY KEY,
                                        name text UNIQUE,
                                        note text,
                                        type text
                                    ); """)

    tables.append(""" CREATE TABLE IF NOT EXISTS _groups (
                                        group_id integer PRIMARY KEY,
                                        name text UNIQUE,
                                        note text,
                                        type text
                                    ); """)

    tables.append(""" CREATE TABLE IF NOT EXISTS _types (
                                        type_id integer PRIMARY KEY,
                                        name text UNIQUE
                                    ); """)

    # type is relation (work, school, personal, and subcategories)
    tables.append(""" CREATE TABLE IF NOT EXISTS contacts (
                                        user_id text PRIMARY KEY,
                                        name text,
                                        note text,
                                        type text
                                    ); """)

    tables.append(""" CREATE TABLE IF NOT EXISTS messages (
                                        id integer PRIMARY KEY,
                                        title text,
                                        body text,
                                        sender text NOT NULL,
                                        date_sent text,
                                        time_sent text,
                                        date_read text,
                                        time_read text,
                                        FOREIGN KEY (sender) REFERENCES contacts (user_id)
                                    ); """)

    tables.append(""" CREATE TABLE IF NOT EXISTS project_contributors (
                                        project text NOT NULL,
                                        contributor text NOT NULL,
                                        contributor_role text,
                                        note text,
                                        start_date text,
                                        end_date text,
                                        start_time text,
                                        end_time text,
                                        FOREIGN KEY (project) REFERENCES projects (project_id)
                                        FOREIGN KEY (contributor) REFERENCES contacts (user_id)
                                    ); """)

    for table in tables:
        create_table(conn, table)


# import google calendar
# Will
def import_calendar(conn, calendar=None):
    # fill_calendar(year of first task in imported calendar, year of last task)
    pass


def fill_calendar(conn, start_year=date.today().year - 1, end_year=date.today().year + 1):
    month_lengths = {
        'jan': 31,
        'feb': 28,
        'mar': 31,
        'apr': 30,
        'may': 31,
        'jun': 30,
        'jul': 31,
        'aug': 31,
        'sep': 30,
        'oct': 31,
        'nov': 30,
        'dec': 31
    }

    # generalize by making start_year = current year OR previous if imported or previous button is clicked
    for year in range(start_year, end_year + 1):
        fill_year(conn, year, month_lengths)


def fill_year(conn, year, month_lengths):
    if year % 4 == 0:
        month_lengths['feb'] += 1

    cur = conn.cursor()
    m = 1
    doy = 1

    for month in month_lengths.keys(): # should I replace with "range(len(month_lengths))"?
        for day in range(1, month_lengths[month] + 1):
            date = ('0' if m < 10 else '') + str(m) + ('-0' if day < 10 else '-') + str(day) + '-' + str(year)
            # print(str(date))
            stmnt = '''INSERT INTO days(date, dow, doy, status)
            VALUES(?,?,?,?) '''
            values = (str(date), int((doy - 1) % 7), int(doy), str('open'))
            cur.execute(stmnt, values)
            doy += 1
        m += 1

    if year % 4 == 0:
        month_lengths['feb'] -= 1
