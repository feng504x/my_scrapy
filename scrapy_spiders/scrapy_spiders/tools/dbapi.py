# -*- coding: utf-8 -*-

__all__ = ['DBApi']

import MySQLdb


class DBApi(object):

    def __init__(self, db_config, auto_commit=True, dict_cursor=True, disable_warning=True):
        super(DBApi, self).__init__()
        try:
            self.conn = MySQLdb.connect(**db_config)
        except MySQLdb.Error as e:
            print(e)
        self._config = db_config
        self._autocommit = auto_commit
        self.conn.autocommit(auto_commit)
        self._dict_cursor = dict_cursor
        self._disable_warning = disable_warning

        if dict_cursor:
            self._cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        else:
            self._cursor = self.conn.cursor()

        if disable_warning:
            self._cursor._defer_warnings = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__del__()

    def __del__(self):
        if self.conn is not None:
            self.conn.close()

        self.conn = None
        self._cursor = None

    def close(self):
        return self.__del__()

    def get_insert_id(self):
        return self.conn.insert_id()

    def _run_sql(self, sql, param=None, func=None):
        cmd = self._cursor.execute if func is None else func
        rownum = cmd(sql, param)
        return rownum

    def query_one(self, sql, param=None):
        self._run_sql(sql, param)
        return self._cursor.fetchone()

    def query_many(self, sql, param=None):
        self._run_sql(sql, param)
        return self._cursor.fetchall()

    def query_batch(self, size, sql, param=None):
        self._run_sql(sql, param)
        while True:
            data = self._cursor.fetchmany(size)
            if data:
                yield data
            else:
                break

    def modify(self, sql, param=None):
        return self._run_sql(sql, param)

    def modify_many(self, sql, param=None):
        return self._run_sql(sql, param, self._cursor.executemany)

    def autocommit(self, auto_commit):
        self._autocommit = auto_commit
        self.conn.autocommit(auto_commit)

    def is_autocommit(self):
        return self._autocommit

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def begin(self):
        self.query_one('BEGIN')
