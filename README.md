# Foris.ai challenge <img src="https://www.foris.ai/img/logo-foris.svg" width="100" align="right">
Este proyecto resuelve en forma automátizada el desafio de la empresa **Foris.ai** para el puesto de **"Back-end Software Engineer"**
(https://www.getonbrd.com/empleos/programacion/back-end-software-engineer-foris-ai-remote-9155)

## Solución
Se base en código Python el cual implementa diferentes tecnologías para lograr resolver el desafio planteado.
* **requests**:
  Se utiliza para acceder a diferentes end point (descripto el desafio) para obtener datos para ir cumpliendo los pasos necesarios para resolver el desafío.
  Lo que se va obteniendo paso a paso son:
   - Datos para obtener el token bearer para autenticar sobre los end point
   - detalles de como continar el desafio
   - descarga del script para crear y poblar la base de datos
   - rutas y formatos para validar los resultados
* **docker**:
  Se utiliza para crear una base de datos temporal donde crear las tablas y realizar las consultas sql que dan respuestas al desafio.
* **mysql-connector**:
  El uso de 2 bibliotecas específicas (_mysql-connector_ y _mysql-connector-python_) permite la interacción con la base de datos MySQL (para este caso, la que está funcionando en el docker) para resolver los desafío.
  

## Requerimientos
Para poder ejecuta la aplicación y resolver el desafio necesitas:
* **Python 3** (https://www.python.org/downloads/) <img src="https://www.python.org/static/img/python-logo.png" width="100">
* **Docker** (https://www.docker.com/) <img src="https://www.docker.com/wp-content/uploads/2023/08/logo-guide-logos-1.svg" width="100">

## Pasos para ejecutar la solución
Descargar el código en el directorio que desees
_https://github.com/HugoRubenEspinosa/foris_challenge/archive/refs/heads/main.zip_

Crear un entorno virtual 
```
python -m venv venv
```
Activar el entorno virtual
```
./venv/Script/Activate
```
Instalar las dependencias 
```
pip install -r requirements.txt
```
Ejecutar la aplicacion 
```
python ./src/main.py
```
