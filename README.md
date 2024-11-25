# Foris.ai challenge <img src="https://www.foris.ai/img/logo-foris.svg" width="100" align="right">
Este proyecto resuelve en forma automátizada el desafio de la empresa **Foris.ai** para el puesto de **"Back-end Software Engineer"**
(https://www.getonbrd.com/empleos/programacion/back-end-software-engineer-foris-ai-remote-9155)

## Challenge
https://mini-challenge.foris.ai/

## Solución
Se base en código Python el cual implementa diferentes tecnologías para lograr resolver el desafio planteado.
* **requests**:
  Se utiliza para acceder a diferentes end point (descripto el desafio) para obtener datos para ir cumpliendo los pasos necesarios para resolver el desafío.
  Lo que se va obteniendo paso a paso son:
   - Datos para obtener el token bearer para autenticar sobre los end point
   - detalles de como continuar el desafio (pasos)
   - descarga del script para crear y poblar la base de datos
   - rutas (path) y formatos para validar los resultados
* **docker**:
  Se utiliza para crear una base de datos temporal donde crear las tablas y realizar las consultas sql que dan respuestas al desafio.
* **mysql-connector**:
  El uso de 2 bibliotecas específicas (_mysql-connector_ y _mysql-connector-python_) permite la interacción con la base de datos MySQL (para este caso, la que está funcionando en el docker) para resolver los desafío.
  

## Requerimientos
Para poder ejecuta la aplicación y resolver el desafio necesitas:
* **Python 3** (https://www.python.org/downloads/) <img src="https://www.python.org/static/img/python-logo.png" width="100">
* **Docker** (https://www.docker.com/) <img src="https://www.docker.com/wp-content/uploads/2023/08/logo-guide-logos-1.svg" width="100">

## Pasos para ejecutar la solución
Descargá y descomprimí el código en el directorio que desees
_https://github.com/HugoRubenEspinosa/foris_challenge/archive/refs/heads/main.zip_

Abrí una consola en el directorio seleccionado

Creá un entorno virtual (simplemente para mantener ordenadas las dependencias)
```
python -m venv venv
```
Activá el entorno virtual
```
./venv/Scripts/Activate  |  ./venv/Scripts/activate.bat (Windows)
```
Actualizá el comando _pip_
```
python -m pip install --upgrade pip
```
Instalá las dependencias 
```
pip install -r requirements.txt
```
Ejecutá la aplicacion 
```
python ./src/main.py
```
## Personalizaciones
En el caso que necesites realizar cambios relacionados al entorno de ejecución, modificá el archivo ```./src/config.ini```. 

Si deseas modificar las consultas (query) a la base de datos podés modificar los archivos ```./sql/query_challenge_1.sql``` y ```./sql/query_challenge_2.sql```
