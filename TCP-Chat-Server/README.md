# TCP-Chat-Server
TCP chat server for computer networking class.

TCP server in 3 files using python

Server runs using TCP and threading, allowing many connections
Each connection is named by their socket (ip and port)
Port defaults to 1234 but can be inputted in terminal to change

General file design philosophy is to seperate functionality
New clients are pushed into a thread which is managed by the Client class, this class inherits from the Thread class of the threading library.
In this class all actual functionality is implemented, so each thread handles basically everything for it's connection.

Clients can:
send messages to all other clients
set name with /nick <name>
see other connections with /list
leave the server with /quit
private message with /msg <recipient> <message>

Server operators can:
send messages to all clients
private message with /msg <recipient> <message>
kick clients with /kick <name>


Example with all features:

SERVER:
$ python3 chatServer.py 12345
Server started on port 12345
Welcome 127.0.0.1|41050 to the server!
Welcome 127.0.0.1|41052 to the server!
127.0.0.1|41050 is now Malcolm
127.0.0.1|41052 is now Sturgis
Welcome 127.0.0.1|41054 to the server!
127.0.0.1|41054 is now Jimmy
Hello users!
/msg Sturgis You're my favorite <3
Message sent to 1 users of name Sturgis
/kick Jimmy
Jimmy has left the server.
Kicked 1 people.
Malcolm has left the server.
Sturgis has left the server.

CLIENT 1:
$ nc localhost 12345
Welcome 127.0.0.1|41050 to the server!
Welcome 127.0.0.1|41052 to the server!
/nick Malcolm
You are now Malcolm
127.0.0.1|41052 is now Sturgis
Welcome 127.0.0.1|41054 to the server!
127.0.0.1|41054 is now Jimmy
Jimmy(private): Hey, how's it going? 
Operator: Hello users!
Jimmy has left the server.
/quit
You have left the server

CLIENT 2:
$ nc localhost 12345
Welcome 127.0.0.1|41052 to the server!
127.0.0.1|41050 is now Malcolm
/nick Sturgis
You are now Sturgis
Welcome 127.0.0.1|41054 to the server!
127.0.0.1|41054 is now Jimmy
/list
127.0.0.1|41050 as Malcolm
127.0.0.1|41054 as Jimmy
Operator: Hello users!
Operator (private): You're my favorite <3 
Jimmy has left the server.
Malcolm has left the server.
/quit
You have left the server

CLIENT 3:
Welcome 127.0.0.1|41054 to the server!
/nick Jimmy
You are now Jimmy
/msg Malcolm Hey, how's it going?
Message sent to 1 users of name Malcolm
Operator: Hello users!
You have left the server
