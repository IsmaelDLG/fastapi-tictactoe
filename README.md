# TicTacToe

API Rest para jugar al tres en raya.

Para ejecutar el servidor hace falta instalar las dependencias (requirements.txt), declarar las variables de entorno necesarias y inicializar la BBDD. Para más info, ver el apartado de [Instalación](#instalación).

## Instalación

1. Definir variables de entorno
2. Instalar dependencias
3. Inicializar BBDD
4. Arrancar servidor

Ejemplo en windows:

```cmd
cd <root-del-repositorio>
:: Definir variables de entorno
(
echo DB_PATH=./sqlite3.db
echo JWT_EXPIRE_MINUTES=60
echo JWT_SECRET=Secret12345
echo JWT_ALGO=HS256
)>".env"
:: Crear entorno virtual
py -3 -m virtualenv venv 
:: Activarlo  
venv\Scripts\activate.bat
:: Instalar dependencias en el entorno
pip install -r requirements.txt
:: Iniciar BBDD
alembic upgrade head
:: Iniciar servidor
uvicorn app.main:app
```

### Variables de entorno

 - DB_PATH: path en el que se guardará la BBDD sqlite3
 - JWT_EXPIRE_MINUTES: tiempo de expiración de los JWT
 - JWT_SECRET: secret para encriptar los tokens
 - JWT_ALGO: algoritmo de encriptación. Ver https://pyjwt.readthedocs.io/en/stable/algorithms.html

## Tests

Para lanzar los tests del proyecto, es suficiente con utilizar el comando `pytest`. Ejemplo de ejecución:

```cmd
(venv) D:\myRepos\fastapi-tictactoe>pytest
================================= test session starts =================================
platform win32 -- Python 3.11.5, pytest-7.4.0, pluggy-1.3.0
rootdir: D:\myRepos\fastapi-tictactoe
plugins: anyio-4.0.0
collected 17 items

app\tests\test_games.py .........                                                [ 52%]
app\tests\test_main.py .                                                         [ 58%] 
app\tests\test_moves.py ....                                                     [ 82%]
app\tests\test_users.py ...                                                      [100%]

================================= 17 passed in 3.64s ================================== 

(venv) D:\myRepos\fastapi-tictactoe>
```

## Uso

Se puede interactuar con la API de muchas maneras, pero recomiendo utilizar Swagger. Se puede acceder a este en el path `/docs`. Ejemplo: `http://127.0.0.1:8000/docs`

