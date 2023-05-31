#!/usr/bin/env python3

import sys
from pathlib import Path
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import sqlite3


def sql_connection(filename: Path) -> sqlite3.Connection:
    """
    Returns an Sqlite3 Cursor object from a given path to a sqlite3 database file

    Parameters
    ----------
    filename : Path
        Full path to a sqlite3 database file

    Returns
    -------
    sqlite3.Connection
        Sqlite3 Connection object for updating table

    """
    try:
        return sqlite3.connect(Path(filename))
    except sqlite3.Error:
        print(sqlite3.Error)
        sys.exit(-1)


def sql_table(obj: sqlite3.Cursor) -> None:
    """
    Creates the initial sqlite3 table for PR states and status

    Parameters
    ----------
    obj : sqlite3.Cursor
         Cursor object for Sqlite3

    """

    obj.execute("CREATE TABLE processing(pr integer PRIMARY KEY, state text, status text)")


def sql_insert(obj: sqlite3.Cursor, entities: list) -> None:
    """
    Inserts a new row in sqlite3 table with PR, state, and status

    Parameters
    ----------
    obj : sqlite3.Cursor
        Cursor object for Sqlite3
    entities : list
        The list three string values that go into sqlite table (pr, state, status)

    """

    obj.execute('INSERT INTO processing(pr, state, status) VALUES(?, ?, ?)', entities)


def sql_update(obj: sqlite3.Cursor, pr: str, state: str, status: str) -> None:
    """Updates table for a given pr with new values for state and status

    Parameters
    ----------
    obj : sqlite.sql_connection
        sqlite3 Cursor Object
    pr : str
        The given pr number to update in the table
    state : str
        The new value for the state (Open, Closed)
    status: str
        The new value for the status (Ready, Running, Failed)

    """

    obj.execute(f'UPDATE processing SET state = "{state}", status = "{status}" WHERE pr = {pr}')


def sql_fetch(obj: sqlite3.Cursor) -> list:
    """ Gets list of all rows in table

    Parameters
    ----------
    obj : sqlite.sql_connection
        sqlite3 Cursor Object

    """

    obj.execute('SELECT * FROM processing')
    return obj.fetchall()


def sql_remove(obj: sqlite3.Cursor, pr: str) -> None:
    """ Removes the row from table with given pr number

    Parameters
    ----------
    obj : sqlite.sql_connection
        sqlite3 Connection Object
    pr : str
        pr number acting as key for removing the row with in it

    """

    obj.execute(f'DELETE FROM processing WHERE pr = {pr}').rowcount


def input_args():

    description = """Arguments for creating and updating db file for pr states
    """

    parser = ArgumentParser(description=description,
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('sbfile', help='SQLite3 database file with PR list', type=str)
    parser.add_argument('--create', help='create sqlite file for pr list status', action='store_true', required=False)
    parser.add_argument('--add_pr', nargs=1, metavar='PR', help='add new pr to list (defults to: Open,Ready)', required=False)
    parser.add_argument('--remove_pr', nargs=1, metavar='PR', help='removes pr from list', required=False)
    parser.add_argument('--update_pr', nargs=3, metavar=('pr', 'state', 'status'), help='updates state and status of a given pr', required=False)
    parser.add_argument('--display', help='output pr table', action='store_true', required=False)

    args = parser.parse_args()
    return args


if __name__ == '__main__':

    args = input_args()

    con = sql_connection(args.sbfile)
    obj = con.cursor()

    if args.create:
        sql_table(obj)

    if args.add_pr:
        rows = sql_fetch(obj)
        for row in rows:
            if str(row[0]) == str(args.add_pr[0]):
                print(f"pr {row[0]} already is in list: nothing added")
                sys.exit(0)

        entities = (args.add_pr[0], 'Open', 'Ready')
        sql_insert(obj, entities)

    if args.update_pr:
        pr = args.update_pr[0]
        state = args.update_pr[1]
        status = args.update_pr[2]
        sql_update(obj, pr, state, status)

    if args.remove_pr:
        sql_remove(obj, args.remove_pr[0])

    if args.display:
        rows = sql_fetch(obj)
        for row in rows:
            print(' '.join(map(str, row)))

    con.commit()
    con.close()