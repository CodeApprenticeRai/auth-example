import bcrypt
import mysql.connector
from getpass import getpass

CREATE_DB_SQL = "CREATE DATABASE IF NOT EXISTS main"
USE_MAIN_DB_SQL = "USE main"
CREATE_USERS_TABLE_SQL = "CREATE TABLE IF NOT EXISTS users (\
    id INT AUTO_INCREMENT PRIMARY KEY,\
    username VARCHAR(255) NOT NULL,\
    password VARCHAR(255) NOT NULL,\
    email VARCHAR(255) NOT NULL\
)"

class Application:
    def __init__(self):
        self._exit_program = False
        self.db_connection, self.db_cursor = self.setup_db()

        self.current_user = None
        self.UNALLOWED_USERNAME_CHARACTERS = set("~!@#$%^&*()_+=-|\\}{][\"';:,./<>?")
        
        #user sees menu1 if not logged in
        self.menu1 = {
            0 : ("Exit", self.exit_program),
            1 : ("Create New User", self.create_new_user),
            2 : ("Login", self.login)
        }

        #user sees menu2 if logged in
        self.menu2 = {
            0 : ("Exit", self.exit_program),
        }


    def exit_program(self):
        self._exit_program = True
        print("Thank you for using the app!")
        return None

    def setup_db(self):
        db_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="demo"
        )
            
        db_cursor = db_connection.cursor()
        db_cursor.execute(CREATE_DB_SQL)
        db_cursor.execute(USE_MAIN_DB_SQL)
        db_cursor.execute(CREATE_USERS_TABLE_SQL)
        
        return (db_connection, db_cursor)

    def username_is_valid(self, username):
        for letter in username:
            if letter in self.UNALLOWED_USERNAME_CHARACTERS:
                return False
        return True

    def username_is_available(self, username):
        #check if username already exists in db
        self.db_cursor.execute("SELECT username FROM users WHERE username = '{}' LIMIT 1".format(username))
        result = self.db_cursor.fetchall()
        if (len(result) > 0):
            print("Username '{}' is already taken".format(username))
            return False
        return True

    def create_new_user(self):
        requested_username = ""
        _username_is_valid = False
        _username_is_available = False

        # username must be valid and available to proceed to new user creation step
        while (
                (not _username_is_valid) or 
                (not _username_is_available)
            ):
            requested_username = input("Enter New Username:  ")

            _username_is_valid = self.username_is_valid(requested_username)

            if not _username_is_valid:
                print("Username can only contain alphanumeric charcters. Please try again.")
                continue
            
            _username_is_available = self.username_is_available(requested_username)
            

        
        password = getpass("Enter Password: ").encode() # password has no validation restrictions
        hash = bcrypt.hashpw(password, bcrypt.gensalt())

        
        # create new user in db
        self.db_cursor.execute(
            "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
            (requested_username, hash, "demo@email.com")
        )

        self.db_connection.commit()
        
        print("User {} was created.".format(requested_username))

        return None 

    def login(self):
        username = ""
        _username_is_valid = False
        
        while ((username == "") or (not _username_is_valid)):
            username = input("Enter Username: ")
            _username_is_valid = self.username_is_valid(username)
            if (not _username_is_valid):
                print('Username can only contain alphanumeric charcters. Please try again.')
        
        password = getpass("Enter Password: ").encode()
        
        self.db_cursor.execute(
            "SELECT username, password FROM users WHERE username = %s LIMIT 1",
            (username,)
        )

        results = self.db_cursor.fetchall()

        if (len(results) > 0):
            hash = results[0][1].encode()
            if bcrypt.checkpw(password, hash):
                print("You've successfully signed in")
                self.current_user = username
            else:
                print("Username / Password combination not found")
        else:
            print("Username / Password combination not found")

        return None

    def use_menu1(self):
        validated_choice = None

        while (validated_choice == None):
            user_choice = None

            #print menu1 options
            print("Please enter an integer corresponding to one of the following options:\n")
            for key in self.menu1:
                print("{} : {}".format(key, self.menu1[key][0]))
            
            # try to read user input
            try:
                user_choice = int(input("Choice: "))
            except ValueError:
                print("That was not a valid choice. Please try again.")
                continue

            
            if user_choice in self.menu1:
                validated_choice = user_choice
            else:
                print("That was not a valid choice.")
                continue
        
        # perform selected choice
        self.menu1[validated_choice][1]()
        return None

    def use_menu2(self):
        print("Currently logged in as {}".format(self.current_user))
        
        validated_choice = None
        while (validated_choice == None):
            user_choice = None

            #print menu1 options
            print("Please enter an integer corresponding to one of the following options:\n")
            for key in self.menu2:
                print("{} : {}".format(key, self.menu2[key][0]))
            
            # try to read user input
            try:
                user_choice = int(input("Choice: "))
            except ValueError:
                print("That was not a valid choice. Please try again.")
                continue

            
            if user_choice in self.menu2:
                validated_choice = user_choice
            else:
                print("That was not a valid choice.")
                continue
        
        # perform selected choice
        self.menu2[validated_choice][1]()
        return None


    def main_loop(self):
        while (not self._exit_program):
            if (self.current_user == None):
                self.use_menu1()
            else:
                self.use_menu2()            
        return None

if __name__ == "__main__":
    app = Application()
    app.main_loop()
    
    