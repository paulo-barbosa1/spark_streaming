import psycopg2
from config import config


def create_tables():
    """ create tables in the PostgreSQL database"""
    query = (
        """
        CREATE TABLE public.retail
        (
            id bigserial NOT NULL,
            Invoice character varying(20),
            InvoiceDate timestamp,
            CustomerID character varying(10),
            Country character varying(20),
            Cancelled character varying(1),
            total_amount real,
            PRIMARY KEY (id)
        );

        ALTER TABLE public.retail
            OWNER to admin;
        """,
        )
    conn = None
    try:
        params = config()
        conn = psycopg2.connect("host=localhost port=5416 dbname=orders user=admin password=admin")
        cur = conn.cursor()
        for command in query:
            cur.execute(command)
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    create_tables()