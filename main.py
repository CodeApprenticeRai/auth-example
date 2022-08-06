from multiprocessing.sharedctypes import Value
import bcrypt
import mysql.connector

CREATE_DB_SQL = "CREATE DATABASE IF NOT EXISTS main"
USE_MAIN_DB_SQL = "USE main"
CREATE_USERS_TABLE_SQL = "CREATE TABLE IF NOT EXISTS users (\
    id INT AUTO_INCREMENT PRIMARY KEY,\
    username VARCHAR(255) NOT NULL,\
    password VARCHAR(255) NOT NULL,\
    email VARCHAR(255) NOT NULL\
)"

exit_program = False
current_user = None
UNALLOWED_USERNAME_CHARACTERS = set("~!@#$%^&*()_+=-|\\}{][\"';:,./<>?")

def exit_program_choice():
    global exit_program
    exit_program = True
    print("Thank you for using the app!")
    return None

def valid_username(username):
    for letter in username:
        if letter in UNALLOWED_USERNAME_CHARACTERS:
            return False
    return True

def create_new_user_choice():
    requested_username = ""
    username_is_valid = False
    username_is_available = False
    global db_cursor

    while ((not username_is_valid) or (not username_is_available)):
    # get username and validate against db
        requested_username = input("Enter New Username:  ")
        
        if not valid_username(requested_username):
            print('Username can only contain alphanumeric charcters. Please try again.')
            continue
        else:
            username_is_valid = True

            #check if username already exists in db
            db_cursor.execute("SELECT username, password FROM users WHERE username = '{}' LIMIT 1".format(requested_username))
            result = db_cursor.fetchall()
            if (len(result) > 0):
                print("Username '{}' is already taken".format(requested_username))
            else:
                username_is_available = True
    
    password = input("Enter Password: ").encode()
    hash = bcrypt.hashpw(password, bcrypt.gensalt())
    


    db_cursor.execute(
        "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
        (requested_username, hash, "demo@onegenerativestudio.com")
    )
    global db_connection
    db_connection.commit()
    
    print("User {} was created.".format(requested_username))

    return None 

def login_choice():
    username = ""
    username_is_valid = False
    while ((username == "") or (not username_is_valid)):
        username = input("Enter Username: ")
        username_is_valid = valid_username(username)
        if (not username_is_valid):
            print('Username can only contain alphanumeric charcters. Please try again.')
    
    password = input("Enter Password: ").encode()
    db_cursor.execute(
        "SELECT username, password FROM users WHERE username = %s LIMIT 1",
        (username,)
    )

    results = db_cursor.fetchall()

    if (len(results) > 0):
        hash = results[0][1].encode()
        if bcrypt.checkpw(password, hash):
            print("You've successfully signed in")
            current_user = username
        else:
            print("Username / Password combination not found")
    else:
        print("Username / Password combination not found")

    return None


menu1 = {
    0 : ("Exit", exit_program_choice),
    1 : ("Create New User", create_new_user_choice),
    2 : ("Login", login_choice)
}

def main_loop():
    validated_choice = None

    while (validated_choice == None):
        user_choice = None
        print("Please enter an integer corresponding to one of the following options:\n")

        for key in menu1:
            print("{} : {}".format(key, menu1[key][0]))
        
        try:
            user_choice = int(input("Choice: "))
        except ValueError:
            print("That was not a valid choice")
            continue

        if user_choice in menu1:
            validated_choice = user_choice
        else:
            print("That was not a valid choice")
            continue

    menu1[validated_choice][1]()
    return None

if __name__ == "__main__":
    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="demo"
    )
    
    # db setup
    db_setup_results = [] 
    db_cursor = db_connection.cursor()
    db_setup_results.append( db_cursor.execute(CREATE_DB_SQL) ) 
    db_setup_results.append( db_cursor.execute(USE_MAIN_DB_SQL) )
    db_setup_results.append( db_cursor.execute(CREATE_USERS_TABLE_SQL) )

    while (not exit_program):
        main_loop()
    
    