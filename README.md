# Backend Store

## Descripción

Backend Store es una aplicacion que funciona como el api para la tienda online.

## Proceso de instalacion

### Pre requisitos

* Python = 3.12.4
* Pip

### Intalacion

1. Clonar el proyecto
   ```
   git clone https://github.com/StoreDevApps/bk_store.git
   ```
2. Si no se tiene instalado virtualenv
   ```
   pip install virtualenv
   ```
3. Si no se tiene creado el entorno vitual
   ```
   python -m virtualenv env
   ```
4. Activar el entorno virtual (Si ya se lo tiene creado, omitir paso 2 y 3)
   ```
   virtualenv env
   ```
   Si no funciona de la forma anterior
   ```
   .\env\Scripts\activate
   ```
5. Instalar los requerimientos
   ```
   pip install -r requirements.txt
   ```
6. Migrar la base de datos
   ```
   python manage.py migrate
   ```


9. Iniciar el servidor de django
   ```
   python manage.py runserver
   ```

### Otros comandos de administración

* Para iniciar el servidor de desarrollo
   ```
   python manage.py runserver
   ```

* Para aplicar los cambios de los modelos creados en la migración
   ```
   python manage.py makemigrations
   ```

* Para crear superusuarios django admin
   ```
   python manage.py createsuperuser
   ```
* Para ejecutar test
   ```
   python manage.py test

* Si se instala un nuevo requerimiento, se debe actualizar el archivo requirements.txt
   ```
   pip freeze > requirements.txt
   ```


## Tabla de Contenido - Carpeta de Comunicaciones

Este documento indexa todas las piezas de evidencia dentro de la carpeta de comunicaciones, proporcionando detalles clave sobre cada archivo, incluyendo su nombre, descripción, tipo, participantes, fecha y hora.

| **#** | **Nombre del Archivo** | **Descripción** | **Tipo de Archivo** | **Participantes** | **Fecha** | **Hora** |
|-------|------------------------|-----------------|---------------------|-------------------|-----------|----------|
| 1     | reunion_inicial.pdf     | Acta de la reunión inicial donde se discutieron los requerimientos y el plan de proyecto. | PDF | Juan Pérez, María Gómez, Equipo de Desarrollo | 2024-07-01 | 09:00 AM |


**Nota:** Esta tabla se actualizará continuamente a medida que se agreguen nuevos archivos y evidencias al proyecto.
