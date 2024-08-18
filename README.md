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
| 1     | [Primera_reunion_Analisis_de_requerimientos.png](./communications/Primera_reunion_Analisis_de_requerimientos.png) | Captura de pantalla de la primera reunión de análisis de requerimientos. | PNG | Jorge Zambrano, Lizbeth Peña, Alejandra Cotrina, Cliente | 2024-06-19 | 10:18 PM |
| 2     | [campos_productos.xlsx](./communications/campos_productos.xlsx) | Documento que contiene la explicación de campos para los productos y elaboración de tablas. | Excel | Jorge Zambrano, Lizbeth Peña, Alejandra Cotrina, Cliente | 2024-06-23 | 04:15 PM |
| 3     | [Reunion_avances.png](./communications/Reunion_avances.png) | Se presentaron concepto de ventanas de la plataforma dentro de figma| PNG | Jorge Zambrano, Lizbeth Peña, Alejandra Cotrina | 2024-07-05 | 11:00 PM |
| 4     | [Recepcion_de_datos.jpg](./communications/Recepcion_de_datos.jpg) | El cliente nos proporcionó datos para continuar con el desarrollo | JPG | Jorge Zambrano, Lizbeth Peña, Alejandra Cotrina, Cliente | 2024-07-15 | 05:00 PM |
| 5     | [Reunion_de_avances.png](./communications/Reunion_de_avances.png) | Se presentaron pantallas funcionaes de la plataforma | PNG | Alejandra Cotrina, Cliente | 2024-07-28 | 08:00 PM |
| 6     | [Reunion_para_avances.png](./communications/Reunion_para_avances.png) | Se mostraron las pantallas de la plataforma hechas hasta el momento y ver su funcionalidad | PNG | Jorge Zambrano, Lizbeth Peña, Alejandra Cotrina, Cliente | 2024-08-10 | 10:00 PM |
| 7     | [Presentacion.jpg](./communications/Presentacion.jpg) <br> [Manual_de_Instalacion_Sistema.pdf](./communications/Manual_de_Instalacion_Sistema.pdf)  | Presentacion de las diferentes partes desarrolladas dentro de la plataforma. Se indicaron informacion de sitios desplegados y la entrega del manual de instalación | JPG <br> PDF | Jorge Zambrano, Lizbeth Peña, Alejandra Cotrina, Cliente | 2024-08-14 | 10:00 PM |
