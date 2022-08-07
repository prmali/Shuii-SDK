import psycopg2
from config import config


class DatabaseClient:
    def __init__(self):
        self.commands = []

    def queue_command(self, command):
        self.commands.append(command)

    def queue_commands(self, commands):
        for command in commands:
            self.queue_command(command)

    def execute(self):
        connection = None
        try:
            # read the connection parameters
            params = config()
            # connect to the PostgreSQL server
            connection = psycopg2.connect(**params)
            cursor = connection.cursor()
            # create table one by one
            for command in tuple(self.commands):
                cursor.execute(self.commands.pop(0))
            # close communication with the PostgreSQL database server
            cursor.close()
            # commit the changes
            connection.commit()
            self.commands = []
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if connection is not None:
                connection.close()

    @staticmethod
    def prep_data(table_name, columns, data):
        statement = f'INSERT INTO {table_name} ({",".join(columns)}) VALUES \n'

        # ",".join(entry)
        for entry in data:
            statement += f'{str(entry)},\n'

        return statement[:-2]

    @staticmethod
    def query(statement):
        connection = None
        data = None
        try:
            params = config()
            connection = psycopg2.connect(**params)
            cursor = connection.cursor()
            cursor.execute(statement)
            data = cursor.fetchall()
            connection.commit()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if connection is not None:
                connection.close()

            return data
