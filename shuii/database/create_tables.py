import psycopg2
from config import config
from DatabaseClient import DatabaseClient

commands = (
    """
        DROP TABLE IF EXISTS networks CASCADE;
        DROP TABLE IF EXISTS collections CASCADE;
        DROP TABLE IF EXISTS traits CASCADE;
        DROP TABLE IF EXISTS tokens CASCADE;
        DROP TABLE IF EXISTS attributes CASCADE;
    """,
    """
        CREATE TABLE networks (
            network_id SERIAL PRIMARY KEY,
            network_name VARCHAR(255) NOT NULL UNIQUE,
            network_symbol VARCHAR(255) NOT NULL UNIQUE
        )
    """,
    """
    CREATE TABLE collections (
        collection_id SERIAL PRIMARY KEY,
        network_id INTEGER NOT NULL,
        collection_address VARCHAR(255) NOT NULL,
        collection_name VARCHAR(255) NOT NULL,
        collection_symbol VARCHAR(255),
        total_supply INTEGER NOT NULL,
        UNIQUE (network_id, collection_address),
        FOREIGN KEY (network_id)
            REFERENCES networks (network_id)
            ON UPDATE CASCADE ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE traits (
        trait_id SERIAL PRIMARY KEY,
        collection_id INTEGER NOT NULL,
        trait_type VARCHAR(255) NOT NULL,
        value VARCHAR(255),
        count INTEGER NOT NULL,
        weight FLOAT NOT NULL,
        UNIQUE (collection_id, trait_type, value),
        FOREIGN KEY (collection_id)
            REFERENCES collections (collection_id)
            ON UPDATE CASCADE ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE tokens (
        token_id SERIAL PRIMARY KEY,
        collection_id INTEGER NOT NULL,
        id INTEGER NOT NULL,
        rank INTEGER NOT NULL,
        weight FLOAT NOT NULL,
        UNIQUE(collection_id, id),
        FOREIGN KEY (collection_id)
            REFERENCES collections (collection_id)
            ON UPDATE CASCADE ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE attributes (
        attribute_id SERIAL PRIMARY KEY,
        collection_id INTEGER NOT NULL,
        token_id INTEGER NOT NULL,
        trait_id INTEGER NOT NULL,
        FOREIGN KEY (collection_id)
            REFERENCES collections (collection_id)
            ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (token_id)
            REFERENCES tokens (token_id)
            ON UPDATE CASCADE ON DELETE CASCADE
    )
    """
)

client = DatabaseClient()
client.queue_commands(commands)
client.execute()

# def create_tables():
#     """ create tables in the PostgreSQL database"""

#     commands = (
#         """
#         CREATE TABLE vendors (
#             vendor_id SERIAL PRIMARY KEY,
#             vendor_name VARCHAR(255) NOT NULL
#         )
#         """,
#         """ CREATE TABLE parts (
#                 part_id SERIAL PRIMARY KEY,
#                 part_name VARCHAR(255) NOT NULL
#                 )
#         """,
#         """
#         CREATE TABLE part_drawings (
#                 part_id INTEGER PRIMARY KEY,
#                 file_extension VARCHAR(5) NOT NULL,
#                 drawing_data BYTEA NOT NULL,
#                 FOREIGN KEY (part_id)
#                 REFERENCES parts (part_id)
#                 ON UPDATE CASCADE ON DELETE CASCADE
#         )
#         """,
#         """
#         CREATE TABLE vendor_parts (
#                 vendor_id INTEGER NOT NULL,
#                 part_id INTEGER NOT NULL,
#                 PRIMARY KEY (vendor_id , part_id),
#                 FOREIGN KEY (vendor_id)
#                     REFERENCES vendors (vendor_id)
#                     ON UPDATE CASCADE ON DELETE CASCADE,
#                 FOREIGN KEY (part_id)
#                     REFERENCES parts (part_id)
#                     ON UPDATE CASCADE ON DELETE CASCADE
#         )
#         """)
#     conn = None
#     try:
#         # read the connection parameters
#         params = config()
#         # connect to the PostgreSQL server
#         conn = psycopg2.connect(**params)
#         cur = conn.cursor()
#         # create table one by one
#         for command in commands:
#             cur.execute(command)
#         # close communication with the PostgreSQL database server
#         cur.close()
#         # commit the changes
#         conn.commit()
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)
#     finally:
#         if conn is not None:
#             conn.close()


# if __name__ == '__main__':
#     create_tables()
