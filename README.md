# Backend Store

## Proceso de instalacion

### Pre requisitos

* Python
* Pip

### Intalacion

1. git clone https://github.com/AntonellaDevApps/antonellaBk.git
2. pip install virtualenv

3. virtualenv env (Cada vez que se quiera volver a trabajar y ya se tenga instalado todo, iniciar desde aqui)
   python -m virtualenv env (si no funciona de la forma anterior, escribirlo de esta manera)
4. .\env\Scripts\activate
5. pip install -r requirements.txt
6. python manage.py migrate

Para iniciar el servidor de desarrollo
* python3 manage.py runserver 

o

* python manage.py runserver 

Para crear superusuarios django admin
*  python manage.py createsuperuser
