import sqlite3

class DatabaseInterface (object):
    def __init__ (self, database):
        if database != ":memory:":
            if '.db' not in database: 
                database += '.db'

        self.conn = sqlite3.connect(database)
        self.c = self.conn.cursor()

    def execute_query (self, q):
        self.c.execute(q) 

        return self.c.fetchall()

    def add_primary_table (self, table_name, primaryKey, primaryKeyType):
        if self.table_exists(table_name):
            print ("Table Already Exists")
            return

        self.c.execute("CREATE TABLE {tn} ({pk} {pt} PRIMARY KEY)"\
                        .format(tn=table_name, 
                                pk=primaryKey, 
                                pt=primaryKeyType))

        self.conn.commit()

    def add_related_table (self, table_name, foreignKey, foreignKeyType,\
                            primaryTable):
        if self.table_exists(table_name):
            print ("Table Already Exists")
            return

        self.c.execute("CREATE TABLE {tn} ({fk} {ft} REFERENCES {pt}({fk}))"\
                        .format(tn=table_name, 
                                fk=foreignKey, 
                                ft=foreignKeyType, 
                                pt=primaryTable))

        self.conn.commit()

    def add_column (self, table_name, attr, attrType):
        if not self.table_exists(table_name):
            print ("Table Doesn't Exists")
            return

        self.c.execute("ALTER TABLE {tn} ADD COLUMN '{a}' {t}"\
                        .format(tn=table_name, a=attr, t=attrType))

        self.conn.commit()

    def insert_row (self, table_name, row):
        if len(row) != len(self.get_columns(table_name)):
            print ("row/table length mismatch")
            return 

        self.c.execute("INSERT INTO {tn} VALUES {r}"
                        .format(tn=table_name, r=row))
        self.conn.commit()

    def bulk_insert_row(self, table_name, rows):
        if len(rows[0]) != len(self.get_columns(table_name)):
            print ("row/table length mismatch")
            return 

        for i, row in enumerate(rows):
            self.c.execute("INSERT INTO {tn} VALUES {r}"
                            .format(tn=table_name, r=row))
            if i % 200 == 0: 
                self.conn.commit()
        
        self.conn.commit()

    def bulk_insert_row_txt(self, rows):
        for i, row in enumerate(rows):
            self.c.execute("INSERT INTO ArticleTXT VALUES (?, ?, ?, ?)", row)
            if i % 200 == 0: 
                self.conn.commit()
        
        self.conn.commit()

    def delete_table (self, table_name): 
        if not self.table_exists(table_name):
            print ("Table Doesn't Exists")
            return

        self.c.execute('DROP TABLE {tn}' .format(tn=table_name))

        self.conn.commit()

    # Retrieves table and database information
    def get_tables (self): 
        y = self.c.execute("SELECT name FROM sqlite_master WHERE type='table'")

        table_names = list(map(lambda x: x[0], y))

        return table_names

    def get_columns (self, table_name):
        if not self.table_exists(table_name):
            print ("Table Doesn't Exists")
            return

        # Pragma table data stored as 
        # (id, name, type, notnull, default_value, primary_key)
        y = self.c.execute('PRAGMA TABLE_INFO({})'.format(table_name))

        # Grab the name of each column
        column_names = [tup[1] for tup in self.c.fetchall()]

        return column_names

    def print_schema (self): 
        for table in self.get_tables():
            print (table + " " + str(self.get_columns(table)))
        
    def table_exists (self, table_name):
        """Checks if a given table is in the database"""
        if table_name in self.get_tables():
            return True
        else: 
            return False
