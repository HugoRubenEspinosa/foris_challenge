import mysql.connector
from mysql.connector import Error

def db_connect(host, port, database, user, password):
      return  mysql.connector.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
      )


def db_execute_from_file(host, port, database, user, password, file):
    try:
        error = True
        answer = ""
        with open(file, 'r', encoding='utf-8') as f:
            query_string = f.read()

        connection = db_connect(host = host,
                                port = port,
                                database = database,
                                user = user,
                                password = password
                               )

        if connection.is_connected():

            cursor = connection.cursor()

            cursor.execute(query_string)
            record = cursor.fetchone()
            error = False
            error_description = ""
        
    except Error as e:
        error = True
        error_description = e
        record = None

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            return error, error_description, record


def db_execute_sql_from_file(conection, sql_file):
    results = []  # Lista para almacenar resultados
    try:
        # Abrir y leer el archivo SQL
        with open(sql_file, 'r', encoding='utf-8') as file:
            sql_script = file.read()
        
        # Crear un cursor para ejecutar los comandos SQL
        cursor = conection.cursor()

        # Ejecutar el script SQL leído
        for i, statement in enumerate(sql_script.split(';'), start=1):  # Dividir por cada sentencia SQL (por ';')
            statement = statement.strip()
            if statement:  # Ignorar líneas vacías
                cursor.execute(statement)
                
                # Si es una consulta SELECT, obtener los resultados
                if statement.lower().startswith("select"):
                    result = cursor.fetchall()  # Obtener todos los resultados de la consulta SELECT
                    results.append({
                        'statement': statement,
                        'result': result,
                        'rowcount': None
                    })
                else:
                    # Para otras consultas como INSERT, UPDATE, DELETE
                    results.append({
                        'statement': statement,
                        'result': None,
                        'rowcount': cursor.rowcount  # Cantidad de filas afectadas
                    })
        
        # Confirmar los cambios
        conection.commit()

        error = None

    except Exception as e:
        error = str(e)
    
    finally:
        # Cerrar el cursor
        if conection.is_connected():
            cursor.close()
        
        # Devolver los resultados y el error (si existe)
        return results, error
