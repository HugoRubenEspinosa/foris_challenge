import configparser
import logging.config

from Bcolors import Bcolors

#from ast import literal_eval

#datatypes = (tuple, int, float, set, dict, list)
config = configparser.ConfigParser()

class ConfigSettings:
    def __init__(self, config_ini, environment):
        try:
            config.read(config_ini)

            self.work_dir_documents = config['WORK_DIR']['DIR_DOCUMENTS']
            self.work_dir_scripts = config['WORK_DIR']['DIR_SCRIPTS']

            self.db_docker_container_name = config['DOCKER']['DOCKER_CONTAINER_NAME']
            self.db_docker_container_image = config['DOCKER']['DOCKER_CONTAINER_IMAGE']
            self.db_docker_db_engine = config['DOCKER']['DOCKER_DB_ENGINE']
            self.db_docker_db_port = config['DOCKER']['DOCKER_DB_PORT']

            if environment == None:             
                environment = self.db_docker_db_engine
            else:
                self.db_docker_db_engine = environment

            self.db_host = config[environment]['DB_HOST']
            self.db_port = config[environment]['DB_PORT']
            self.db_name = config[environment]['DB_NAME']
            self.db_user = config[environment]['DB_USER']
            self.db_password = config[environment]['DB_PASSWORD']
            self.db_dumps = config[environment]['DB_DUMPS']
            
            logging.info(f"{Bcolors.OKBLUE}File Config [{config_ini}] was loaded{Bcolors.ENDC}")

            logging.debug(f"{Bcolors.OKCYAN}db_docker_container_name: {self.db_docker_container_name}{Bcolors.ENDC}")
            logging.debug(f"{Bcolors.OKCYAN}db_docker_db_engine: {self.db_docker_db_engine}{Bcolors.ENDC}")
            logging.debug(f"{Bcolors.OKCYAN}db_docker_db_port: {self.db_docker_db_port}{Bcolors.ENDC}")

            
            logging.debug(f"{Bcolors.OKCYAN}db_host: {self.db_host}{Bcolors.ENDC}")
            logging.debug(f"{Bcolors.OKCYAN}db_port: {self.db_port}{Bcolors.ENDC}")
            logging.debug(f"{Bcolors.OKCYAN}db_name: {self.db_name}{Bcolors.ENDC}")
            logging.debug(f"{Bcolors.OKCYAN}db_user: {self.db_user}{Bcolors.ENDC}")
            logging.debug(f"{Bcolors.OKCYAN}db_password: {self.db_password}{Bcolors.ENDC}")


        except Exception as e:
            logging.warning(f"{Bcolors.FAIL}failed to read {config_ini}{Bcolors.ENDC}")
            logging.warning(f"{Bcolors.FAIL}{e}{Bcolors.ENDC}")
