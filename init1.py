#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
from datetime import datetime
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)
UPLOAD_FOLDER = r'C:\Users\Brien Bledsoe\Documents\Intro_to_Databases\Project\Part3proj\Images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
# app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port = 3308,
                       user='root',
                       password='',
                       db='finstagramtable',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
                       # creating a cursor that will be used to iterate over the results
                       # that we get

#Define a route to hello function
@app.route('/')#allows us to write a function for what will be returned for this specifie route
def hello():
    # return ('Hello World')
    return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')
    # render_template takes a file thats in our directory and renders thats in our
    # browser


#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():

    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM person WHERE username = %s and password = %s'
    cursor.execute(query, (username, password))
    #stores the results in a variable
    # again here we have our password in plain text, but if we stored a hash of the password
    # such as the shaw2 then we would simply call that hush function in the cursor.execute
    # right next to the password variable
    #cursor.execute(query,(username,shaw2(password)))
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    #we close the query when its over
    error = None
    #error of course is set to none initially so that we can check for one
    if(data):
        #eif the query was made and there was data in the query, then we want to
        #start a session
        #creates a session for the the user
        session['username'] = username
        #session is a built in python dictionary, associating the username, (whatever the user entered)
        #with the string 'username'
        return redirect(url_for('home'))
        #and when were done we go back to the url root for home and the code does whatever
        #we specify to do
    else:
        #returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)
        #send thhem the error message if invalid login and allow them to attempt to login again
        #click the link to be redirected to register

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['userName']
    firstname = request.form['firstName']
    lastname = request.form['lastName']
    email = request.form['email']
    password = request.form['password']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    #query = 'SELECT * FROM user WHERE username = %s'
    query = 'SELECT * FROM person WHERE userName = %s'
    #is a string that will act as the query
    #%s is a placeholder, and the s is basically saying its expecting a string
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row

    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        #cursor.close()
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO person VALUES(%s, %s, %s, %s, %s)'
        #this is bad practice to put password in plain text, in industry practice you
        #would usually want to hash with a cryptographic hash like shaw2
        cursor.execute(ins, (username, password, firstname, lastname, email))
        #executing on our cursor, with variable name and parameters of variable we
        #fetched from the user
        conn.commit()
        #then we commit to make sure those changes are stored into the database
        cursor.close()
        return render_template('index.html')


@app.route('/home')
def home():
    user = session['username']
    #first thing the home page does is get back the stored username session variable and store
    #it to some python variable
    cursor = conn.cursor();
    query = 'SELECT postingDate, pID,follower,followee FROM photo NATURAL JOIN follow WHERE poster = %s ORDER BY postingDate DESC'
    #also bringing in all the post the user made along with the timestamp and ORDER
    #of timestamps, so we can get them in reverse chronological order
    cursor.execute(query, (user))
    #executing that query, plugging in for the %s string parameter the value of the user
    #here we could be getting back an arbitrary number of rows depending on how many posts
    #this user has previosly done
    data = cursor.fetchall()
    cursor.close()
    #after we get done fetching the data we close it
    return render_template('home.html', username=user, photos=data)
    #when we are done we are going to send some data back to the user
    #we will be sending the home.html file that the user will see on the client side
    #and we are also sending back two parameters, username and posts, into render_template
    #one is the name of the user and the value returned from the data base
    #so posts is going to be some kind of list of lists, along with some meta data thats
    # representing all of the rows we got back when we executed this query


@app.route('/post', methods=['GET', 'POST'])
def post():
    username = session['username']
    #grabbing the username from the session dictionary, which has username that was previously stored when
    #we logged in
    cursor = conn.cursor();
    #set up the connection
    blog = request.form['blog']
    #fetching our parameter blog, which is passed in the home.html form
    query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
    #query that we are going to insert into the blog table
    # attributes we are sending is blog_post and username and the values are going to be two
    # strings
    cursor.execute(query, (blog, username))
    # when we execute those queries we are going to abstantiate those strings, with blog
    # the test that we typed into the text box ^, and username which is the logged in user
    conn.commit()

    cursor.close()
    return redirect(url_for('home'))

@app.route('/select_user')
def select_blogger():
    #check that user is logged in
    username = session['username']
    #should throw exception if username not found
    cursor = conn.cursor();
    query = 'SELECT DISTINCT username FROM person'
    #only going to users who have actually posted something
    #and since their might be multiple posts, posted by the same person we are going to
    #use SELECT DISTINCT
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('select_user.html', user_list=data)

@app.route('/follow', methods=["GET","POST","DELETE"])
def followUser():
    if request.form: #submitted
        username = session['username']
        #going to have an insert statement, getting one of the parameters from the data passed in
        #the username of the person I want to followee
        #the other parameter is my username for the follower
        #if request.form
        cursor = conn.cursor();
        query = "SELECT * FROM person WHERE username = %s" #checking valid user
        cursor.execute(query, (username))
        data = cursor.fetchone()

        if(data):
            followerUsername = session['username']
            followeeUsername = request.form['followeeUsername']
            # cursor = conn.cursor();
            query = "SELECT * FROM follow WHERE follower = %s AND followee = %s"
            print(followeeUsername)
            cursor.execute(query, (followerUsername,followeeUsername))
            data = cursor.fetchone()
            if(data):#my thought process from the TA's is that this means we already sent request
                if(data["followStatus"] == 1):
                    error = "%s Is already followed by you!" % (followeeUsername)
                else:
                    error = "You already sent a request to %s" % (followeeUsername)
                return render_template("follow.html", error=error)

            else: #no previous follow request sent
                query = "INSERT INTO follow VALUES(%s,%s,0)"
                #query = "INSERT INTO follow (follower,followee,followStatus) VALUES(%s,%s,%i)"
                #for some reason this syntax wont allow me to execute the query below marked "test"
                conn.commit()
                cursor.execute(query, (followerUsername,followeeUsername))
                #status= 0
                #cursor.execute(query, (followerUsername, followeeUsername),0)) #test
                message = "Successfully sent a request to %s" % (followeeUsername)
                return render_template("follow.html", error=message)

        else:
            error = "That username does not exist"
            return render_template("follow.html", error=error)




    return render_template("follow.html")


@app.route('/notifications', methods=["GET", "POST", "DELETE"])#will accept get or post parameters
def show_notifications():
    if(request.method == 'POST'):
        # message="Testing"
        choice = request.form.get('choice')
        follower = request.form.get('follower')
        print("--------",follower)
        #currentFollower = {{follower}}
        #print(currentFollower)
        username=session['username']
        cursor=conn.cursor()
        query = 'SELECT followStatus FROM follow\
        JOIN person ON followee=username WHERE followee= %s AND followStatus = 0'
        cursor.execute(query,(username))
        data =cursor.fetchall()
        #cursor.close()
        print(data)
        #print('This is the choice var: ', choice)
        if(choice=="accept"):
                #if(data['followStatus']==0):
            query = 'UPDATE follow SET followStatus=1\
            WHERE followee= %s'

            cursor.execute(query,(username))
            conn.commit()
            #cursor.close()
            #data = cursor.fetchall()
            message = 'You have accepted the request'
            return render_template('notifications.html', error = message)
        else:
            #message = "This user already follows you"
            # queryFollower = 'SELECT follower FROM follow\
            # JOIN person ON followee=username WHERE followee = %s AND followStatus =0 '
            # cursor.execute(queryFollower,(username))
            # theFollower = cursor.fetchall()
            # print("happy=====-----")
            # print("theFollower: ",theFollower)
            query = 'DELETE FROM follow\
            WHERE followee=%s AND follower=%s'
            print("follower: ",follower)
            conn.commit()
            cursor.execute(query,(username,follower))
            #cursor.close()
            message = 'You have declined the request'
            return render_template('notifications.html', error = message)


    username = session['username']

    #decline = request.form['decline']
    #making sure that the user is logged in first
    #poster = request.args['poster']
    cursor = conn.cursor();

    query = 'SELECT follower FROM follow\
    JOIN person ON followee=username WHERE followee= %s AND followStatus = 0'

    #needed the first name of the user in the session
    #joining person with the follower ID
    #focus on fixing the query
    cursor.execute(query, (username))
    #data = cursor.fetchone()
    data = cursor.fetchall() #can't use fetchone(), because it doesn't provide a list I can iterate through
    #data2 = cursor.execute(query,(username))
    print(data)
    #print("this is data 2: ", data2)
    print("===========")
    cursor.close()
    if(data):
        return render_template('notifications.html', follower=data)
    else:
        message= 'You have no follow request'
        return render_template('notifications.html', error=message)



# authenticating creation or joining
# a group
@app.route( "/friendGroups", methods = ["GET","POST"] )
def groupAuth( ):
    # grab username and set error to none
    if(request.method=="POST"):

        username = session["username"]
        groupName= request.form["groupName"]
        description=request.form.get("description")
        cursor = conn.cursor()
        query = 'SELECT groupName, groupCreator FROM friendgroup WHERE groupName= %s AND\
        groupCreator=%s'
        cursor.execute(query,(groupName,username))
        data=cursor.fetchall()
        print(data)
        if(data):
            error = "You have already created a friendgroup with the name %s" % (groupName)
            return render_template('groups.html',error=error)
        else:
            query = 'INSERT INTO friendgroup(groupName,groupCreator,description) VALUES (%s,%s,%s)'
            cursor.execute(query,(groupName,username,description))
            conn.commit()
            error = None
            return render_template('groups.html',error=error)
    # error = None
    return render_template('groups.html')

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/post_photo', methods=["POST", "GET"])
def postPhoto():
    if(request.method=="POST"):
        username = session["username"]
        image = request.form["img"]
        # pID = 11111
        print("This image: ", image)
        print("====================================================+++")
        caption = request.form.get("caption")
        allFollowers = request.form.get("allFollowersChoice")
        cursor = conn.cursor()
        if image not in request.files:
            message = 'No file part'
            return render_template('post.html',message=message)
        if image.filename == "":
            message = "no files selected for upload"
            return render_template('post.html',message=message)
        if image and allowed_file(image):
            image = secure_filename(image.filename)
            image.save(os.path.join("UPLOAD_FOLDER"),filename)
            if allFollowers == 1:
                photoID = username + image.filename #how do I use AUTO INCREMENT
                #I think the query isn't working because of pID not being correctly generated
                #by the auto increment feature, we haven't figured out how to add auto increment
                query = "INSERT INTO photo(pID,postingDate,filePath,allFollowers,caption,poster)\
                VALUES (%i,%s,%s,%i,%s,%s)"
                cursor.execute(query, (pID,time.strftime('%Y-%m-%d %H:%M:%S'),image.filename,allFollowers,caption,username))
                conn.commit()
                message = 'None'
                render_template('post.html',message=message)
            else:
                allFollowers = 0
                photoID = username + image.filename #how do I use AUTO INCREMENT
                query = "INSERT INTO photo(pID,postingDate,filePath,allFollowers,caption,poster)\
                VALUES (%s,%s,%s,%s,%s,%s)"
                cursor.execute(query, (photoID,time.strftime('%Y-%m-%d %H:%M:%S'),image.filename,allFollowers,caption,username))
                conn.commit()
                message = 'File successfully uploaded'
                render_template('post.html',message=message)


        else:
            message ='Allowed file types are png,jpg,jpeg,gif'
            return render_template('post.html',message=message)

    return render_template('post.html')


@app.route('/logout')
def logout():
    session.pop('username')
    # when we log out we are just going to take that dictionary and pop the username out so that we will
    # no longer have a username in our dictionary and then redirect to the loading screen
    # after somebody is logged out, they shouldn't be able to do something that can be done by users that
    # are logged in
    return redirect('/')

app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
    #port 5000 is specified here,
    # 127.0.0.1 is the url for local host
