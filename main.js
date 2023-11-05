const prompt = require("prompt-sync")({ sigint: true});
const bcrypt = require("bcrypt");
const saltRounds = 10; 

var mysql = require('mysql2');

const CREATE_DB_SQL = `CREATE DATABASE IF NOT EXISTS main`; 
const USE_MAIN_DB_SQL = `USE main`; 
const CREATE_USERS_TABLE_SQL = `CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL, 
    email VARCHAR(255) NOT NULL
)`;

var db_connection = mysql.createConnection({
    host: "localhost",
    user: "root",
    password: "demo"
})
console.log("created connection.");


var mysqlQueryCallback = (err, report) => {
    if (err) throw err;
    console.log("Report: " + JSON.stringify(report) + "\n");
}

db_connection.connect((err) => {
    if (err){throw err;}
    //else: 
    console.log("Successfully connected to database");
});

db_connection.query(CREATE_DB_SQL, mysqlQueryCallback);
db_connection.query(USE_MAIN_DB_SQL, mysqlQueryCallback);
db_connection.query(CREATE_USERS_TABLE_SQL, mysqlQueryCallback);


var exitProgram = false; 
var userChoiceMenu1;
var menu1  = {
    0 : "Exit",
    1 : "Create New User",
    2 : "Login"
}

var printMenu1 = () => {
    console.log("Please enter an integer corresponding to one of the following options:\n");
    
    for (let key in menu1){
        console.log(`${key} : ${menu1[key]}`);
    }

    console.log("\n");
    return;
}

var createNewUser = () => {
    let usernameExists = true;
    let newUsername;

    while (usernameExists){
        newUsername =  prompt("Enter New Username: ");

        // check that newUsername does not already exist in the database
        db_connection.query(`SELECT * FROM users WHERE username = ${newUsername}`, (err, rows) => {
            if (err){throw err;}
            if (rows.length > 0){
                usernameExists = true;
                console.log("That username already exists.");
            }
        });
    }
    
    let passwordMatch = false;

    while (!passwordMatch){
        let unencryptedPassword1 = prompt("Enter Password: ");
        let unencryptedPassword2 = prompt("Re-enter Password: ");
        if (unencryptedPassword1 == unencryptedPassword2){
            passwordMatch = True;
        } else {
            "Passwords must match. Please try again.\n"
        }
    }
    
    bcrypt.genSalt(saltRounds, (err, salt) => {
        bcrypt.hash(unencryptedPassword1, salt, (err, hash) => {
            // create record in the database for new username and password combination
            // store hashed password in database
            db_connection.query(
                `INSERT INTO users VALUES (${newUsername}, ${hash}, demo_email@onegenerativestudio.com)`,
                mysqlQueryCallback
            );
        });
    });
    // console.log("New User Successfully Created.")
    return;
}

var login = () => {
    let authenticated = false;

    while (!authenticated){
        let username = prompt("Enter Username: ");
        let password = prompt("Enter Password: ");
            
        // if username and password match database records
        db_connection.query(
            `SELECT username, password from users where username=${username}`,
            (err, results) => {
                if (results.length > 0){
                    bcrypt.compare(password, results[0].password, (err, result) => {
                        authenticated = result;
                        if (!authenticated){
                            console.log("The username/password combination entered was invalid.\n");
                        }
                    });
                }
            }
        );
    }
}

var handleUserChoiceMenu1 = {
    0 : () => { 
        exitProgram = true; 
    },
    1 : createNewUser,
    2 : login
}


var mainLoop = () => {
    while (!exitProgram){
        printMenu1()
        userChoiceMenu1 = parseInt( prompt("Choice: ") );
        console.log(`The option you chose was: ${userChoiceMenu1}`)
        handleUserChoiceMenu1[userChoiceMenu1]();
        console.log(`variable exitProgram is now set to ${exitProgram}`);
    }
}

mainLoop(); 
db_connection.end();

console.log("the program should return to the terminal at this point.");