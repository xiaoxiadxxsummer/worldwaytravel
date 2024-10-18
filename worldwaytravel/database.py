import mysql.connector


def get_dict_cursor():
    connection = mysql.connector.connect(user='root',
                                         password='root1234', host='127.0.0.1', auth_plugin='mysql_native_password', \

                                         database='Worldway Travel', autocommit=True)
    dbconn = connection.cursor()
    return dbconn, connection


def get_cursor():
    connection = mysql.connector.connect(user='root',
                                         password='root1234', host='127.0.0.1', auth_plugin='mysql_native_password', \

                                         database='Worldway Travel', autocommit=True)
    dbconn2 = connection.cursor()
    return dbconn2, connection