# ITEC6410_Bookstore
MGA ITEC 6410's final project to create an online bookstore prototype

Launch:
To start the application, run app.py from the terminal using “python3 app.py” or in your preferred IDE. Port 5000 must be available for the app to launch.


In your browser, go to http://127.0.0.1:5000 to interact with the interface.


Certain options are limited based on the user’s role (student, staff, faculty). To test those, login using one of the following email addresses and then navigate to a book page or http://127.0.0.1:5000/profile. 
bisky.forbes@mga.edu - Student
random.student@mga.edu - Student
dr.faculty@mga.edu - Faculty
Removing a book from a Course List
Creating a Course List
Adding a Book to a Course List
aloethecat@bookstore.com -Staff
Removing a Book from the Catalog
Editing Book information
Structure Overview:
App.py: This application uses Flask to deliver a browser-based interface.
Setup.py: The application comes with a sqlite database already setup in bookstore.db. This supplies test data such as books, accounts, and course lists.
To reset the database, run setup.py in the terminal. This will reset the database to the sample data in the setup.py file. You can replace this with your own sample data.
Models.py: The classes used are all contained in this folder as recommended for Python. Classes include:
Book
Cart
User
Student
Staff
Faculty
CourseList
Order
OrderItem
