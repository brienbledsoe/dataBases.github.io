def follow():
    if request.form: # submitted
        username = request.form["username"]
        # check if the username exists
        cursor = connection.cursor()
        query = "SELECT * FROM person WHERE username = %s" #query to check
        cursor.execute(query, (username))
        data = cursor.fetchone()

        if data: # if there is a username with 'username'
            # we found the username, send a follow request
            query = "SELECT * FROM follow WHERE username_followed = %s \
            AND username_follower = %s"
            # check if request has been sent already
            cursor.execute(query, (username, session['username']))
            data = cursor.fetchone()
            if (data): # we already sent the request before
                # check the followstatus
                if (data['followstatus'] == 1):
                    error = f"You already follow {username}!"
                else:
                    error = f"You already sent a request to {username}"
                return render_template("follow.html", message=error)
            else:  # good to go
                query = "INSERT INTO follow VALUES(%s,%s,0)"
                connection.commit()
                cursor.execute(query, (username, session['username']))
                message = f"Successfully sent a request to {username}"
                return render_template("follow.html", message=message)
        else: # the username was not found
            error = "That username does not exist, try another one"
            return render_template("follow.html", message=error)

    return render_template("follow.html")
