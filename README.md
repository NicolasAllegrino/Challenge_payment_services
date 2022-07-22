# Challenge de New Combin
API REST de una versión súper simplificada de un proveedor de servicios de pago de impuestos.<br>
Desarrollada en Python para el Desafio Back-end de New Combin (el mismo se puede consultar <a href="https://github.com/newcombin/devskillsback">aquí</a>)

## Pasos y configuraciones para ejecutar la API REST
Descargar el directorio Challenge_payment_services en la hubicación que prefieran.<br>

### Base de Datos
Esta API REST está desarrollada utilizando una Base de Datos de MySQL<br>
Para crear la  base de datos y sus tablas, copiar y ejecutar en su gestor de Base de Datos MySQL (En mi caso he utilizado MySQL Workbench) los comandos del archivo DB.txt que se encuentra en el directorio: ...\Challenge_payment_services\DataBase\<br>
Una vez creada la base de datos, se deberán establecer los atributos de conexión a la misma en el archivo:  ...\Challenge_payment_services\src\api_rest\config.py<br>
Abrir el archivo config.py en un editor de texto y completar los atributos con los siguientes datos:<br>
   * MYSQL_HOST = 'localhost' (ó el nombre de HOST de su equipo)
   * MYSQL_USER = 'root'  (ó el nombre de usuario de su gestor de Base de Datos MySQL)
   * MYSQL_PASSWORD = 'CONTRASEÑA' (colocar la contraseña de su conexión a la Base de Datos)

> NOTA: los demás parámetros no modificarlos

### Iniciar la API REST en entorno virtual
Abrir la consola de comandos y posicionarde en el directorio raíz Challenge_payment_services.<br>
Ya posicionados en ese directorio, ingresamos .\env\Scripts\activate, quedando, por ejemplo:<br>
...\Challenge_payment_services>.\env\Scripts\activate<br>
y aceptamos, y en la siguiente línea tiene que aparecer primero con (env) ...\Challenge_payment_services> (Ya habremos iniciado el entorno virtual de Python)<br>
Luego ejecutamos: py .\src\api_rest\app.py<br>
...\Challenge_payment_services>py .\src\api_rest\app.py<br>
Con eso ya debería de estar funcionando el servicio de Flask localmente...<br>
Si no surge ningún error, debería imprimirle por pantalla datos como los siguientes:<br>
 * Serving Flask app 'app' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://127.0.0.1:5000 
> Esta URL puede variar según su equipo. Es la que se utilizará para consumir la API (URL REQUEST)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 100-898-847


## Endpoints del servicio de la API
### 1. Para crear una boleta de pago
 * endpoint: /create-tax
 * methods: POST
 * data request: JSON = {
                            "create_tax":
                            {
                                "tipo_de_servicio": "STRING",
                                "descripcion_del_servicio": "STRING",
                                "importe_del_servicio": FLOAT,
                                "fecha_de_vencimiento": "DATE",
                                "status_del_pago": "STRING"
                            }
                        }
 * data response: JSON = {
                                                "create_tax":   (Se excluye si no se registró correctamente la boleta)
                                                {
                                                    "codigo_de_barra": INT
                                                }
                                                "message": "STRING",
                                                "error": INT
                                            }<br>
`create_tax`: Si la boleta se creo correctamente, envío el codigo_de_barra correspondiente a la boeta<br>
`message`: Describe el mensaje de respuesta<br>
`error`: Describe el número de error. Si no surgió ningún error -> "error": 0 (error interno para determinar en dónde se originó)<br>

### 2. Para efectuar el pago de un impuesto
 * endpoint: /pay-tax
 * methods: POST
 * data request: JSON = {
                            "pay_tax":
                            {
                                "metodo_de_pago": "STRING",
                                "numero_de_tarjeta": "STRING",
                                "importe_del_pago": FLOAT,
                                "codigo_de_barra": BIGINT,
                                "fecha_de_pago": "DATE"
                            }
                        }
 * data response: JSON = {
                                                "message": "STRING",
                                                "error": INT
                                            }<br>
`message`: Describe el mensaje de respuesta<br>
`error`: Describe el número de error. Si no surgió ningún error -> "error": 0 (error interno para determinar en dónde se originó)<br>

### 3. Para listar las boletas impagas según se detalle el tipo de servicio a consultar, o no.
 * endpoint: /payables
 * methods: POST
 * data request: JSON = {
                            "payables":
                            {
                                "tipo_de_servicio": "STRING"
                            }
                        }
 * data response: JSON = {
                                                "payables":
                                                [
                                                    {
                                                        "tipo_de_servicio": "STRING", (Se excluye si no se recibe ningún dato para filtrar)
                                                        "fecha_de_vencimiento": "DATE",
                                                        "importe_del_servicio": FLOAT,
                                                        "codigo_de_barra": BIGINT
                                                    },...
                                                ],
                                                "message": "STRING",
                                                "error": INT
                                            }<br>
`payables`: Lista las boletas impagas (si las hay).<br>
`message`: Describe el mensaje de respuesta<br>
`error`: Describe el número de error. Si no surgió ningún error -> "error": 0 (error interno para determinar en dónde se originó)<br>

### 4. Para listar los pagos (transacciones) entre un periodo de fechas
 * endpoint: /transactions
 * methods: POST
 * data request: JSON = {
                            "transactions":
                            {
                                "fecha_desde": "DATE",
                                "fecha_hasta": "DATE"
                            }
                        }
 * data response: JSON = {
                                                "transactions":
                                                [
                                                    {
                                                        "fecha_de_pago": "DATE",
                                                        "importe_acumulado": FLOAT,
                                                        "cantidad_de_transacciones": INT
                                                    },...
                                                ],
                                                "message": "STRING",
                                                "error": INT
                                            }<br>
`transactions`: Lista los pagos realizados entre las fechas solicitadas.<br>
                `fecha_de_pago`: Fecha en la que se efectuó el pago de la boleta<br>
                `importe_acumulado`: Suma de los importes de los pagos efectuados con la misma fecha_de_pago<br>
                `cantidad_de_transacciones`: Cantidad de pagos efectuados en la fecha_de_pago<br>
`message`: Describe el mensaje de respuesta<br>
`error`: Describe el número de error. Si no surgió ningún error -> "error": 0 (error interno para determinar en dónde se originó)<br>

## Consumir la API
Para probar y consumir los servicios de la API, se puede realizar mediante POSTMAN (por ejemplo)<br>
La consulta se realiza hacia la URL detallada arriba (URL REQUEST), seguido del endpoint requerido.<br>
> Por ejemplo: http://127.0.0.1:5000/transactions<br>
> NOTA: La URL puede variar según el equipo. Puede ser http://localhost:5000/... o también cambiar el valor :5000 por el en N° de su puesto configurado.

Las peticiones a la API se configuraron mediante methods POST<br>
Como data request en el Body de la consulta, se debe enviar un JSON con la estructura especificada en el data request de cada endpoint<br>
En el archivo data_test.txt dentro del directorio DataBase se encuentran algunos datos de pruebas correspondientes a cada endpoint
