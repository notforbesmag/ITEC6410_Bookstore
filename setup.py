import sqlite3

def create_database():
    try:
        conn = sqlite3.connect('bookstore.db')
        cursor = conn.cursor()

        # Create the books table if it does not exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isbn TEXT NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                price REAL NOT NULL,
                cover_url TEXT
            )
        ''')

        # Sample books
        sample_books = [
            ['978-0-321-89761-2', 'Introduction to Algorithms', 'Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest', 79.99, 'introduction_to_algorithms_cover.jpg'],
            ['978-0-134-68599-1', 'Engineering Mechanics: Dynamics', 'J.L. Meriam, L.G. Kraige', 47.99, 'engineering_mechanics_dynamics_cover.jpg'],
            ['978-0-073-38309-5', 'Fundamentals of Physics', 'David Halliday, Robert Resnick, Jearl Walker', 99.99, 'fundamentals_of_physics_cover.jpg'],
            ['978-0-123-74751-2', 'Biology', 'Neil A. Campbell, Jane B. Reece', 160.00, 'biology_cover.jpg'],
            ['978-0-071-61268-0', 'Physics for Scientists and Engineers', 'Douglas C. Giancoli', 108.50, 'physics_for_scientists_and_engineers_cover.jpg'],
            ['978-0-134-70609-2', 'Discrete Mathematics and Its Applications', 'Kenneth H. Rosen', 118.00, 'discrete_mathematics_cover.jpg'],
            ['978-0-321-92056-8', 'Linear Algebra and Its Applications', 'David C. Lay', 72.99, 'linear_algebra_cover.jpg'],
            ['978-1-305-24848-4', 'Calculus: Early Transcendentals', 'James Stewart', 122.00, None],
            ['978-0-133-75757-3', 'Introduction to Probability', 'Dimitri P. Bertsekas, John N. Tsitsiklis', 99.99, 'introduction_to_probability_cover_573.jpg'],
            ['978-1-138-36991-7', 'Introduction to Probability', 'Joseph K. Blitzstein, Jessica Hwang', 89.99, 'introduction_to_probability_cover_917.jpg'],
            ['978-1-118-53818-7', 'Engineering Fluid Mechanics', 'Donald F. Young', 78.50, None],
            ['978-0-262-03384-8', 'Introduction to the Theory of Computation', 'Michael Sipser', 97.99, 'theory_of_computation_cover.jpg'],
            ['978-0-674-53099-0', 'The Feynman Lectures on Physics, Vol 1', 'Richard P. Feynman', 55.00, 'feynman_lectures_cover_990.jpg'],
            ['978-0-674-53099-1', 'The Feynman Lectures on Physics, Vol 2', 'Richard P. Feynman', 55.00, 'feynman_lectures_cover_991.jpg'],
            ['978-0-674-53099-2', 'The Feynman Lectures on Physics, Vol 3', 'Richard P. Feynman', 55.00, 'feynman_lectures_cover_992.jpg'],
        ]

        for sample in sample_books:
            cursor.execute("INSERT OR IGNORE INTO books (isbn, title, author, price, cover_url) VALUES (?,?,?,?,?)", sample)

        conn.commit()

        # Create the users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                department TEXT,
                address TEXT
            )
        ''')

        # Sample users
        sample_users = [
            ['soudea.forbes@mga.edu', 'Soudea', 'student', None, "123 Lane Lane, Dublin GA 31021"],
            ['alekya.thalakoti@mga.edu', 'Alekya', 'student', None, None],
            ['joobum.kim@mga.edu', 'Dr. Kim', 'faculty', 'ITEC', "MGA Campus, Macon, GA, 31201"],
            ['aloethecat@bookstore.com', 'Aloe', 'staff', None, None]
        ]
        for sample in sample_users:
            cursor.execute("INSERT OR IGNORE INTO users (email, name, status, department,address) VALUES (?,?,?,?,?)", sample)

        conn.commit()

        # Create the orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                total_amount REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # Create the order_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                return_requested BOOLEAN DEFAULT 0,
                return_date DATETIME,
                FOREIGN KEY (order_id) REFERENCES orders (order_id),
                FOREIGN KEY (book_id) REFERENCES books (id)
            );
        ''')

        # Create course reading list table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS course_lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                professor TEXT NOT NULL,
                professor_name TEXT NOT NULL,
                course_title TEXT NOT NULL,
                department TEXT NOT NULL,
                course_number TEXT NOT NULL
            )
        ''')

        # Create course list books table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS course_list_books (
                course_list_id INTEGER,
                book_id INTEGER,
                PRIMARY KEY (course_list_id, book_id),
                FOREIGN KEY (course_list_id) REFERENCES course_lists(id),
                FOREIGN KEY (book_id) REFERENCES books(id)
            )
        ''')

        # Sample course lists
        sample_course_lists = [
            ['joobum.kim@mga.edu', 'Dr. Kim', 'Data Structures', 'ITEC', 3500],
            ['nina.thomas@mga.edu', 'Dr. Nina Thomas', 'Digital Logic Design', 'EE', 2001],
            ['alice.jones@mga.edu', 'Dr. Alice Jones', 'Calculus I', 'MATH', 1101]
        ]

        for sample in sample_course_lists:
            cursor.execute("INSERT OR IGNORE INTO course_lists (professor, professor_name, course_title, department, course_number) VALUES (?,?,?,?,?)", sample)

        sample_course_list_books = [
            [1, 1], 
            [1, 2], 
            [2, 1], 
        ]

        for sample in sample_course_list_books:
            cursor.execute("INSERT OR IGNORE INTO course_list_books (course_list_id, book_id) VALUES (?, ?)", sample)

        conn.commit()

        print("Database and tables created successfully!")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_database()
