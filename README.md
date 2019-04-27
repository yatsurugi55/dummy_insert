# Overview 
 
 dummy_insert is tool that inserts dummy data to db2 database for python.  
 This tool generates appropriate dummy data and insert them to the table following  
 the sql file you specified.

# Description

 This tool generates appropriate dummy data to match the table columns.  
 The set of the column types and the dummy value is below.  

 - CHAR(n)
    random n characters

 - VARCHAR(n)
    random n characters

 - SMALLINT
    a random integer between 0 and 2^15 - 1

 - INTEGER
    a random integer between 0 and 2^31 - 1

 - BIGINT
    a random integer between 0 and 2^63 - 1

 - REAL
    a random decimal between minimum of positive binary32 and maximum binary32

 - FLOAT
    a random decimal between minimum of positive binary64 and maximum binary64
  
 - DOUBLE
    a random decimal between minimum of positive binary64 and maximum binary64

 - DECIMAL(m, n)
    a random decimal between 0 and 10 * (m - n)

 - NUMERIC(m, n)
    a random decimal between 0 and 10 * (m - n)

 - DATE
    a random date between 2000/1/1 and the execution date

 - TIME
    a random time between 00:00:00 and 23:59:59

 - TIMESTAMP
    a random timestamp between 2000/1/1 00:00:00 and the execution datetime

 - BLOB(n)
    random n bytes

 - CLOB(n)
    random n characters
    
# Demo

 ## 1. All dummy data columns

 `$ cat insert.sql`  
 `INSERT INTO EMPLOYEE VALUES (?, ?, ?, ?, ?, ?, ?)`

 `$ python dummy_insert.py -d TESTDB -f insert.sql -r 5`

 `$ db2 "select * from EMPLOYEE"`

    EMPNO  NAME            WORKDEPT HIREDATE   EDLEVEL SALARY      BONUS  
    ------ --------------- -------- ---------- ------- ----------- -----------  
    LUmgkB UKjE3aIlQng9hIR dKX      2017-03-30   15396  3795350.65  5271653.16  
    iG9u4z UDqnPq5IBCk8oek 2xh      2012-02-09   12280  9535687.58  7452416.87  
    crqdKq JjGFqtAPFWWWjDb EX2      2017-06-16   25585  3580199.77  3314787.84  
    pkU65i sonIxHJMynZO8Kn 87B      2008-03-07   29357  6566233.61  7845889.90  
    dcAAbf G9hInP6Yne8O2TE kDu      2015-10-03    9281  3719330.84  7481345.00  


 ## 2. With sequence object column  
 
 `$ cat insert.sql`  
 `INSERT INTO EMPLOYEE VALUES (NEXT VALUE FOR seq_empno, ?, ?, ?, ?, ? ,?)`  

 `$ python dummy_insert.py -d TESTDB -f insert.sql -r 10`

 `$ db2 "select * from EMPLOYEE"`

    EMPNO  NAME            WORKDEPT HIREDATE   EDLEVEL SALARY      BONUS  
    ------ --------------- -------- ---------- ------- ----------- -----------  
    0      wQ6ZfLFYnRkv8Dv nZH      2004-06-12     884  7243451.42   746280.88  
    1      QWSA3CjMhS48iew 0Zp      2000-11-22   23228   694883.29  8727302.89  
    2      8z6oXiLD0ejCeyc 52g      2001-08-05   16840  3369529.05   685200.17  
    3      57MEHiABZuJlgve AfP      2015-08-31    9262  6423607.84  5383415.31  
    4      PCvVKpPinYSYo3y c5h      2004-02-14   15285  2491254.42  5888457.46  
    5      YjgpydMSuE1YtbT ANJ      2003-08-03    8835  1908574.31  8097953.25  
    6      HBb4CPTVOne3gbi bAq      2018-11-15   28498   403495.09  9514459.89  
    7      MWL4HUBxeiIZUWQ UPX      2000-10-06    8414  2999179.89  2046048.66  
    8      7NqHbN5rc2tqgk5 LNK      2014-08-10   20344  2263640.65  1883061.79  
    9      d7URwC47E9DD1jU 4P5      2018-02-10   28888  6119592.45   570743.94  


 ## 3. Bulk insert  
 This 1,000,000 insert example ran in 312 seconds in my environment.  
   
 `$ cat insert.sql`  
 `INSERT INTO EMPLOYEE VALUES (NEXT VALUE FOR seq_empno, ?, ?, ?, ?, ? ,?)`

 `$ python dummy_insert.py -d TESTDB -f insert.sql -r 1000000`  
 
 `$ db2 "select count(*) from EMPLOYEE"`
 
    1
    -----------
        1000000
    
 `$ db2 "select * from EMPLOYEE order by INTEGER(EMPNO)" | tail`
 
    999993 lJf2fkOtVLdt 8pr      2011-03-21    5410  1881059.41  9978670.79
    999994 U8xlY1ZU83fk CtZ      2015-12-23   25629  9939366.38   163365.14
    999995 NIGEcOn1FAju ZEa      2017-07-17   21347  9826046.86  5398803.83
    999996 TgdLAxGHBRl0 R4k      2010-01-09    9805  7114331.35  1997074.28
    999997 LGKVnqCm6vZU m0S      2013-06-24    7350  4040582.61  9101479.18
    999998 f2mZ7OAj9Q95 tEf      2012-09-19    9608  8481912.74   788261.46
    999999 px8b6uPNg4EU UKI      2003-11-13    8245  5424813.68  2262311.08
 
 
# Requirement

 python2.7, db2, ibm_db

# Usage

 usage: dummy_insert.py [-h] -d DBNAME -f INPUT_FILE [-r ROWS]

   - DBNAME  
       Your db2 database name

   - INPUT_FILE  
       The file of a insert sql with some parameter markers. And you can 
       set some sequence objects in your sql.

       ex)  
         - INSERT INTO TABLE1 VALUES (?, ?, ?, ?, ?)  
         - INSERT INTO TABLE2 VALUES (NEXT VALUE FOR seq_obj, ?, ?)  

   - ROWS  
       The row number you want to insert to db.
       (the transaction will execute commit each 1000 rows)
       
