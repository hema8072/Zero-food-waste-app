from flask import Flask, render_template, request, redirect, session, flash
from database import get_db_connection
import os

app = Flask(__name__)

app.secret_key = "your_secret_key"
UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "uploads"
)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
# Home
@app.route('/')
def home():
    return render_template('home.html')


# Register
@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        conn = get_db_connection()

        conn.execute(
            "INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
            (name,email,password,role)
        )

        conn.commit()
        conn.close()

        return redirect('/login')


    return render_template('register.html')



# Login
@app.route('/login', methods=['GET','POST'])
def login():

    msg=None

    if request.method == 'POST':

        email=request.form['email']
        password=request.form['password']


        conn=get_db_connection()

        user=conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email,password)
        ).fetchone()

        conn.close()


        if user:

            session['user']=dict(user)

            if user['role']=="donor":
                return redirect('/donor')

            else:
                return redirect('/receiver')

        else:
            msg="Invalid Email or Password"


    return render_template('login.html',msg=msg)



# Donor Dashboard
@app.route('/donor')
def donor():

    if 'user' not in session or session['user']['role'] != 'donor':
        return redirect('/login')


    return render_template(
        'donor.html',
        user=session['user']
    )



# Receiver Dashboard
@app.route('/receiver')
def receiver():

    if 'user' not in session or session['user']['role'] != 'receiver':
        return redirect('/login')

    conn = get_db_connection()

    foods = conn.execute(
    """
    SELECT * FROM food_donations
    WHERE status='Available'
    """
    ).fetchall()

    conn.close()


    return render_template(
        'receiver.html',
        user=session['user'],
        foods=foods
    )

@app.route('/add_food', methods=['POST'])
def add_food():

    if 'user' not in session or session['user']['role'] != 'donor':
        return redirect('/login')


    food_name = request.form['food_name']
    quantity = request.form['quantity']
    category = request.form['category']
    expiry = request.form['expiry_time']
    address = request.form['address']
    contact = request.form['contact']


    image = request.files['image']


    image_name = ""


    if image:

        image_name = image.filename

        image.save(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                image_name
            )
        )


    donor_email = session['user']['email']


    conn = get_db_connection()


    conn.execute(
    '''
    INSERT INTO food_donations
    (
    donor_email,
    food_name,
    quantity,
    category,
    expiry_time,
    address,
    contact,
    image,
    status
    )

    VALUES(?,?,?,?,?,?,?,?,?)
    ''',

    (
    donor_email,
    food_name,
    quantity,
    category,
    expiry,
    address,
    contact,
    image_name,
    "Available"
    )

)


    conn.commit()
    conn.close()


    flash("Food added successfully!")
    return redirect('/donor')
@app.route('/request_food', methods=['POST'])
def request_food():

    if 'user' not in session or session['user']['role'] != 'receiver':
        return redirect('/login')


    food_id = request.form['food_id']

    receiver_email = session['user']['email']


    conn = get_db_connection()


    # Check if already requested
    existing = conn.execute(
        """
        SELECT * FROM food_requests
        WHERE food_id=? AND receiver_email=?
        """,
        (food_id, receiver_email)
    ).fetchone()


    if existing:

        conn.close()

        flash("You already requested this food!")
        return redirect('/receiver')


    # Insert new request
    conn.execute(
        """
        INSERT INTO food_requests
        (food_id, receiver_email, status)

        VALUES(?,?,?)
        """,

        (
        food_id,
        receiver_email,
        "Pending"
        )

    )


    conn.commit()
    conn.close()


    flash("Food request sent!")
    return redirect('/my_requests')

@app.route('/admin', methods=['GET','POST'])
def admin_login():

    if request.method=="POST":

        username=request.form['username']

        password=request.form['password']


        conn=get_db_connection()


        admin=conn.execute(
            """
            SELECT * FROM admin
            WHERE username=? AND password=?
            """,
            (username,password)
        ).fetchone()


        conn.close()


        if admin:

            session['admin'] = admin['username']

            return redirect('/admin_dashboard')


        else:

            return "Invalid Admin Login"



    return render_template('admin_login.html')



@app.route('/admin_dashboard')
def admin_dashboard():

    if 'admin' not in session:
        return redirect('/admin')


    conn = get_db_connection()


    users = conn.execute(
        "SELECT * FROM users"
    ).fetchall()



    foods = conn.execute(
        "SELECT * FROM food_donations"
    ).fetchall()



    requests = conn.execute(
        "SELECT * FROM food_requests"
    ).fetchall()



    user_count = len(users)

    food_count = len(foods)

    request_count = len(requests)



    conn.close()



    return render_template(
        'admin_dashboard.html',
        users=users,
        foods=foods,
        requests=requests,
        user_count=user_count,
        food_count=food_count,
        request_count=request_count
    )




@app.route('/donor_requests')
def donor_requests():

    if 'user' not in session:
        return redirect('/login')


    donor_email = session['user']['email']


    conn = get_db_connection()


    requests = conn.execute(
    """
    SELECT 
    food_requests.id,
    food_requests.receiver_email,
    food_requests.status,
    food_donations.food_name,
    food_donations.quantity

    FROM food_requests

    JOIN food_donations

    ON food_requests.food_id = food_donations.id

    WHERE food_donations.donor_email=?

    """,
    (donor_email,)
).fetchall()



    conn.close()



    return render_template(
        'donor_requests.html',
        requests=requests
    )

@app.route('/update_request', methods=['POST'])
def update_request():

    request_id = request.form['request_id']
    action = request.form['action']


    conn = get_db_connection()


    # update request status
    conn.execute(
        """
        UPDATE food_requests
        SET status=?
        WHERE id=?
        """,
        (action, request_id)
    )


    # If accepted, mark food as claimed
    if action == "Accepted":

        food_id = conn.execute(
            """
            SELECT food_id
            FROM food_requests
            WHERE id=?
            """,
            (request_id,)
        ).fetchone()['food_id']


        conn.execute(
            """
            UPDATE food_donations
            SET status='Claimed'
            WHERE id=?
            """,
            (food_id,)
        )


    conn.commit()
    conn.close()


    return redirect('/donor_requests')


@app.route('/my_requests')
def my_requests():

    if 'user' not in session:
        return redirect('/login')


    receiver_email = session['user']['email']


    conn = get_db_connection()


    requests = conn.execute(
        """
        SELECT 
        food_requests.id,
        food_requests.status,
        food_donations.food_name,
        food_donations.quantity,
        food_donations.address

        FROM food_requests

        JOIN food_donations

        ON food_requests.food_id = food_donations.id


        WHERE food_requests.receiver_email=?

        """,
        (receiver_email,)
    ).fetchall()


    conn.close()


    return render_template(
        'my_requests.html',
        requests=requests
    )

@app.route('/admin_logout')
def admin_logout():

    session.pop('admin', None)

    return redirect('/admin')

@app.route('/delete_user/<int:id>')
def delete_user(id):

    if 'admin' not in session:
        return redirect('/admin')


    conn = get_db_connection()

    conn.execute(
        "DELETE FROM users WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()


    return redirect('/admin_dashboard')



@app.route('/delete_food/<int:id>')
def delete_food(id):

    if 'admin' not in session:
        return redirect('/admin')


    conn = get_db_connection()


    conn.execute(
        "DELETE FROM food_donations WHERE id=?",
        (id,)
    )


    conn.commit()
    conn.close()


    return redirect('/admin_dashboard')



@app.route('/delete_request/<int:id>')
def delete_request(id):

    if 'admin' not in session:
        return redirect('/admin')


    conn = get_db_connection()


    conn.execute(
        "DELETE FROM food_requests WHERE id=?",
        (id,)
    )


    conn.commit()
    conn.close()


    return redirect('/admin_dashboard')



# Logout
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')



if __name__=="__main__":
    app.run(debug=True)