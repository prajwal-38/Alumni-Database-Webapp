from flask import Flask, render_template, request, redirect, session, flash, Response
from flask_session import Session
# from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import io
from base64 import b64encode
import csv
import pymysql
from flaskext.mysql import MySQL
from dataclasses import dataclass
import os
import json

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


#mail configs
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = '**************@gmail.com'
app.config['MAIL_PASSWORD'] = '****************'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)
mail_list = None


mysql_host = os.environ.get('MYSQL_HOST', 'localhost')
mysql_user1 = os.environ.get('MYSQL_USER1', 'root')
mysql_password1 = os.environ.get('MYSQL_PASSWORD1', 'root')
mysql_user2 = os.environ.get('MYSQL_USER2', 'student')
mysql_password2 = os.environ.get('MYSQL_PASSWORD2', 'Pass@1234')
mysql_user3 = os.environ.get('MYSQL_USER3', 'employee')
mysql_password3 = os.environ.get('MYSQL_PASSWORD3', 'Pass@5678')
login_db = os.environ.get('LOGIN_DB', 'users')
mysql_db = os.environ.get('MYSQL_DB', 'alumni')

mysql = None
Role =None
userdb = MySQL(app, prefix="userdb", host=mysql_host,
               user=mysql_user1, password=mysql_password1, db=login_db)
mysql1 = MySQL(app, prefix="mysql1", host=mysql_host,
               user=mysql_user1, password=mysql_password1, db=mysql_db)
mysql2 = MySQL(app, prefix="mysql2", host=mysql_host,
               user=mysql_user2, password=mysql_password2, db=mysql_db)
mysql3 = MySQL(app, prefix="mysql3", host=mysql_host,
               user=mysql_user3, password=mysql_password3, db=mysql_db)

def get_cols(mysql, table_name):
    cursor = mysql.get_db().cursor()
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    tuples = cursor.fetchall()
    cols = []
    for x in tuples:
        cols.append(x[0])
    return cols


@dataclass
class User():
    name: str
    password: str
    role: str = None

# defining home route


@app.route('/', methods=['GET'])
def index():
    session["logged_in"] = False
    session.pop("user", None)
    return render_template('index.html')


@app.route('/', methods=['POST'])
def login():
    session["user"] = User(request.form['name'], request.form['password'])
    cursor = userdb.get_db().cursor()
    cursor.execute("SELECT password, role FROM login_details WHERE name=%s", (session["user"].name,))
    userdb.get_db().commit()
    password = cursor.fetchone()
    # print(password)
    cursor.close()
    if password is None:
        flash("Not a recognized user")
        session.pop("user", None)
        return render_template('index.html')
    elif(password[0] == session["user"].password):
        session["logged_in"] = True
        global mysql
        global Role
        if(password[1] == "admin"):
            Role = "Admin"
            mysql = mysql1
        elif(password[1] == "Student"):
            Role = "Student"
            mysql = mysql2
        else:
            Role = "Employee"
            mysql = mysql3
        return redirect('/tables')
    else:
        session.pop("user", None)
        flash("Wrong Password")
        return render_template('index.html')


@app.route('/logout', methods=['GET'])
def logout():
    session["logged_in"] = False
    session.pop("user", None)
    return redirect('/')

# directing to team page or tables page

# @app.route('/', methods=['POST'])
# def home_post():
#     x = request.form

#     if(x.get('edit')==None):
#         return redirect('/team')
#     else:
#         return redirect('/tables')


# rendering team_details page
@app.route('/team', methods=['GET'])
def team():
    return render_template('team_details.html')


# rendering the list of tables in the database
@app.route('/tables', methods=['GET'])
def tables():
    if session.get('logged_in', False) == False or mysql is None:
        return redirect('/')
    args = request.args

    cursor = mysql.get_db().cursor()
    cursor.execute("SHOW TABLES")
    tables_in_db = cursor.fetchall()
    cursor.close()
    table_names_in_db = []
    
    for i in range(len(tables_in_db)):
        table_names_in_db.append(tables_in_db[i][0])

    table_name = args.get('tableName', default=None, type=str)
    if(table_name is not None and table_name not in table_names_in_db):
        return render_template('errors.html', errorMessage="This table doesn't exist")




    if table_name is None:
        cursor = mysql.get_db().cursor()
        cursor.execute("SHOW TABLES")

        tables = cursor.fetchall()
        cursor.close()
        table_names = []
        # print(tables)
        for i in range(len(tables)):
            table_names.append(tables[i][0])

        cur = mysql.get_db().cursor()
        schema = []
        for table_name in table_names:
            cur.execute(f"SHOW COLUMNS FROM {table_name}")
            mysql.get_db().commit()
            schema.append(cur.fetchall())
        cur.close()

        # return render_template('display_entries.html', userDetails=table_data, table_col_names=TABLE_COLUMN_NAMES, table_name=table_name, EntriesOrSchema="Schema",
        #                     display_edit_buttons="NO",display_edit_fields="NO")
        TABLE_COLUMN_NAMES = ["Field", "Type", "Null", "Key"]
        if mysql == mysql1 or mysql == mysql3:
            return render_template('display_tables.html', table_names=table_names, schema=schema, table_col_names=TABLE_COLUMN_NAMES, display_edit_buttons="EMP", len=len(table_names), len_col=len(TABLE_COLUMN_NAMES))
        else:
            return render_template('display_tables.html', table_names=table_names, schema=schema, table_col_names=TABLE_COLUMN_NAMES, display_edit_buttons="STUDENT", len=len(table_names), len_col=len(TABLE_COLUMN_NAMES))
    else:
        # try:
        cur = mysql.get_db().cursor()
        cur.execute(f"SELECT * FROM {table_name}")
        mysql.get_db().commit()
        table_data = cur.fetchall()
        cur.close()
        # img = None
        # if table_name == "alumni":
        #     img = []
        #     # img = table_data[0][4].decode('ascii')
        #     # print(img)
        #     img.append(b64encode(table_data[0][4]).decode('utf-8'))
        #     # print(img)

        # len_col = len(table_data[0])

        # cursor = mysql.get_db().cursor()
        # cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        # table_column_names_tuples = cursor.fetchall()
        # TABLE_COLUMN_NAMES = []

        # for x in table_column_names_tuples:
        #     TABLE_COLUMN_NAMES.append(x[0])
        # cursor.close()
        TABLE_COLUMN_NAMES = get_cols(mysql, table_name)
        # TABLE_COLUMN_NAMES=[]

        if mysql == mysql1:
            return render_template('display_entries.html', userDetails=table_data, table_name=table_name, table_col_names=TABLE_COLUMN_NAMES, EntriesOrSchema="Entries",
                                    display_edit_buttons="ADMIN", display_edit_fields="NO", is_search_op="NO")
        elif mysql == mysql2:
            return render_template('display_entries.html', userDetails=table_data, table_name=table_name, table_col_names=TABLE_COLUMN_NAMES, EntriesOrSchema="Entries",
                                    display_edit_buttons="STUDENT", display_edit_fields="NO", is_search_op="NO")
        elif mysql == mysql3:
            return render_template('display_entries.html', userDetails=table_data, table_name=table_name, table_col_names=TABLE_COLUMN_NAMES, EntriesOrSchema="Entries",
                                    display_edit_buttons="EMP", display_edit_fields="NO", is_search_op="NO")

            # return render_template('display_entries.html', userDetails=table_data, table_name=table_name, table_col_names=TABLE_COLUMN_NAMES, EntriesOrSchema="Entries",
            #                        display_edit_buttons="ADMIN", display_edit_fields="NO")

        # except Exception as e:

            # print(e)
        return render_template('errors.html', errorMessage="Table not defined")


# updating rendered output based on Operations button pressed.

@app.route('/tables/edit', methods=['POST'])
def tables_edit():
    if session["logged_in"] == False or mysql is None:
        return redirect('/')
    x = request.form
    pressed = None
    table_name = None

    # which button was pressed
    if(x.get('insert') == None):
        if(x.get('update') == None):
            if(x.get('delete') == None):
                if(x.get('rename') == None):
                    if(x.get('search') == None):
                        if(x.get('upload') == None):
                            pressed = 'download'
                        else:
                            pressed = 'upload'
                    else:
                        pressed = 'search'
                else:
                    pressed = 'rename'
            else:
                pressed = 'delete'
        else:
            pressed = 'update'
    else:
        pressed = 'insert'

    # finding column names
    table_name = x[pressed]
    # print(mysql.get_db().cursor())
    # cursor = mysql.get_db().cursor(pymysql.cursors.DictCursor)
    # cursor.execute(
    #     "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s and TABLE_NAME=%s", ("alumni", table_name,))
    # table_column_names_tuples = cursor.fetchall()
    # TABLE_COLUMN_NAMES = []

    # for dict in table_column_names_tuples:
    #     y = dict['COLUMN_NAME']
    #     TABLE_COLUMN_NAMES.append(y)
    TABLE_COLUMN_NAMES = get_cols(mysql, table_name)


    # finding table
    cur = mysql.get_db().cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    mysql.get_db().commit()
    table_data = cur.fetchall()
    len_col = len(table_data[0])
    data = []
    for row in range(len(table_data)):
        # change to tuples
        row_data = []
        for i in range(len(table_data[row])):
            row_data.append(str(table_data[row][i]))
        data.append(row_data)

    # data = json.dumps(data, ensure_ascii=False);
    # updating rendered output based on the button pressed
    if(pressed == 'insert'):
        return render_template('display_entries.html', userDetails=table_data, table_col_names=TABLE_COLUMN_NAMES, table_name=table_name, EntriesOrSchema="Insert",
                               display_edit_buttons="NO", display_edit_fields="YES", op='insert', is_search_op="NO", len_col=len_col, role=Role, table = data)
    elif(pressed == 'update'):
        return render_template('display_entries.html', userDetails=table_data, table_col_names=TABLE_COLUMN_NAMES, table_name=table_name, EntriesOrSchema="Update",
                               display_edit_buttons="NO", display_edit_fields="YES", op='update', is_search_op="NO", len_col=len_col, role= Role, table = data)
    elif(pressed == 'delete'):
        return render_template('display_entries.html', userDetails=table_data, table_col_names=TABLE_COLUMN_NAMES, table_name=table_name, EntriesOrSchema="Delete",
                               display_edit_buttons="NO", display_edit_fields="YES", op='delete', is_search_op="NO", len_col=len_col, role = Role, table = data)
    elif(pressed == 'rename'):
        return render_template('display_entries.html', userDetails=table_data, table_col_names=TABLE_COLUMN_NAMES, table_name=table_name, EntriesOrSchema="Rename",
                               display_edit_buttons="NO", display_edit_fields="YES", op='rename', is_search_op="NO", len_col=len_col, role = Role, table = data)
    elif(pressed == 'search'):
        return render_template('display_entries.html', userDetails=table_data, table_col_names=TABLE_COLUMN_NAMES, table_name=table_name, EntriesOrSchema="Search",
                               display_edit_buttons="NO", display_edit_fields="YES", op='search', is_search_op="YES", len_col=len_col, role = Role, table = data)
    elif(pressed == 'upload'):
        return render_template('display_entries.html', userDetails=table_data, table_col_names=TABLE_COLUMN_NAMES, table_name=table_name, EntriesOrSchema="Upload File",
                               display_edit_buttons="NO", display_edit_fields="YES", op='upload', is_search_op="NO", len_col=len_col, role = Role, table = data)
    elif(pressed == 'download'):
        return redirect(f'/tables/download/{table_name}')
    else:
        return render_template('errors.html')


# insert page render logic

@app.route('/tables/edit/insert', methods=['POST'])
def edit_insert():
    if session["logged_in"] == False:
        return redirect('/')
    x = request.form
    # print(x)
    table_name = x['table_name']

    # Table Before Insertion
    cur = mysql.get_db().cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    mysql.get_db().commit()
    table_data_before = cur.fetchall()

    # getting column names
    # cursor = mysql.get_db().cursor(pymysql.cursors.DictCursor)
    # cursor.execute(
    #     "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s and TABLE_NAME=%s", ("alumni", table_name,))
    # table_column_names_tuples = cursor.fetchall()
    # TABLE_COLUMN_NAMES = []

    # for dict in table_column_names_tuples:
    #     y = dict['COLUMN_NAME']
    #     TABLE_COLUMN_NAMES.append(y)
    TABLE_COLUMN_NAMES = get_cols(mysql, table_name)


    # filling new values
    NEW_VALUES = []
    for col in TABLE_COLUMN_NAMES:
        NEW_VALUES.append(x[col])

    # making the query
    query = "INSERT INTO " + table_name+"(" + ", ".join(TABLE_COLUMN_NAMES) + \
        ") VALUES (" + \
        ", ".join(["%s" for _ in range(len(TABLE_COLUMN_NAMES))]) + ")"

    # executing query
    cur = mysql.get_db().cursor()
    try:
        # cur.executescript(query, NEW_VALUES)
        cur.execute(query, NEW_VALUES)
        mysql.get_db().commit()

        # table after query execution
        cur = mysql.get_db().cursor()
        cur.execute(f"SELECT * FROM {table_name}")
        mysql.get_db().commit()
        table_data_after = cur.fetchall()

        # print(table_data_after)
        # print(type(table_data_after))

        return render_template('tables_before_after.html', table_before=table_data_before, table_after=table_data_after, table_name=table_name,
                               table_col_names=TABLE_COLUMN_NAMES, second_table="YES")
    except Exception as e:
        # print(e)
        return render_template('errors.html', errorMessage="Input Error- Re-check your input against the schema.", errorDetails=e.args[1])


# update page render logic

@app.route('/tables/edit/update', methods=['POST'])
def edit_update():
    if session["logged_in"] == False:
        return redirect('/')
    x = request.form
    table_name = x['table_name']
    condition = x['condition']

    # Table Before Insertion
    cur = mysql.get_db().cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    mysql.get_db().commit()
    table_data_before = cur.fetchall()

    TABLE_COLUMN_NAMES = get_cols(mysql, table_name)

    # filling new values

    NEW_VALUES = []
    for i in range(len(TABLE_COLUMN_NAMES)):
        if(x[TABLE_COLUMN_NAMES[i]] == ""):
            TABLE_COLUMN_NAMES[i] = "remove"
        else:
            NEW_VALUES.append(x[TABLE_COLUMN_NAMES[i]])

    # changing column names depending on participation of fields
    NEW_COLUMN_NAMES = []
    for name in TABLE_COLUMN_NAMES:
        if(name != "remove"):
            NEW_COLUMN_NAMES.append(name)

    # statement clauses
    strings = []
    for i in range(len(NEW_COLUMN_NAMES)):
        y = NEW_COLUMN_NAMES[i]+"="+NEW_VALUES[i]
        strings.append(y)

    # making query
    query = "UPDATE "+table_name+" SET " + \
        ", ".join(strings) + " WHERE " + condition

    try:
        cur = mysql.get_db().cursor()
        cur.execute(query)
        mysql.get_db().commit()

        # table after query execution
        cur = mysql.get_db().cursor()
        cur.execute(f"SELECT * FROM {table_name}")
        mysql.get_db().commit()
        table_data_after = cur.fetchall()

        return render_template('tables_before_after.html', table_before=table_data_before, table_after=table_data_after, table_name=table_name,
                               table_col_names=TABLE_COLUMN_NAMES, second_table="YES")
    except:
        return render_template('errors.html', errorMessage="Update Error- Re-check your update value types/condition against the schema and current database entries.")


# delete page render logic

@app.route('/tables/edit/delete', methods=['POST'])
def edit_delete():
    if session["logged_in"] == False:
        return redirect('/')
    x = request.form
    table_name = x['table_name']
    
    if (Role == 'Employee'):
        condition = x['drop1'] + " = " + "'"+x['drop2']+"'"
        # print(condition)
    else:
        condition = x['condition']
        # print(condition)

    # Table Before Insertion
    cur = mysql.get_db().cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    mysql.get_db().commit()
    table_data_before = cur.fetchall()

    TABLE_COLUMN_NAMES = get_cols(mysql, table_name)

    # making query
    query = "DELETE FROM "+table_name+" WHERE " + condition

    try:
        cur = mysql.get_db().cursor()
        cur.execute(query)
        mysql.get_db().commit()

        # table after query execution
        cur = mysql.get_db().cursor()
        cur.execute(f"SELECT * FROM {table_name}")
        mysql.get_db().commit()
        table_data_after = cur.fetchall()

        return render_template('tables_before_after.html', table_before=table_data_before, table_after=table_data_after, table_name=table_name,
                                table_col_names=TABLE_COLUMN_NAMES, second_table="YES")
    except Exception as e:
        # print(e)
        return render_template('errors.html', errorMessage=condition+" : Error in condition")


# rename page render logic

@app.route('/tables/edit/rename', methods=['POST'])
def edit_rename():
    if session["logged_in"] == False:
        return redirect('/')
    x = request.form
    old_table_name = x['table_name']
    new_table_name = x['new_table_name']

    # Table Before Insertion
    cur = mysql.get_db().cursor()
    cur.execute(f"SELECT * FROM {old_table_name}")
    mysql.get_db().commit()
    table_data_before = cur.fetchall()

    TABLE_COLUMN_NAMES = get_cols(mysql, old_table_name)

    try:
        # making query
        query = "RENAME TABLE "+old_table_name+" TO " + new_table_name
        cur = mysql.get_db().cursor()
        cur.execute(query)
        mysql.get_db().commit()

        # table after query execution
        cur = mysql.get_db().cursor()
        cur.execute(f"SELECT * FROM {new_table_name}")
        mysql.get_db().commit()
        table_data_after = cur.fetchall()

        return render_template('tables_before_after.html', table_before=table_data_before, table_after=table_data_after, table_name=new_table_name,
                               table_col_names=TABLE_COLUMN_NAMES, old_table_name=old_table_name, new_table_name=new_table_name, second_table="YES")
    except:
        return render_template('errors.html', errorMessage="Rename Error- Re-check your input for New Table Name")


# search table using keyword logic

@app.route('/tables/edit/search/', methods=['POST'])
def edit_search():
    if session["logged_in"] == False:
        return redirect('/')
    x = request.form
    table_name = x['table_name']
    search_key = x['search_key']

    global mail_list
    mail_list = None
    OP = -1

    TABLE_COLUMN_NAMES = get_cols(mysql, table_name)

    # making query
    # query = "DELETE FROM "+table_name+" WHERE " + condition
    cols = ", ".join(TABLE_COLUMN_NAMES)

    query = "SELECT * FROM "+table_name + \
        " WHERE CONCAT(" + cols + ") LIKE " + "'%" + search_key + "%'"
    # print(query)

    # try:
    cur = mysql.get_db().cursor()
    cur.execute(query)
    mysql.get_db().commit()

    OP = cur.fetchall()
    # OP = [list(tup) for tup in OUTPUT]

    if(mail_list==None and table_name=="alumni"):
        q_query = "SELECT Full_Name,Email FROM "+table_name + \
    " WHERE CONCAT(" + cols + ") LIKE " + "'%" + search_key + "%'"
        cur = mysql.get_db().cursor()
        cur.execute(q_query)
        mysql.get_db().commit()

        mail_list=cur.fetchall()
    # print(OP)
    # print(type(OP))
    len_col = len(TABLE_COLUMN_NAMES)
    # return render_template('display_entries.html', userDetails=OP, table_name=table_name, table_col_names=TABLE_COLUMN_NAMES, EntriesOrSchema="Entries",
    #                        display_edit_buttons="NO", display_edit_fields="NO", is_search_op="NO", len_col=len_col)
    return render_template('tables_before_after.html', table_before = OP, table_after=None, table_name=table_name,
                            table_col_names=TABLE_COLUMN_NAMES, search_msg=f'The results for "{search_key}" are:', second_table="NO", search_key=search_key)
    # except:
    return render_template('errors.html', errorMessage="Search Error- Re-check your search key against the schema and current database entries.", table_name=table_name)


@app.route('/tables/download/<table_name>', methods=['GET'])
def service_download(table_name):
    if session["logged_in"] == False:
        return redirect('/')

    table_name = table_name

    TABLE_COLUMN_NAMES = get_cols(mysql, table_name)

    # Table Data
    cur = mysql.get_db().cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    mysql.get_db().commit()
    data = cur.fetchall()

    # Create a CSV file and write the data to it
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(TABLE_COLUMN_NAMES)  # Replace with your column names
    for row in data:
        writer.writerow(row)

    # Return the CSV file as a response with appropriate headers
    response = Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment;filename={table_name}.csv'}
    )

    return response


@app.route('/tables/edit/search/download', methods=['GET', 'POST'])
def service_search_download():
    if session["logged_in"] == False:
        return redirect('/')

    x = request.form
    table_name = x['table_name']
    search_key = x['search_key']

    TABLE_COLUMN_NAMES = get_cols(mysql, table_name)

    # making query
    # query = "DELETE FROM "+table_name+" WHERE " + condition
    cols = ", ".join(TABLE_COLUMN_NAMES)

    query = "SELECT * FROM "+table_name + \
        " WHERE CONCAT(" + cols + ") LIKE " + "'%" + search_key + "%'"

    cur = mysql.get_db().cursor()
    cur.execute(query)
    mysql.get_db().commit()

    data = cur.fetchall()

    # Create a CSV file and write the data to it
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(TABLE_COLUMN_NAMES)  # Replace with your column names
    for row in data:
        writer.writerow(row)

    file_name = table_name+'/'+search_key

    # Return the CSV file as a response with appropriate headers
    response = Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment;filename={file_name}.csv'}
    )

    return response


@app.route('/tables/edit/upload/<table_name>', methods=['POST'])
def upload_file(table_name):
    if session["logged_in"] == False:
        return redirect('/')
    
    uploaded_file = request.files['file']
    # Create a file object from the uploaded file data
    file_stream = io.StringIO(
        uploaded_file.stream.read().decode("UTF8"), newline=None)
    # Parse the CSV data into a list of rows
    csv_data = csv.reader(file_stream)

    # skip the first row
    next(csv_data)

    # Table before Upload
    # Table Before Insertion
    cur = mysql.get_db().cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    mysql.get_db().commit()
    table_data_before = cur.fetchall()

    TABLE_COLUMN_NAMES = get_cols(mysql, table_name)

    # making query
    # query = "DELETE FROM "+table_name+" WHERE " + condition
    cols = ", ".join(TABLE_COLUMN_NAMES)
    placeholders = ", ".join(["%s" for _ in range(len(TABLE_COLUMN_NAMES))])

    # Create a connection to the MySQL database
    cur = mysql.get_db().cursor()

    try:
        # Execute an INSERT statement for each row of data
        for row in csv_data:
            query = "INSERT INTO " + table_name + \
                " (" + cols + ") VALUES (" + placeholders + ")"
            data = [row[i] for i in range(len(row))]
            cur.execute(query, data)
            mysql.get_db().commit()

        # table after query execution
        cur = mysql.get_db().cursor()
        cur.execute(f"SELECT * FROM {table_name}")
        mysql.get_db().commit()
        table_data_after = cur.fetchall()

        return render_template('tables_before_after.html', table_before=table_data_before, table_after=table_data_after, table_name=table_name,
                                table_col_names=TABLE_COLUMN_NAMES, second_table="YES")
    except:
        return render_template('errors.html', errorMessage=f"Upload Error- Recheck your filetype (should be CSV)/filesize or the columns of your file against value types/condition against the schema for {table_name}.")




@app.route('/alumni/mail', methods=['GET','POST'])
def mail_alumni():
    if session["logged_in"] == False:
        return redirect('/')
    
    global mail_list

    if(request.method=='GET'):
        # x = request.form
        # print(x)
        table_name = request.args.get('name_table')
        search_key = request.args.get('key_search')

        # print(table_name,search_key)

        TABLE_COLUMN_NAMES = get_cols(mysql, table_name)

        cols = ", ".join(TABLE_COLUMN_NAMES)
        query = "SELECT Full_Name,Email FROM "+table_name + \
            " WHERE CONCAT(" + cols + ") LIKE " + "'%" + search_key + "%'"
        cur = mysql.get_db().cursor()
        cur.execute(query)
        mysql.get_db().commit()
        OP = cur.fetchall()

        if(mail_list==None):
            mail_list=OP
        
        col_names=["Name","Email"]

        return render_template('mail.html', table_before=mail_list, table_col_names=col_names, enable_send="YES", search_key=search_key, table_name=table_name)
    
    else:
        x = request.form
        table_name = x['table_name']
        search_key = x['search_key']

        
        TABLE_COLUMN_NAMES = get_cols(mysql, table_name)

        cols = ", ".join(TABLE_COLUMN_NAMES)
        query = "SELECT Full_Name,Email FROM "+table_name + \
            " WHERE CONCAT(" + cols + ") LIKE " + "'%" + search_key + "%'"
        cur = mysql.get_db().cursor()
        cur.execute(query)
        mysql.get_db().commit()
        OP = cur.fetchall()

        if(mail_list==None):
            mail_list=OP
        
        col_names=["Name","Email"]

        return render_template('mail.html', table_before=mail_list, table_col_names=col_names, enable_send="YES", search_key=search_key, table_name=table_name)



@app.route('/alumni/mail/edit', methods=['POST'])
def edit_mail():
    if session["logged_in"] == False:
        return redirect('/')
    
    x = request.form
    pressed = None

    if(x.get('add_mail') == None):
        pressed='remove_mail'
    else:
        pressed='add_mail'

    global mail_list
    table_name = x['table_name']
    search_key = x['search_key']

    TABLE_COLUMN_NAMES = get_cols(mysql, table_name)
    
    cols = ", ".join(TABLE_COLUMN_NAMES)
    query = "SELECT Full_Name,Email FROM "+table_name + \
        " WHERE CONCAT(" + cols + ") LIKE " + "'%" + search_key + "%'"
    cur = mysql.get_db().cursor()
    cur.execute(query)
    mysql.get_db().commit()
    OP = cur.fetchall()

    if(mail_list==None):
        mail_list=OP

    col_names=["Name","Email"]



    if(pressed=='add_mail'):
        return render_template('mail.html',table_before = mail_list, table_col_names = col_names, enable_edit="YES", op="Add", search_key=search_key, table_name=table_name)
    else:
        return render_template('mail.html',table_before = mail_list, table_col_names = col_names, enable_edit="YES", op="Remove", search_key=search_key, table_name=table_name)

        
@app.route('/alumni/mail/edit/update', methods=['POST'])
def update_mail_list():
    if session["logged_in"] == False:
        return redirect('/')

    x = request.form
    table_name = x['table_name']
    search_key = x['search_key']

    pressed=None    
    if(x.get('Add') == None):
        pressed='Remove'
    else:
        pressed='Add'


    alum_name = x['alum_name']
    alum_mail = x['alum_mail']

    # print(alum_name,alum_mail)

    global mail_list
    item = (alum_name,alum_mail)
    # print(item)

    if(pressed=='Add'):
        new_mail_list = mail_list + (item,)
        mail_list = new_mail_list
    else:
        mail_list = tuple(t for t in mail_list if t!=item)
    

    col_names=["Name","Email"]
    return render_template('mail.html',table_before = mail_list, table_col_names = col_names, enable_edit="YES", op=pressed, search_key=search_key, table_name=table_name)





@app.route('/alumni/mail/send', methods=['POST'])
def send_mail():
    x = request.form
    subj = x['subject']
    body = x['body']

    global mail_list
    print(mail_list)

    receiver_ids= [alum[1] for alum in mail_list] 
    print(receiver_ids)
    msg = Message(subj,sender='alumni_dbms@g2supremacy.com',recipients=receiver_ids)
    msg.body = body
    mail.send(msg)

    mail_list = None

    return redirect('/tables')


if __name__ == '__main__':
    app.run(debug=True, port=4999)


# dynamic route for rendering updated tables after performing an operation (Insert, Delete, Update or Rename)
# @app.route('/tables/entries/<table_name>', methods =['POST'] )
# def dynamic_table(table_name):
#     if session["logged_in"] == False:
#         return redirect('/')
#     table_name = table_name

#     table_name_string = str(table_name)
#     table_name_string = table_name_string.encode('utf-8').decode('utf-8')
#     table_name_string = str(table_name_string)

#     cur = mysql.get_db().cursor()
#     cur.execute(f"SELECT * FROM {table_name_string}")
#     mysql.get_db().commit()
#     table_data = cur.fetchall()

#     cursor = mysql.get_db().cursor(pymysql.cursors.DictCursor)
#     cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s and TABLE_NAME=%s", ("alumni", table_name_string,))
#     table_column_names_tuples = cursor.fetchall()
#     TABLE_COLUMN_NAMES =[]

#     for dict in table_column_names_tuples:
#         x = dict['COLUMN_NAME']
#         TABLE_COLUMN_NAMES.append(x)

#     cur.close()
#     return render_template('display_entries.html', userDetails=table_data, table_name=table_name_string, table_col_names=TABLE_COLUMN_NAMES, EntriesOrSchema="Entries",
#                             display_edit_buttons="YES",display_edit_fields="NO")


# updating rendered output based on button pressed.

# @app.route('/tables', methods =['POST'])
# def tables_post():
#     x = request.form

#     button_pressed=None
#     table_name = x['tableName']

#     if(x.get('entries')==None):
#         button_pressed='schema'
#     else:
#         button_pressed='entries'

#     table_name_string = str(table_name)
#     table_name_string = table_name_string.encode('utf-8').decode('utf-8')
#     table_name_string = str(table_name_string)


#     #determing rendered output based on button pressed- View Schema or View Entries

#     if(button_pressed=='entries'):

#         cur = mysql.get_db().cursor()
#         try:
#             cur.execute(f"SELECT * FROM {table_name_string}")
#             mysql.get_db().commit()
#             table_data = cur.fetchall()

#             cursor = mysql.get_db().cursor(pymysql.cursors.DictCursor)
#             cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s and TABLE_NAME=%s", ("alumni", table_name_string,))
#             table_column_names_tuples = cursor.fetchall()
#             TABLE_COLUMN_NAMES =[]

#             for dict in table_column_names_tuples:
#                 x = dict['COLUMN_NAME']
#                 TABLE_COLUMN_NAMES.append(x)

#             cur.close()

#             return render_template('display_entries.html', userDetails=table_data, table_name=table_name_string, table_col_names=TABLE_COLUMN_NAMES, EntriesOrSchema="Entries",
#                                 display_edit_buttons="YES",display_edit_fields="NO")

#         except Exception as e:


#             return render_template('errors.html', errorMessage="Table not defined")


#     else:

#         cur = mysql.get_db().cursor()
#         try:
#             cur.execute(f"SHOW COLUMNS FROM {table_name_string}")
#             mysql.get_db().commit()
#             table_data = cur.fetchall()
#             TABLE_COLUMN_NAMES = ["Field","Type","Null","Key","Default","Extra"]
#             cur.close()

#             return render_template('display_entries.html', userDetails=table_data, table_col_names=TABLE_COLUMN_NAMES, table_name=table_name_string, EntriesOrSchema="Schema",
#                                 display_edit_buttons="NO",display_edit_fields="NO")
#         except:
#             return render_template('errors.html', errorMessage="Table not defined")
