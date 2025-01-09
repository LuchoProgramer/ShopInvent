# ShopInvent Backend

**Descripción:** Este es el backend de la aplicación ShopInvent, construido con Django y Django Tenants
para proporcionar una solución de gestión de inventario multi-tenant.

## Características

* **API REST:**  Proporciona una API RESTful para que el frontend pueda interactuar con los datos.
* **Multi-tenant:**  Soporta múltiples tiendas (tenants) con bases de datos separadas.
* **Autenticación:**  Cada tenant usara la autenticacion de Django y el panel de administracion
* **Modelos:**  Define modelos para productos, categorías, proveedores, clientes, ventas, etc.
* **Vistas:**  Implementa vistas para gestionar las operaciones CRUD de los modelos.
* **Serializadores:**  Serializa los datos para la API REST.

## Tecnologías

* **Lenguaje:** Python
* **Framework:** Django
* **Librería Multi-tenant:** Django Tenants
* **API REST:** Django REST Framework
* **Base de datos:** PostgreSQL
* **Contenedores:** Docker, Docker Compose

## Instalación

1. **Requisitos:**
    * Docker
    * Docker Compose

2. **Clonar el repositorio:**

   ```bash
   git clone [URL válida]

3. **Navegar a la carpeta del backend:**

    ```bash
    cd shopinvent/backend

4. **Iniciar los contenedores:**

    ```bash
    docker-compose up -d

## Configuración de Django Tenants

# Documentacion
    https://django-tenants.readthedocs.io/en/latest/install.html

1. **Instala django-tenants:**

    ```bash
    pip install django-tenants

* En mi caso yo cree la app empresas, aqui tengo el modelo que pertenece a la creacion de cada tenant que en mi caso seran las empresas, y tengo la informacion necesaria que luego usare para las distintas configuraciones como los reportes y todo eso.

* Revisa el archivo settings.py para obtener todas las configuraciones para este proyecto pero basicamente fueron las siguientes

    - Database Engine
    - Agrega DATABASE_ROUTERS
    - Agrega el MIDDLEWARE en el principio de los MIDDLEWARES 
    - Configura las App que se compartiran como SHARED_APP TENANT_APP E INSTALLED_APPS
    - EN SHARED_APPS es necesario poner django tenants y en mi caso empresas
    - Agrega TENANT_MODEL y TENANT_DOMAIN_MODEL
    - Ejecuta makemigrations y migrate
    - Crea los esquemas con create_tenant y llena los campos necesarios
    - Agrega el archivo urls publico
    - Agrega la linea PUBLIC_SCHEMA_URLCONF
    - Configurar el Admin
    - Crear SuperUsuario para Public con create superuser y para los Tenant con create_tenant_superuser
    - agrega urls_public para que puedas ingresar al admin de django en publico
    - agrega una mensajde de bienvenida o algo para ingresar a la ruta / vacia

