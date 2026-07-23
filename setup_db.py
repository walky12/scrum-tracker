import psycopg2

def initialize_database():
    try:
        # Connect to your local PostgreSQL server
        connection = psycopg2.connect(
            dbname="scrum_tracker",
            user="postgres",
            password="Monkey",  # Replace with your actual PostgreSQL password
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()

        # Create the responsibilities table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS daily_responsibilities (
            id SERIAL PRIMARY KEY,
            assignment_date DATE NOT NULL,
            responsibility TEXT NOT NULL,
            area VARCHAR(100) NOT NULL,
            assigned_by VARCHAR(100) NOT NULL,
            assigned_to VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'daily_responsibilities' created successfully locally!")

    except Exception as error:
        print(f"Error while connecting to PostgreSQL: {error}")
        
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    initialize_database()