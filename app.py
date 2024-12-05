import random
from flask import Flask, render_template, redirect, url_for, flash, request, session
from models import Book, Cart, User, Student, Staff, Faculty, CourseList, Order, OrderItem

app = Flask(__name__)
app.secret_key = 'supersecretkey'


@app.route('/')
def index():
    books = Book.get_all_books()
    return render_template('index.html', books=books)


@app.route('/search')
def search():
    query = request.args.get('query', '').strip().lower()
    
    if not query:
        flash("Please enter a search term.", "warning")
        return redirect(url_for('index'))

    matching_books = [book for book in Book.search_all_books() if query in book.title.lower() or query in book.author.lower()]

    if not matching_books:
        flash("No books found matching your search.", "info")

    return render_template('search_results.html', books=matching_books, query=query)


@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.get_book_by_id(book_id)
    role = session.get('role', 'guest')  #guest is default
    return render_template('book_detail.html', book=book, role=role)


@app.route('/add_to_cart/<int:book_id>')
def add_to_cart(book_id):
    book = Book.get_book_by_id(book_id)
    if not book:
        flash('Book not found!')
        return redirect(url_for('index'))
    cart = Cart()
    cart.add_item(book_id)
    flash(f'Added "{book.title}" to your cart!')
    return redirect(url_for('view_cart'))


@app.route('/cart')
def view_cart():
    cart = Cart()
    books = Book.get_books_by_ids(cart.get_items())
    return render_template('cart.html', books=books)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_email' not in session:
        flash('You are not logged in. Please sign in or proceed as a guest.', 'warning')
        return redirect(url_for('login_or_guest'))
    user_email = session['user_email']

    cart = Cart()
    cart_items = cart.get_items()  
    if not cart_items:
        flash('Your cart is empty. Please add items to your cart.', 'danger')
        return redirect(url_for('shop'))

    books = Book.get_books_by_ids(cart_items)
    total_cost = sum(book.price for book in books)
    delivery_methods = ['Shipping', 'In-store pickup', 'Digital download']

    if request.method == 'POST':
        delivery_method = request.form.get('delivery_method')
        payment_method = request.form.get('payment_method')

        payment_success = process_payment(payment_method)

        if payment_success:
            order = Order.create_order(user_email, total_cost)
            for book in books:
                OrderItem.create_order_item(order.order_id, book.id, 1, book.price) 
            cart.clear()
            return redirect(url_for('order_confirmation', order_id=order.order_id, total_cost=total_cost))

    return render_template('checkout.html', books=books, total_cost=total_cost, delivery_methods=delivery_methods)

def process_payment(payment_method):
    # fake payment processing
    if payment_method == 'Credit Card':
        return random.choice([True, False])  
    elif payment_method == 'PayPal':
        return random.choice([True, False])  
    elif payment_method == 'University Account':
        return random.choice([True, False])  
    return False

@app.route('/order_confirmation/<int:order_id>', methods=['GET'])
def order_confirmation(order_id):
    order = Order.get_order_by_id(order_id)
    
    if not order:
        flash('Order not found', 'danger')
        return redirect(url_for('index'))

    order_items = OrderItem.get_order_items_by_order_id(order_id)

    books = []
    for item in order_items:
        book = Book.get_book_by_id(item.book_id)  
        books.append({
            'title': book.title,
            'author': book.author,
            'price': book.price,
            'quantity': item.quantity,
        })

    total_cost = order.total_amount

    return render_template('order_confirmation.html', order=order, books=books, total_cost=total_cost)


# STAFF - book management routes
@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if session.get('role') != 'staff':
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('index'))

    book = Book.get_book_by_id(book_id)
    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        price = request.form['price']

        Staff.update_book(book_id, title, author, price)
        flash('Book updated successfully.', 'success')
        return redirect(url_for('index'))

    return render_template('edit_book.html', book=book)


@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    if session.get('role') != 'staff':
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('index'))

    Staff.delete_book(book_id)
    flash('Book deleted successfully.', 'success')
    return redirect(url_for('index'))


# FACULTY - course list management routes
@app.route('/add_to_course_list/<int:book_id>', methods=['GET', 'POST'])
def add_to_course_list(book_id):
    if session.get('role') != 'faculty':
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        course_list_id = request.form['course_list_id']
        Faculty.add_book_to_course_list(course_list_id, book_id)
        flash('Book added to course list successfully.', 'success')
        return redirect(url_for('book_detail', book_id=book_id))

    course_lists = CourseList.get_all_course_lists()
    return render_template('add_to_course_list.html', book_id=book_id, course_lists=course_lists)

@app.route('/remove_from_course_list/<int:course_list_id>/<int:book_id>', methods=['POST'])
def remove_from_course_list(course_list_id, book_id):
    if session.get('role') != 'faculty':
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('index'))

    Faculty.remove_book_from_course_list(course_list_id, book_id)
    flash('Book removed from course list successfully.', 'success')
    return redirect(url_for('manage_course_list', course_list_id=course_list_id))

@app.route('/create_course_list', methods=['GET', 'POST'])
def create_course_list():
    if 'user_email' not in session or session['role'] != 'faculty':
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        professor_email = session['user_email']
        professor_name = session.get('user_name')  
        course_title = request.form['course_title']
        department = request.form['department']
        course_number = request.form['course_number']

        CourseList.create_course_list(professor_email, professor_name, course_title, department, course_number)

        flash('Course list created successfully!', 'success')
        return redirect(url_for('manage_courses')) 

    return render_template('create_course_list.html')

@app.route('/manage_course_list/<int:course_list_id>', methods=['GET'])
def manage_course_list(course_list_id):
    if session.get('role') != 'faculty':
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('index'))

    books = CourseList.get_course_list_books(course_list_id)
    course_list = CourseList.get_course_list_by_id(course_list_id) 

    if not course_list:
        flash('Course list not found.', 'danger')
        return redirect(url_for('manage_courses'))

    return render_template('manage_course_list.html', books=books, course_list=course_list)

@app.route('/manage_courses')
def manage_courses():
    if 'user_email' not in session or session['role'] != 'faculty':
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('index'))

    course_lists = CourseList.get_course_lists_by_professor(session['user_email'])
    return render_template('manage_courses.html', course_lists=course_lists)


#Account routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        user = User.find_by_email(email)
        
        if user:
            session['user_email'] = user.email
            session['user_name'] = user.name
            session['role'] = user.status
            flash('Login successful.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    user = User.find_by_email(session['user_email'])
    role = session.get('role')
    print(role)
    if request.method == 'POST':
        new_name = request.form['name']
        new_address = request.form['address']
        new_department = request.form.get('department')
        user.update_profile(new_name, new_address, new_department)
        session['user_name'] = new_name
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user, role=role)


#order routes
@app.route('/order/<int:order_id>')
def order_details(order_id):
    order = Order.get_order_by_id(order_id)
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('my_orders'))

    order_items = OrderItem.get_order_items_by_order_id(order_id)
    books = []
    for item in order_items:
        book = Book.get_book_by_id(item.book_id)  
        if book:
            books.append({
                'title': book.title,
                'author': book.author,
                'price': book.price,
                'quantity': item.quantity,
                'order_item_id': item.order_item_id
            })
    
    returnable_items = {
        book['order_item_id']: OrderItem.is_returnable(book['order_item_id'])
        for book in books
    }

    total_cost = sum(book['price'] * book['quantity'] for book in books)

    return render_template(
        'order_details.html', 
        order=order, 
        books=books, 
        total_cost=total_cost, 
        returnable_items=returnable_items
    )

@app.route('/my_orders')
def my_orders():
    if 'user_email' not in session:
        flash('You need to be logged in to view your orders.', 'danger')
        return redirect(url_for('login'))

    user_email = session['user_email']
    orders = Order.get_orders_by_user_email(user_email)
    
    return render_template('my_orders.html', orders=orders)

@app.route('/return_book/<int:order_item_id>', methods=['GET', 'POST'])
def return_book(order_item_id):
    order_item = OrderItem.get_order_items_by_order_id(order_item_id)

    if not OrderItem.is_returnable(order_item_id):
        flash('The return window has expired. You cannot return this item.', 'danger')
        return redirect(url_for('my_orders'))

    if request.method == 'POST':
        OrderItem.request_return(order_item_id)
        flash('Your return request has been successfully submitted. A return label has been generated.', 'success')
        return redirect(url_for('my_orders'))

    return render_template('return_book.html', order_item=order_item)


if __name__ == '__main__':
    app.run(debug=True)
