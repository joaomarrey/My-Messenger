# My Messenger
#### Video Demo:  https://www.youtube.com/watch?v=MiJ6ilw_M5E
#### Description:
This project was made by João Marrey Mendonça and is the final project for the CS50 Introduction to Computer Science online course.
This is a messenger, like WhatsappWeb, designed for PC messaging using an internet browser.
The project file contains:
* Two python files
* One .db file, implemented using sqlite3
* A directory, named templates, containing 5 html files, one of wich is a base template implement through JINJA, which serves three other templates
* Another directory named static, containing the css styling file used for all templates
The following tools, taught during the course, were used in this project:
* python
  *flask(library) and Jinja
* html5
* css
*sqlite3

#### app.py:

This file is a flask based python program, which manages the backend server side functions of the messenger.
It first imports some useful libraries, then sets up the flask app and the database that stores all the data from the users, their contacts and the messages.
The database will be explained further in it´s own topic. Now we will talk about the routes, there are five routes:
* register
* login
* logout
* addcontacts
* index

##### register
This route allows for two methods, get and post. First, it checks which method was used, if it was post, it will check if the requirements 
for creating an account are all satisfied:
* existing username that is not already in use
* password and password confirmation match and exist
* password length is greater or equal to 8, and at least one number is used

If all of this is satisfied, the system will hash the password, and insert it and the username into the users table, redirecting the user to the index route 
 and flashig the message: "registered succesfully". If the method was get, the system will render the standard register template. If any 
of the user requirements where violated, the system will render the register template whith a corresponding error message.

##### login
This route allows for two methods, get and post. First, the system will clear the session by calling ´session.clear´. Then, it checks which method was used, if it was post, it then checks 
whether the password and username exist, and correspond to a registered user, in which case, it register the user´s id in the session ´session["user_id"] = select[0]["id"]´ ,
then redirecting them to the index route and flashig the message: "logged in succesfully". If the method was get, the system will render the standard login template. In case the username and/or password 
are incorrect, it will render the login template with the error message: "invalid username or password".

##### logout
This route only allows for the get method, and it simply clears the session using `session.clear`, redirecting the user to the login route.

##### addcontacts
This route allows for two methods, get and post. First, it checks what method was used, if it was post, it will first check if the user requested
for a search or an contact addition, in the first case, it will check if the search was made using id or username, in either case the system 
checks the users table for matching users, which are put on a list and rendered in the html as a table. If the request was made for a contact addition, the system first checks if the user is not trying to 
add themselves to their contacts, if they are not, the system checks if the contact they are trying to add is not already a contact or if they exist as a user, in case they are not and do exist, it inserts both 
the user´s id and the contact´s id into the contacts table, as id_1 and id_2 respectively, after that extracting the automatically created id_chat from the 
newly inserted row, creating a new message table that uses the id_chat in it´s name as an index:
```
id_chat = db.execute("SELECT id_chat FROM contacts WHERE id_1=? AND id_2=?", session["user_id"], request.form.get("id"))
  id_chat = id_chat[0]['id_chat']
db.execute(f"CREATE TABLE messages{id_chat} (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, message TEXT, id_who_sent INTEGER NOT NULL)")
```
after that, it renders the addcontacts template with anmessage saying "Contact added: <username>".
If the method used was get, the standard addcontacts table is rendered, through which the user can search a new contact. If any malicious requests 
where made, the system will render the template with an error message.

##### index
This route allows for two methods, get and post. First, it sets up a new index in the session dictionary:
```
if "contact" not in session:
  session['contact'] = {"id_person": None, "id_chat": None, "username": None}
```
This dictionary allows us to store which of the user´s contacts is the current conversation happening with, so that in the case of, for example, sending a message, 
where it would be necessary to make a new request to the index route, the system would still be able to know who is the user chatting with.
Then the system checks if the request method is post, in that case it extracts all the user´s contacts information (username and id), which will be used to check for malicious requests, 
i.e if the requested id is indeed in the user´s contact list. After that, the route checks if the request was made for an specif id, in that case, the user selected from the standard index page a 
given contact with whom he desires to chat, then it checks if the id is in the contact list, extracting the id of the message database from the contacts
table, a process which is made both for id_1 and id_2, since there is only one register for each user, meaning that their id coudl be registered either as id_1 or id_2 
(for further elaboration on the structure of these complex tables, see "projects.db" topic), after that it sends all the info via a new "get" request 
for the index route, which allows to centralize the rendering of the chat in a single if statement, otherwise, that would have to be done in all four paths 
that require the rendering of the chat. In case the user´s post request was not a chat selection, the path chacks if the request was for a message to be sent, in which case, it checks if the id of the current chat 
is in the contact´s list, to prevent malicious requests, in which case, just like in the case of chat selection, it extracts the id of the message table from the contact´s
table, but now inserting the new message into the right message table, then making the same new request via get to the index route, which will lead to the chat rendering path.
In case the rquest was made via get, the system checks to see if the ´session['contacts´] dictionary has been set, if it has, that means that the get request 
wants the system to render the chat of the contact stored in this dictionary, so the system extracts all the info it needs from it, using it to select 
the right message table, and then rendering the conversation. In the case of the dictionary being empty, the system does not load any conversation, rendering the 
standard index page, from which the user can sect a conversation via a post request. In the case of any malicious requests being made, the system will the standard template with an error message, corresponding 
to the request.

#### helpers.py
this file contains a single decorated function "@login_required", which prevents a user from entering certain routes if they are not logged in, redirecting 
them to the login route.

#### project.db
This file contains three types of table, with wo of them being unique, and one infinitely replicable:
* users (unique)
* contacts (unique)
* messages<id_chat> (replicable)

The first table "users", is used to store basic user data, with it´s columns being:
* id
* username
* hased_password

The second table "contacts" is where the contacts are stored, i.e which user has a active conversation with which other user. It´s columns are:
* id_1
* id_2
* id_chat

The first and second columns are used to store the ids of the users who have a active conversation, generally id_1 will store the id of 
the user who added the contact and id_2 the id of the other one, but that is irrelevant for the purpose of this app. The column id_chat 
is the primary key generated and incremented automatically, which indexes the messages table used for these users´ conversation.

The third table "messages<id_chat>", stores all the information from a given conversation, for that reason, there will exist as many of this table as 
there are active conversations. It´s columns are:
* id
* message
* id_who_sent

The first column id is used to identify each message, the second column message, contains the text sent on that specific message, and the third 
column id_who_sent contains the id of the person who sent that message, so the system can figure out how to display it to the user.

#### static
This directory contains the file "styles.css", which has the css code used in this project.

#### templates
This directory contains all the templates used:
* addcontacts.html
* index.html
* layout.html
* login.html
* register.html

each one named as the route which renders them, except for layout.html, which contains the basic layout for all templates except index.html, implemented via JINJA.











