import sqlite3
from flask import session
from datetime import datetime, timedelta


class Book:
    DB_PATH = 'bookstore.db'

    def __init__(self, id, isbn, title, author, price, cover_url=None):
        self.id = id
        self.isbn = isbn
        self.title = title
        self.author = author
        self.price = float(price)
        self.cover_url = cover_url or "no-cover-available.png"

    @classmethod
    def get_connection(cls):
        return sqlite3.connect(cls.DB_PATH)

    @classmethod
    def get_all_books(cls):
        with cls.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute('SELECT * FROM books').fetchall()
            return [
                cls(row['id'], row['isbn'], row['title'], row['author'], row['price'], row['cover_url'])
                for row in rows
            ]

    @classmethod
    def get_book_by_id(cls, book_id):
        with cls.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
            if row:
                return cls(row['id'], row['isbn'], row['title'], row['author'], row['price'], row['cover_url'])
        return None

    @classmethod
    def get_books_by_ids(cls, book_ids):
        if not book_ids:
            return []
        with cls.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            query = 'SELECT * FROM books WHERE id IN ({})'.format(','.join('?' * len(book_ids)))
            rows = conn.execute(query, book_ids).fetchall()
            return [
                cls(row['id'], row['isbn'], row['title'], row['author'], row['price'], row['cover_url'])
                for row in rows
            ]

    @classmethod
    def search_all_books(cls):
        with cls.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM books").fetchall()
            return [
                cls(row['id'], row['isbn'], row['title'], row['author'], row['price'], row['cover_url'])
                for row in rows
            ]

    def is_on_course_list(self):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute('SELECT 1 FROM course_list_books WHERE book_id = ?', (self.id,)).fetchone()
            return row is not None

    def get_course_lists(self):
        with CourseList.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT cl.id, cl.department || ' ' || cl.course_number AS name, cl.course_title, 
                cl.professor, cl.professor_name 
                FROM course_lists cl
                JOIN course_list_books clb ON cl.id = clb.course_list_id
                WHERE clb.book_id = ?
            """, (self.id,)).fetchall()
            return [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "course_title": row["course_title"],
                    "professor": row["professor"],
                    "professor_name": row["professor_name"]
                }
                for row in rows
            ]


class Cart:
    def __init__(self):
        if 'cart' not in session:
            session['cart'] = []

    def add_item(self, book_id):
        session['cart'].append(book_id)
        session.modified = True

    def get_items(self):
        return session.get('cart', [])

    def clear(self):
        session['cart'] = []
        session.modified = True


class User:
    DB_PATH = 'bookstore.db'

    @classmethod
    def get_connection(cls):
        return sqlite3.connect(cls.DB_PATH)

    def __init__(self, email, name, status=None, department=None, address=None):
        self.email = email
        self.name = name
        self.status = status
        self.department = department
        self.address = address

    def is_student(self):
        return self.status == 'student'

    def is_staff(self):
        return self.status == 'staff'

    def is_faculty(self):
        return self.status == 'faculty'

    def update_profile(self, new_name, new_address, new_department):
        self.name = new_name
        self.address = new_address
        self.department = new_department
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE users SET name = ?, address = ?, department = ? WHERE email = ?",
                (new_name, new_address, new_department, self.email)
            )

    @classmethod
    def find_by_email(cls, email):
        with cls.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            if row:
                return cls(
                    email=row['email'],
                    name=row['name'],
                    status=row['status'],
                    department=row['department'],
                    address=row['address']
                )
        return None

    @classmethod
    def authenticate(cls, email):
        user = cls.find_by_email(email)
        if user:
            return user
        return None

    def set_session(self):
        session['username'] = self.email
        session['role'] = self.status
        session['user_name'] = self.name


class Student(User):
    def __init__(self, email, name, status='student', department=None, address=None):
        super().__init__(email, name, status, department, address)


class Staff(User):
    def __init__(self, email, name, status='staff', department=None, address=None):
        super().__init__(email, name, status, department, address)

    @staticmethod
    def add_book(title, author, price):
        with Book.get_connection() as conn:
            conn.execute('INSERT INTO books (title, author, price) VALUES (?, ?, ?)', (title, author, price))

    @staticmethod
    def delete_book(book_id):
        with Book.get_connection() as conn:
            conn.execute('DELETE FROM books WHERE id = ?', (book_id,))

    @staticmethod
    def update_book(book_id, title, author, price):
        with Book.get_connection() as conn:
            conn.execute(
                'UPDATE books SET title = ?, author = ?, price = ? WHERE id = ?',
                (title, author, price, book_id)
            )


class Faculty(User):
    def __init__(self, email, name, status='faculty', department=None, address=None):
        super().__init__(email, name, status, department, address)

    def add_department(self, new_department):
        self.department = new_department
        self._update_database('department', new_department)

    def _update_database(self, field, value):
        with self.get_connection() as conn:
            conn.execute(f"UPDATE users SET {field} = ? WHERE email = ?", (value, self.email))

    @staticmethod
    def add_book(title, author, price):
        with Book.get_connection() as conn:
            conn.execute('INSERT INTO books (title, author, price) VALUES (?, ?, ?)', (title, author, price))

    @staticmethod
    def add_book_to_course_list(course_list_id, book_id):
        CourseList.add_book_to_course_list(course_list_id, book_id)

    @staticmethod
    def remove_book_from_course_list(course_list_id, book_id):
        CourseList.remove_book_from_course_list(course_list_id, book_id)


class CourseList:
    DB_PATH = 'bookstore.db'

    def __init__(self, id, professor, course_title, department, course_number, name=None):
        self.id = id
        self.professor = professor
        self.course_title = course_title
        self.department = department
        self.course_number = course_number
        self.name = name or f"{department} {course_number}"

    @classmethod
    def get_connection(cls):
        return sqlite3.connect(cls.DB_PATH)

    @classmethod
    def create_course_list(cls, professor, professor_name, course_title, department, course_number):
        with cls.get_connection() as conn:
            name = f"{department} {course_number}"
            conn.execute(
                "INSERT INTO course_lists (professor, professor_name, course_title, department, course_number) VALUES (?, ?, ?, ?, ?)",
                (professor, professor_name, course_title, department, course_number)
            )


    @classmethod
    def add_book_to_course_list(cls, course_list_id, book_id):
        with cls.get_connection() as conn:
            conn.execute(
                "INSERT INTO course_list_books (course_list_id, book_id) VALUES (?, ?)",
                (course_list_id, book_id)
            )

    @classmethod
    def remove_book_from_course_list(cls, course_list_id, book_id):
        with cls.get_connection() as conn:
            conn.execute(
                "DELETE FROM course_list_books WHERE course_list_id = ? AND book_id = ?",
                (course_list_id, book_id)
            )

    @classmethod
    def get_all_course_lists(cls):
        with cls.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute('SELECT * FROM course_lists').fetchall()
            return [
                cls(row['id'], row['professor'], row['course_title'], row['department'], row['course_number'], row['department'] + ' ' + row['course_number'])
                for row in rows
            ]

    @classmethod
    def get_course_list_by_id(cls, course_list_id):
        with cls.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute('SELECT * FROM course_lists WHERE id = ?', (course_list_id,)).fetchone()
            if row:
                return cls(row['id'], row['professor'], row['course_title'], row['department'], row['course_number'], row['department'] + ' ' + row['course_number'])
        return None

    @classmethod
    def get_course_lists_by_professor(cls, professor_name):
        with cls.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM course_lists WHERE professor = ?",
                (professor_name,)
            ).fetchall()
            return [
                cls(row['id'], row['professor'], row['course_title'], row['department'], row['course_number'], row['department'] + ' ' + row['course_number'])
                for row in rows
            ]
        
    @classmethod
    def get_course_list_books(cls, course_list_id):
        conn = cls.get_connection()
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT b.id, b.isbn, b.title, b.author, b.price, b.cover_url "
            "FROM books b "
            "JOIN course_list_books clb ON b.id = clb.book_id "
            "WHERE clb.course_list_id = ?",
            (course_list_id,)
        ).fetchall()
        conn.close()
        return [
            Book(row['id'], row['isbn'], row['title'], row['author'], row['price'], row['cover_url'])
            for row in rows
        ]



class Order:
    DB_PATH = 'bookstore.db'

    def __init__(self, order_id, user_email, status='pending', total_amount=0, created_at=None):
        self.order_id = order_id
        self.user_email = user_email
        self.status = status
        self.total_amount = total_amount
        self.created_at = created_at or datetime.now()

    @classmethod
    def get_connection(cls):
        return sqlite3.connect(cls.DB_PATH)

    @classmethod
    def create_order(cls, user_email, total_amount):
        with cls.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO orders (user_email, total_amount, status) VALUES (?, ?, ?)",
                (user_email, total_amount, 'pending')
            )
            order_id = cursor.lastrowid
            return cls(order_id, user_email, status='Pending', total_amount=total_amount)

    @classmethod
    def get_order_by_id(cls, order_id):
        with cls.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,)).fetchone()
            if row:
                return cls(row['order_id'], row['user_email'], row['status'], row['total_amount'], row['created_at'])
        return None
    
    @classmethod
    def get_orders_by_user_email(cls, user_email):
        with cls.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute('SELECT * FROM orders WHERE user_email = ?', (user_email,)).fetchall()
            return [
                cls(row['order_id'], row['user_email'], row['status'], row['total_amount'], row['created_at'])
                for row in rows
            ]


class OrderItem:
    DB_PATH = 'bookstore.db'

    def __init__(self, order_item_id, order_id, book_id, quantity, price):
        self.order_item_id = order_item_id
        self.order_id = order_id
        self.book_id = book_id
        self.quantity = quantity
        self.price = price

    @classmethod
    def get_connection(cls):
        return sqlite3.connect(cls.DB_PATH)

    @classmethod
    def create_order_item(cls, order_id, book_id, quantity, price):
        with cls.get_connection() as conn:
            conn.execute(
                "INSERT INTO order_items (order_id, book_id, quantity, price) VALUES (?, ?, ?, ?)",
                (order_id, book_id, quantity, price)
            )

    @classmethod
    def get_order_items_by_order_id(cls, order_id):
        with cls.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,)).fetchall()
            return [
                cls(row['order_item_id'], row['order_id'], row['book_id'], row['quantity'], row['price'])
                for row in rows
            ]
        
    @classmethod
    def request_return(cls, order_item_id):
        with cls.get_connection() as conn:
            conn.execute(
                "UPDATE order_items SET return_requested = ?, return_date = ? WHERE order_item_id = ?",
                (True, datetime.now(), order_item_id)
            )

    @classmethod
    def is_returnable(cls, order_item_id): #Return window is 30 days
        with cls.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT o.created_at, oi.return_requested FROM order_items oi "
                "JOIN orders o ON oi.order_id = o.order_id WHERE oi.order_item_id = ?",
                (order_item_id,)
            ).fetchone()
            if row:
                order_date = datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S')
                return_requested = row['return_requested']
                if return_requested:
                    return False
                return datetime.now() - order_date <= timedelta(days=30)
        return False
