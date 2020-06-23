import os
from collections import deque
from flask import Flask,render_template,session,request,redirect
from flask_socketio import SocketIO,send,emit,join_room,leave_room
from helpers import login_required

app = Flask(__name__)
app.config["SECRET_KEY"] ="my secter key"
socketio = SocketIO(app)

# kepp track of channels
channelsCreated =[]

# users logged
usersLogged =[]

# instanciate a dict
channelsMessages = dict()

@app.route("/")
@login_required
def room():
	return render_template("room.html",channels=channelsCreated)

@app.route("/signin",methods=['GET','POST'])
def signin():

	session.clear()
	username = request.form.get("username")

	if request.method == "POST":
		if len(username) < 1 or username == '' :
			return render_template("error.html",message="username can't be empty")
		if username in usersLogged:
			return render_template("error.html",message="that username already exists !")

		usersLogged.append(username)

		session['username'] = username

		# remember the user session on a cookie if the browser is closed
		session.permanent =True
		return redirect("/")
	else:
		return render_template("signin.html")

@app.route("/logout",methods=['GET'])
def logout():

	try:
		usersLogged.remove(session['username'])
	except ValueError:
		pass

	session.clear()
	return redirect("/")

@app.route("/create",methods=['GET','POST'])
def create():


	newChannel = request.form.get("channel")

	if request.method == "POST":

		if newChannel in channelsCreated :
			return render_template("error.html",message="that channel already exists !")

		channelsCreated.append(newChannel)


		channelsMessages[newChannel] = deque()

		return redirect("/chat/"+newChannel)

	else:
		return render_template("create.html",channels = channelsCreated)

@app.route("/chat/<channel>",methods=['GET','POST'])
@login_required
def enter_channel(channel):

	session['current_channel'] = channel

	if request.method =="POST":
		return redirect("/")
	else:
		return render_template("chat.html",channels=channelsCreated,messages=channelsMessages[channel])

@socketio.on("joined",namespace='/')
def joined():

	room=session.get('current_channel')

	join_room(room)

	emit('status',{
		'userJoined': session.get('username'),
		'channel':room,
		'msg':session.get('username')+' has entered the channel '
		},room=room)


@socketio.on("left",namespace='/')
def left():

	room = session.get('current_channel')

	leave_room(room)

	emit('status',{
		'msg':session.get('username')+' has left the chaanel'

		},room=room)


@socketio.on('send message')
def send_msg(msg,timestamp) :
	room = session.get('current_channel')


	if len (channelsMessages[room]) > 100 :
		
		channelsMessages[room].popleft()

	channelsMessages[room].append([session.get('username'),msg,timestamp])


	emit('announce message',{
		'user':session.get('username'),
		'timestamp':timestamp,
		'msg':msg},
		room=room)



