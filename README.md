# Foris.ai challenge
Este proyecto resuelve en forma automática el desafio de la empresa Foris.ai para el puesto de "Back-end Software Engineer"
(https://www.getonbrd.com/empleos/programacion/back-end-software-engineer-foris-ai-remote-9155)

## Solución
Se base en código Python el cual implementa diferentes tecnologías para lograr resolver el desafio planteado.
* Requests: Se utiliza para obtiene de diferentes end point (descripto el desafio) información para ir cumpliendo los pasos necesarios, entre ellos:
 - Datos para obtener el token bearer,
 - definiciones del desafio,
 - script para crear y poblar la base de datos.
 - rutas para validar los resultados
* Docker: Se utiliza para crear una base de datos temporal donde crear las tablas y realizar las consultas sql que dan respuestas al desafio.

## Requerimientos
Para poder ejecuta la aplicación y resolver el desafio necesitas:
Python 3
Docker

## Pasos para ejecutar la solución
Descargar el código en el directorio que desees
https://github.com/HugoRubenEspinosa/foris_challenge/archive/refs/heads/main.zip

Crear un entorno virtual 
```
python -m venv venv
```
Instalar las dependencias 
```
pip install -r requirements.txt
```
Ejecutar la aplicacion 
```
python ./src/main.py
```
