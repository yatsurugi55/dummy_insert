import os
import re
import sys
import numpy as np
import random
import string
import struct
import datetime
import traceback
from argparse import ArgumentParser

import ibm_db
import connect_conf

class DummyInsert:
    DAT = string.digits + string.ascii_lowercase + string.ascii_uppercase

    def main(self):
        args = self.get_option()
        dbname = args.dbname         # args1
        input_file = args.input_file # args2
        rows = args.rows             # args3

        username = connect_conf.username
        password = connect_conf.password

        schema = username.upper()
        l_list = []
        g_list = []
        col_types = []
        col_sizes = []
        col_size_fractions = []
        col_num = 0
        count = 0
        COMMIT_ROW = 1000

        # connect 
        try:
            conn = ibm_db.pconnect(dbname, username, password)
        except Exception as e:
            print("Connection failed")
            traceback.print_exc()
            return

        ibm_db.autocommit(conn, ibm_db.SQL_AUTOCOMMIT_OFF)   

        # get the sql
        try:
            insert_sql = self.get_sql(input_file)
        except Exception as e:
            print("Cannot read sqlfile.")
            traceback.print_exc() 
            return

        stmt = ibm_db.prepare(conn, insert_sql)
        if not stmt:
            print("Failed in prepare.")
            return
    
        # get the table name from sql, and check
        tabname = re.split("[ ]*INSERT INTO[ ]+", insert_sql)[1]
        tabname = re.split("[ ]+VALUES", tabname)[0]
        if tabname is None:
            print("Error in contents of sqlfile.")
            return

        # verify whether the table exist
        rc = self.chk_table(conn, schema, tabname)
        if not rc:
            print("table name " + tabname + " is not found in " + dbname)
            return
    
        # get the number of the columns
        result = ibm_db.columns(conn, None, None, tabname)
        col = ibm_db.fetch_tuple(result)
        while (col):
            col_num = col_num + 1
            col = ibm_db.fetch_tuple(result)
    
        # list of column type and column size
        col_info = ibm_db.columns(conn, None, None, tabname)
        col = ibm_db.fetch_tuple(col_info)
        while (col):
            col_types.append(col[5])
            col_sizes.append(col[6])
            col_size_fractions.append(col[8])
            col = ibm_db.fetch_tuple(col_info)
    
        for i in range(rows):
            count = 0
            random.seed()
            
            for j in range(len(col_types)):
                count = count + 1
    
                if self.chk_par_mark(count, insert_sql):
                    if col_types[j] == "CHAR":
                        param = self.get_random_char(col_sizes[j])
                        
                    elif col_types[j] == "VARCHAR":
                        param = self.get_random_char(col_sizes[j])
            
                    elif col_types[j] == "SMALLINT":
                        param = self.get_random_smallint()
            
                    elif col_types[j] == "INTEGER":
                        param = self.get_random_integer()
            
                    elif col_types[j] == "BIGINT":
                        param = self.get_random_long()
            
                    elif col_types[j] == "REAL":
                        param = self.get_random_real()
            
                    elif col_types[j] == "FLOAT":
                        param = self.get_random_double()
            
                    elif col_types[j] == "DOUBLE":
                        param = self.get_random_double()
                   
                    elif col_types[j] == "DECIMAL":
                        digit = col_sizes[j] - col_size_fractions[j] 
                        param = self.get_random_decimal(digit)
            
                    elif col_types[j] ==  "NUMERIC":
                        digit = col_sizes[j] - col_size_fractions[j]
                        param = self.get_random_decimal(digit)
             
                    elif col_types[j] == "DATE":
                        param = self.get_random_date()
            
                    elif col_types[j] == "TIME":
                        param = self.get_random_time()
            
                    elif col_types[j] == "TIMESTAMP":
                        param = self.get_random_timestamp()
      
                    elif col_types[j] == "BLOB":
                        param = self.get_random_byte(col_sizes[j])
    
                    elif col_types[j] == "CLOB":
                        param = self.get_random_char(col_sizes[j])
    
                    else:
                        param = ''       
        
                    # set the parameter to the list
                    self.set_param_list(param, l_list) 
        
                # end of the columns
                if count == col_num:
                    self.concat_list(g_list, l_list)
                    l_list = []
    
                    if ((i + 1) % COMMIT_ROW == 0):
                        #print g_list
                        rc = ibm_db.execute_many(stmt,
                                tuple(tuple(x) for x in g_list))
    
                        rc = ibm_db.commit(conn)
                        g_list = []
    
        if len(g_list) != 0: 
            print g_list
            rc = ibm_db.execute_many(stmt, tuple(tuple(x) for x in g_list))
            rc = ibm_db.commit(conn)
    
        ibm_db.close(conn)
    
    def get_option(self):
        argparser = ArgumentParser()
        argparser.add_argument('-d', '--dbname', type=str, required=True)
        argparser.add_argument('-f', '--input_file', type=str, required=True)
        argparser.add_argument('-r', '--rows', type=int, default=1)

        args = argparser.parse_args()
       
        return args

    # verify the table by using ibm_db api
    def chk_table(self, conn, schema, tabname):
        tables = []
        tables_set = ibm_db.tables(conn, None, schema)
        result = ibm_db.fetch_both(tables_set)
        while (result):
            tables.append(result[2])
            result = ibm_db.fetch_both(tables_set)
      
        if tabname in tables:
            return True

        return False    
   
    # check whether or not the column is the parameter marker 
    def chk_par_mark(self, count, sql):
        rc = False
        par_val = re.split("VALUES[ ]+", sql)[1].split(",")

        if "?" in par_val[count-1]:
            rc = True

        return rc

    # return the max value of binary32
    # (all 1) * 2 ^ (all 1)
    def get_max_binary32(self):
        return struct.unpack('>f',
                struct.pack('>i', int(format(0x7f7fffff,'d'))))[0]
    
    # return the min value of binary32
    # 2 ^ -126
    def get_min_binary32(self):
        return struct.unpack('>f',
                struct.pack('>i', int(format(0x00800000,'d'))))[0]
    
    def get_random_byte(self, colsize):
        return os.urandom(colsize)
    
    def get_random_char(self, colsize):
        return ''.join([random.choice(DummyInsert.DAT) for i in range(colsize)])
    
    def get_random_smallint(self):
        return random.randint(0, 2**16 / 2 - 1)
    
    def get_random_integer(self):
        return random.randint(0, 2**32 / 2 - 1)
    
    def get_random_long(self):
        return random.randint(0, 2**64 / 2 - 1)
    
    def get_random_real(self):
        return random.uniform(self.get_min_binary32(), self.get_max_binary32())
    
    def get_random_double(self):
        return random.uniform(sys.float_info.min, sys.float_info.max)
    
    def get_random_decimal(self, precision):
        return random.uniform(0, 10 ** precision)
    
    # return random date anytime after 2000/1/1
    def get_random_date(self):
        date_start = datetime.date(2000, 1, 1)
        date_end = datetime.date.today()
        date_diff = (date_end - date_start).days
        rand_diff = random.randint(0, date_diff)
    
        return date_start + datetime.timedelta(days=rand_diff)
    
    # return random time anytime between 00:00:00 and 23:59:59
    def get_random_time(self):
        hour = random.randint(0,23)
        minute = random.randint(0,59)
        second = random.randint(0,59)
    
        return datetime.time(hour, minute, second)
    
    # return random timestamp anytime after 2000/1/1 00:00:00
    def get_random_timestamp(self):
        start_ut = int(datetime.datetime(2000,1,1,0,0,0).strftime('%s'))
        now_ut = int(datetime.datetime.now().strftime('%s'))
        rand_ut = random.randint(start_ut, now_ut)
    
        return datetime.datetime.fromtimestamp(rand_ut)
    
    def get_sql(self, sqlfile):
        try:
            with open(sqlfile) as f:
                sql = f.read().strip("\n")
        except Exception as e:
            raise e
 
        return sql 
    
    def concat_list(self, g_list, l_list):
        g_list.append(l_list)
        return
    
    def set_param_list(self, param, l_list):
        return l_list.append(param)
        
if __name__ == '__main__':
    di = DummyInsert()
    di.main()

