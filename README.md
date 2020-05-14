# dashboard-covid-espania
Dashboard de Python hecho con Dash. Url: https://coronavirus-resumen.herokuapp.com/

Obtiene los datos de la web de la Johns Hopkins University https://coronavirus.jhu.edu/

Mi web personal donde publico sobre ciencia de datos: https://machinelearningparatodos.com/

## PARA PROBAR EN LOCAL
1- Instalar dependencias

	$ pip install dash
	$ pip install plotly

2 - Cambiar el main de **app.py** 

Descomentar parte local, y comentar parte heroku

3 - Ejecutar **app.py**

	$ ./app.py

## PARA DESPLEGAR EN HEROKU

### 1 - Crear una carpeta para el proyecto

	$ mkdir dash_app_example
	$ cd dash_app_example

### 2 - Inicializar el repo con git y un entorno virtual

	$ git init        
	$ virtualenv venv 
	$ source venv/bin/activate 

### 3 - Instalar dependencias

	$ pip install dash
	$ pip install plotly
	$ pip install gunicorn

### 4 - Inicializar la carpeta con la app, un .gitignore, un Procfile y un fichero de requerimientos

- **.gitignore** tal cual en este repo
- **app.py** tal cual en este repo
- **Procfile** tal cual en este repo
- **requirements.txt**, depende de si se instalan más cosas. Mejor con 
	
		$ pip freeze > requirements.txt


### 5 - Inicializar heroku, añadir ficheros y desplegar

	$ heroku login # Necesario crear cuenta en Heroku
	$ heroku create nombre-app # Nombre de la app a crear
	$ git add . # Añadir todos los ficheros a git
	$ git commit -m 'Commit inicial'
	$ git push heroku master # Despliego

En cuentas gratis, heroku sólo da un dyno (contenedor), si tienes cuenta de pago, cambiar el 1 por el número de contenedores

	$ heroku ps:scale web=1  