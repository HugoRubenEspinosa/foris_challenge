import requests

import docker
import time

import logging.config

import tarfile
import io
from pathlib import Path

from mysql_conn import db_connect, db_execute_sql_from_file
from config import ConfigSettings
from Bcolors import Bcolors



def create_dir(dir):
    import os
    try:
        os.mkdir(dir)
        logging.debug(f"{Bcolors.OKCYAN}Directory '{dir}' was created.{Bcolors.ENDC}")
    except FileExistsError:
        logging.debug(f"{Bcolors.OKCYAN}The directory '{dir}' already exists.{Bcolors.ENDC}")


def get_work_dir(dir):
    dir_parent=Path(__file__).parent
    work_dir = (dir_parent / dir).resolve()
    create_dir (work_dir)
    return work_dir

def get_access_token(url, user, password):
    # Realizar el POST a /login
    login_url = url
    login_data = {
        "username": "{{user}}",
        "password": "{{password}}"
    }

    response = requests.post(login_url, json=login_data)

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        error = 0
    else:
        access_token = ""
        error = response.status_code

    return error, access_token


def get_challenge(url, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        text= response.text
        error = 0
    else:
        text = ""
        error = response.status_code

    return error, text


def save_challenge_document(file_dir, file_name, text):
    dir = get_work_dir(file_dir)
    file = (dir / file_name).resolve()

    try:
        with open(file, "w") as file:
            file.writelines(text)
        logging.info(f"{Bcolors.OKBLUE}File {file_name} was created succesfully.{Bcolors.ENDC}")
        step_error = False
    except Exception as e:
        logging.error(f"{Bcolors.FAIL}Save Challenge Instruction does not work - '{file_name}' in '{file_dir}'.{Bcolors.ENDC}")
        logging.error(f"{Bcolors.FAIL}Description: {e}{Bcolors.ENDC}")
        step_error = True

    return step_error


def download_SQL_dump(url, access_token, file):
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers, allow_redirects=True)

        open(file, 'wb').write(response.content)
        step_error = False

    except Exception as e:
        logging.error(f"{Bcolors.FAIL}Save Challenge Instruction does not work - file '{file}'.{Bcolors.ENDC}")
        logging.error(f"{Bcolors.FAIL}Description: {e}{Bcolors.ENDC}")
        file = None
        step_error = True

    return step_error, file


def create_tar_in_memory(file_path):
    # Crear un archivo tar en memoria
    tar_stream = io.BytesIO()
    name = file_path.name
    with tarfile.open(fileobj=tar_stream, mode='w') as tar:
        tar.add(file_path, name)
    tar_stream.seek(0)  # Volver al principio del stream
    return tar_stream


def remove_container(container_name):
    try:
        existing_container = docker.from_env().containers.get(container_name)
        logging.info(f"{Bcolors.OKBLUE}Container '{container_name}' exists. Stopping and deleting...{Bcolors.ENDC}")

        # Si el contenedor existe, detenerlo y eliminarlo
        existing_container.stop()
        existing_container.remove()
        logging.info(f"{Bcolors.OKBLUE}Container '{container_name}' was deleted.{Bcolors.ENDC}")

    except docker.errors.NotFound:
        logging.info(f"{Bcolors.OKBLUE}Container '{container_name}' does not exist.{Bcolors.ENDC}")


def create_container_database(config_setting: ConfigSettings):
    client = docker.from_env()

    # Configurar variables de entorno para MySQL
    mysql_root_password = config_setting.db_password
    mysql_database = config_setting.db_name
    mysql_port = config_setting.db_port
    container_name = config_setting.db_docker_container_name
    container_image = config_setting.db_docker_container_image
    container_port = config_setting.db_docker_db_port

    # Remove container if exists
    logging.info(f"{Bcolors.OKBLUE}Validate container '{container_name}' exist.{Bcolors.ENDC}")
    remove_container(container_name)
    
    # Crear el contenedor
    logging.info(f"{Bcolors.OKBLUE}Creating container '{container_name}'.{Bcolors.ENDC}")
    container = client.containers.run(
                                        container_image,
                                        name=container_name, 
                                        ports={mysql_port:container_port},          
                                        environment={
                                            "MYSQL_ROOT_PASSWORD": mysql_root_password,
                                            "MYSQL_DATABASE": mysql_database,
                                        },
                                        detach=True               
                                    )
    container.reload()

    # Esperar a que MySQL esté listo
    waiting_seconds = 30
    logging.info(f"{Bcolors.OKBLUE}Waiting for 'MySQL' to be ready ({waiting_seconds} seconds).{Bcolors.ENDC}")
    time.sleep(waiting_seconds)  # Dar tiempo para que el servicio de MySQL esté completamente iniciado

    return container


def create_container_db_tables(config_setting: ConfigSettings, container, sql_file_path):
    # Crear archivo tar con el archivo .sql
    tar_stream = create_tar_in_memory(sql_file_path)

    # Copiar el archivo .sql dentro del contenedor
    logging.info(f"{Bcolors.OKBLUE}Coping '{sql_file_path}' to container '{config_setting.db_docker_container_name}'.{Bcolors.ENDC}")
    container.put_archive("/tmp", tar_stream)

    # Validar que el archivo fue copiado
    logging.info(f"{Bcolors.OKBLUE}Validating that the file '{sql_file_path}' was copied.{Bcolors.ENDC}")
    exec_result = container.exec_run("ls /tmp")
    logging.debug(f"{Bcolors.OKCYAN}exec_result.output.decode(){Bcolors.ENDC}")  # Ver lista de archivos en /tmp

    # Verificar si el archivo está en la lista
    file_name = sql_file_path.name
    if file_name in exec_result.output.decode():
        logging.info(f"{Bcolors.OKBLUE}The file '{file_name}' was copied successfully.{Bcolors.ENDC}")
    else:
        logging.error(f"{Bcolors.FAIL}The file '{file_name}' is not located in the container '{config_setting.db_docker_container_name}'.{Bcolors.ENDC}")

    # Ejecutar el archivo SQL para crear la base de datos
    logging.info(f"{Bcolors.OKBLUE}Executing script SQL from '{file_name}' to databes '{config_setting.db_name}'.{Bcolors.ENDC}")

    # Ejecutar el script SQL dentro del contenedor
    exec_log = container.exec_run(
        f"bash -c 'cat /tmp/{file_name} | mysql --user=root --password={config_setting.db_password} --default-character-set=latin1 {config_setting.db_name}'"
    )

    # Mostrar la salida del comando
    logging.debug(f"{Bcolors.OKCYAN}{exec_log.output.decode()}{Bcolors.ENDC}")
    logging.info(f"{Bcolors.OKGREEN}Databases was created from '{file_name}' successfully{Bcolors.ENDC}")

    return container


def db_execute_from_files(config_setting: ConfigSettings, file):
    host = config_setting.db_host
    port = config_setting.db_docker_db_port
    database = config_setting.db_name
    user = config_setting.db_user
    password = config_setting.db_password

    #error, error_description, record = db_execute_from_file(host, port, database, user, password, file)

    connection = db_connect(host, port, database, user, password)
    results, error = db_execute_sql_from_file(connection, file)
    error_description = ""


    if not error:
        for result in results:
            result_result = result_statement = result_rowcount = None
            if 'result' in result:
                result_statement = result['statement']
                result_result = result['result']

                logging.debug(f"{Bcolors.OKCYAN}Statement: '{result_statement}'.{Bcolors.ENDC}")
                logging.debug(f"{Bcolors.OKCYAN}Result: '{result_result}'.{Bcolors.ENDC}")
            else:
                result_statement = result['statement']
                result_rowcount = result['rowcount']
                logging.debug(f"{Bcolors.OKCYAN}Statement: '{result_statement}'.{Bcolors.ENDC}")
                logging.debug(f"{Bcolors.OKCYAN}Rowcount: '{result_rowcount}'.{Bcolors.ENDC}")

        #answer = record[0]
        #logging.debug(f"{Bcolors.OKGREEN}The answer is '{answer}'.{Bcolors.ENDC}")
        error = False
    else:
        logging.error(f"{Bcolors.FAIL}Error: {error} - Description: '{error_description}'.{Bcolors.ENDC}")
        error = True
        #answer=None
    
    return error, results


def challenge_validate(url, access_token, number_of_groups, answer):
    headers = {"Authorization": f"Bearer {access_token}"}
    validate_data = {
                      "number_of_groups": number_of_groups,
                      "answer": answer
                    }
    response = requests.post(url, headers=headers, json=validate_data)

    if response.status_code == 200:
        result_validation = False
        validate_text = "Your answer its correct!"

        text= response.json().get("msg")
        error_code = 0
        error_description = ""

        if text == validate_text:
            result_validation = True
        else:
            error_description = text
            result_validation = False

    else:
        text = ""
        result_validation = False
        error_code = response.status_code
        error_description = response.json().get('error')
        logging.error(f"{Bcolors.FAIL}{error_code} - {error_description}{Bcolors.ENDC}")

    return error_code, error_description, result_validation


def main():
    url_path_root = "http://mini-challenge.foris.ai"
    step_name = ""
    step_error = False

    if not step_error:
        step_name = "get_access_token"
        logging.info(f"{Bcolors.OKBLUE}Executing [{step_name}]{Bcolors.ENDC}")

        url_path_end_point = url_path_root + "/login"
        step_error, access_token = get_access_token(url_path_end_point, "foris_challenge", "ForisChallenge")

    if not step_error:
        step_name = "get_challenge"
        logging.info(f"{Bcolors.OKBLUE}Executing [{step_name}]{Bcolors.ENDC}")

        url_path_end_point = url_path_root + "/challenge"
        step_error, texto = get_challenge(url_path_end_point, access_token)

    if not step_error:
        step_name = "save_challenge_document"
        logging.info(f"{Bcolors.OKBLUE}Executing [{step_name}]{Bcolors.ENDC}")

        step_error = save_challenge_document(config_setting.work_dir_documents, "challenge_document.txt", texto)

    if not step_error:
        step_name = "download_SQL_dump"
        logging.info(f"{Bcolors.OKBLUE}Executing [{step_name}]{Bcolors.ENDC}")

        url_path_end_point = url_path_root + config_setting.db_dumps #"/dumps/mysql"
        file_path = get_work_dir(config_setting.work_dir_scripts)
        file_name = "mysql_dump.sql"
        file = (file_path / file_name).resolve()

        step_error, file_dump = download_SQL_dump(url_path_end_point, access_token, file)
        logging.info(f"{Bcolors.OKBLUE}'{file_dump}' was download.{Bcolors.ENDC}")

    if not step_error:
        step_name = "ai_analyzer"
        logging.info(f"{Bcolors.OKBLUE}Executing [{step_name}]{Bcolors.ENDC}")
        logging.info(f"{Bcolors.OKBLUE}By the time I have enough money to pay openAI. {Bcolors.YELLOW}:({Bcolors.ENDC}")
        
        #step_error, challenges_description = ai_analyzer("challenge_document.txt")
        #i = 0
        #for challenge in challenges_description:
        #    i += 1
        #    create_file_challenge(challenge, "query_challenge_"+i+".sql")


    if not step_error:
        step_name = "create_container_database"
        logging.info(f"{Bcolors.OKBLUE}Executing [{step_name}]{Bcolors.ENDC}")
        
        container = create_container_database(config_setting)
        
    if not step_error:
        step_name = "create_container_db_tables"
        logging.info(f"{Bcolors.OKBLUE}Executing [{step_name}]{Bcolors.ENDC}")
        
        create_container_db_tables(config_setting, container, file_dump)

    if not step_error:
        step_name = "db_execute_first_challenge"
        logging.info(f"{Bcolors.OKBLUE}Executing [{step_name}]{Bcolors.ENDC}")

        file_path = get_work_dir(config_setting.work_dir_scripts)
        file_name = "query_challenge_1.sql"
        file = (file_path / file_name).resolve()

        step_error, result = db_execute_from_files(config_setting, file)
        if not step_error:
            challenge_answer_1 = result[0]['result'][0][0]
            logging.info(f"{Bcolors.OKGREEN}challenge_answer_1 : {challenge_answer_1}{Bcolors.ENDC}")
        else:
            logging.error(f"{Bcolors.FAIL}challenge_answer_1 error: {step_error}{Bcolors.ENDC}")
   
    if not step_error:
        step_name = "db_execute_second_challenge"
        logging.info(f"{Bcolors.OKBLUE}Executing [{step_name}]{Bcolors.ENDC}")
        
        file_path = get_work_dir(config_setting.work_dir_scripts)
        file_name = "query_challenge_2.sql"
        file = (file_path / file_name).resolve()
        
        step_error, result = db_execute_from_files(config_setting, file)
        if not step_error:
            challenge_answer_2 = result[0]['result'][0][0]
            logging.info(f"{Bcolors.OKGREEN}challenge_answer_2 : {challenge_answer_2}{Bcolors.ENDC}")
        else:
            logging.error(f"{Bcolors.FAIL}challenge_answer_2 error: {step_error}{Bcolors.ENDC}")
        

    if not step_error:
        step_name = "validate_challenge"
        logging.info(f"{Bcolors.OKBLUE}Executing [{step_name}]{Bcolors.ENDC}")
        number_of_groups = challenge_answer_2
        answer = challenge_answer_1
        result = step_error = step_error_description = ""
        url_path_end_point = url_path_root + "/validate"
        
        step_error, step_error_description, result = challenge_validate(url_path_end_point, access_token, number_of_groups, answer)

        if result:
            logging.info(f"{Bcolors.OKGREEN}Validation successful. number_of_groups={number_of_groups}, answer={answer}{Bcolors.ENDC}")
        else:
            logging.info(f"{Bcolors.YELLOW}Validation fail for number_of_groups:{number_of_groups} & answer:{answer}{Bcolors.ENDC}")
            logging.info(f"{Bcolors.YELLOW}Error:{step_error} - Description: {step_error_description}{Bcolors.ENDC}")
            step_error = False

    if step_error:
        logging.error(f"{Bcolors.FAIL}{step_name} - error: {step_error}{Bcolors.ENDC}")



if __name__ == "__main__":
    try:
        logging.basicConfig(format='%(asctime)-23s | %(processName)-12s | %(name)-12s | %(levelname)7s : %(message)s', level=logging.INFO)

        step_name = "ConfigSetting"
        logging.info(f"{Bcolors.OKBLUE}Executing [{step_name}]{Bcolors.ENDC}")

        exec_dir = Path(__file__).parent
        config_ini = (exec_dir / 'config.ini').resolve()

        config_setting = ConfigSettings(config_ini, None)

        main()

    except Exception as e:
        logging.error(f"{Bcolors.FAIL}{e}{Bcolors.ENDC}")

    finally:
        container_name = config_setting.db_docker_container_name
        remove_container(container_name)