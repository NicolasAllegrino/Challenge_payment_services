"""
API REST de una versión súper simplificada de un proveedor de servicios de pago de impuestos.
Desarrollada para el Desafio Back-end de New Combin

Author: Allegrino Nicolás
"""

#Librerías requeridas
from flask import Flask, jsonify, request
from config import config
from flask_mysqldb import MySQL
from datetime import datetime

# Instancio el servicio Flask
app = Flask(__name__)
# Instancio la conexion a la DB
conexion = MySQL(app)


# ENDPOINT POST para registrar uns nueva boleta de pago
@app.route('/create-tax', methods=['POST'])
def create_tax():
    """
    Recibo como parámetro un JSON con los datos de la boleta a cargar
    ESTRUCTURA DEL JSON =
                        {
                            "create_tax":
                            {
                                "tipo_de_servicio": "STRING",
                                "descripcion_del_servicio": "STRING",
                                "importe_del_servicio": FLOAT,
                                "fecha_de_vencimiento": "DATE",
                                "status_del_pago": "STRING"
                            }
                        }
    :return: Retorno un JSON con información del resultado del proceso al registrar la boleta
            ESTRUCTURA DEL JSON DE RESPUESTA =
                                            {
                                                "create_tax":
                                                {
                                                    "codigo_de_barra": INT
                                                }
                                                "message": "STRING",
                                                "error": INT
                                            }
            :create_tax: Si la boleta se creo correctamente, envío el codigo_de_barra correspondiente a la boeta
            :message: Describe el mensaje de respuesta
            :error: Describe el número de error. Si no surgió ningún error -> "error": 0 (error interno para determinar en dónde se originó)
    """

    try:
        req = request.get_json(force=True)
        req_keys = list(req["create_tax"].keys())
        req_values = list(req["create_tax"].values())

        #valido que no haya ningún dato vacío
        if "" in req_values:
            index_vacio = req_values.index("")
            return jsonify({"message": f"El valor de {req_keys[index_vacio]} no puede estar vacío.", "error": 1.1})

        #Valido que el importe del servicio a cargar sea mayor a 0
        elif req["create_tax"]["importe_del_servicio"] <= 0:
            return jsonify({"message": "El importe del servicio debe ser mayor a 0", "error": 1.2})
        else:
            #Convierto fecha_de_vencimiento en formato 'AAAA-MM-DD'
            req["create_tax"]["fecha_de_vencimiento"] = req["create_tax"]["fecha_de_vencimiento"].replace("/", "-")
            req["create_tax"]["fecha_de_vencimiento"] = datetime.strptime(req["create_tax"]["fecha_de_vencimiento"], '%Y-%m-%d')

            #Preparo y ejecuto la consulta a la BD para guardar el registro
            sql = f"""INSERT INTO payables (tipo_de_servicio, descripcion_del_servicio, importe_del_servicio, fecha_de_vencimiento, status_del_pago)
                                VALUES ('{req["create_tax"]["tipo_de_servicio"]}', '{req["create_tax"]["descripcion_del_servicio"]}',
                                {req["create_tax"]["importe_del_servicio"]}, '{req["create_tax"]["fecha_de_vencimiento"]}', '{req["create_tax"]["status_del_pago"]}')"""
            cursor = conexion.connection.cursor()
            cursor.execute(sql)

            # Consulto el codigo_de_barra del último registro
            sql_get_last_codigo_de_barra = "SELECT MAX(codigo_de_barra) FROM payables"
            cursor = conexion.connection.cursor()
            cursor.execute(sql_get_last_codigo_de_barra)
            result = cursor.fetchone()
            create_tax = {"codigo_de_barra": result[0]}

            conexion.connection.commit()
            return jsonify({"create_tax": create_tax, "message": "Se ha registrado correctamente la boleta de pago.", "error": 0})
    except Exception as Err:
        return jsonify({"message": f"Ha ocurrido un error al crear la boleta de pago.{Err}", "error": 1.0})


# ENDPOINT POST para efectuar el pago de un impuesto
@app.route('/pay-tax', methods=['POST'])
def pay_tax():
    """
    Recibo como parámetro un JSON con los datos para efectuar el pago de una boleta
    ESTRUCTURA DEL JSON =
                        {
                            "pay_tax":
                            {
                                "metodo_de_pago": "STRING",
                                "numero_de_tarjeta": "STRING",
                                "importe_del_pago": FLOAT,
                                "codigo_de_barra": BIGINT,
                                "fecha_de_pago": "DATE"
                            }
                        }

    :return: Retorno un JSON con información del resultado del proceso al efectuar el pago de la boleta
            ESTRUCTURA DEL JSON DE RESPUESTA =
                                            {
                                                "message": "STRING",
                                                "error": INT
                                            }
            :message: Describe el mensaje de respuesta
            :error: Describe el número de error. Si no surgió ningún error -> "error": 0 (error interno para determinar en dónde se originó)
    """

    try:
        req = request.get_json(force=True)
        req_keys = list(req["pay_tax"].keys())
        req_values = list(req["pay_tax"].values())

        # valido que no haya ningún dato vacío
        if "" in req_values:
            index_vacio = req_values.index("")
            #Si el pago se efectúa con tarjeta, el numero_de_tarjeta no debe estar vacío
            if (str(req["pay_tax"]["metodo_de_pago"]) != 'cash') and (str(req_keys[index_vacio]) == "numero_de_tarjeta"):
                msj = f"Si abona con tarjeta, el valor de {req_keys[index_vacio]} no puede estar vacío."
                return jsonify({"message": msj, "error": 2.1})
            else:
                msj = f"El valor de {req_keys[index_vacio]} no puede estar vacío."
                return jsonify({"message": msj, "error": 2.2})

        # Valido que el importe del pago sea mayor a 0
        #NOTA: También se podría considerar que importe_del_pago sea igual al importe_del_servicio de la boleta que corresponde
        elif req["pay_tax"]["importe_del_pago"] <= 0:
            return jsonify({"message": "El importe del pago debe ser mayor a 0", "error": 2.2})

        # Convierto fecha_de_pago en formato 'AAAA-MM-DD'
        req["pay_tax"]["fecha_de_pago"] = req["pay_tax"]["fecha_de_pago"].replace("/", "-")
        req["pay_tax"]["fecha_de_pago"] = datetime.strptime(req["pay_tax"]["fecha_de_pago"], '%Y-%m-%d')

        # Preparo y ejecuto la consulta a la BD
        sql = f'SELECT status_del_pago FROM payables WHERE  codigo_de_barra = {req["pay_tax"]["codigo_de_barra"]}'
        cursor = conexion.connection.cursor()
        cursor.execute(sql)
        status_pago = cursor.fetchone()
        conexion.connection.commit()

        #Valido si existe la boleta a abonar
        if status_pago == None:
            return jsonify({"message": f"NO existe la boleta con el código de barra: {req['pay_tax']['codigo_de_barra']}.", "error": 0})
        # Valido si la boleta ya fue abonada o no
        elif 'paid' in status_pago:
            return jsonify({"message": f"La boleta {req['pay_tax']['codigo_de_barra']} ya fue pagada.", "error": 0})
        else:
            # Determino el N° de la tarjeta si el pago se efectúa con tarjeta, caso contrario envío vacío
            nro_tarjeta = "" if req["pay_tax"]["metodo_de_pago"] == "cash" else req["pay_tax"]["numero_de_tarjeta"]

            # Preparo y ejecuto la consulta a la BD para registrar el pago (transaccion)
            sql = f"""INSERT INTO transactions (metodo_de_pago, numero_de_tarjeta, importe_del_pago, codigo_de_barra, fecha_de_pago)
                        VALUES('{req["pay_tax"]["metodo_de_pago"]}', '{nro_tarjeta}', '{req["pay_tax"]["importe_del_pago"]}',
                                '{req["pay_tax"]["codigo_de_barra"]}', '{req["pay_tax"]["fecha_de_pago"]}')"""
            cursor = conexion.connection.cursor()
            cursor.execute(sql)

            # Preparo y ejecuto la consulta a la BD para cambiar el estado de la boleta abonada a 'paid'
            sql = f"""UPDATE payables SET status_del_pago = 'paid' WHERE codigo_de_barra = '{req["pay_tax"]["codigo_de_barra"]}'"""
            cursor = conexion.connection.cursor()
            cursor.execute(sql)

            conexion.connection.commit()
            return jsonify({"message": "Se ha registrado correctamente el pago de la boleta.", "error": 0})

    except Exception as Err:
        return jsonify({"message": f"Ha ocurrido un error al efectuar el pago de la boleta.{Err}", "error": 2.0})


# ENDPOINT POST para listar las boletas impagas según se detalle el tipo de servicio a consultar, o no.
@app.route('/payables', methods=['POST'])
def payables():
    """
    Recibo como parámetro un JSON con los datos para listar las bletas impagas
    ESTRUCTURA DEL JSON =
                        {
                            "payables":
                            {
                                "tipo_de_servicio": "STRING"
                            }
                        }

    :return: Retorno un JSON con información del resultado al consultar las boletas
            ESTRUCTURA DEL JSON DE RESPUESTA =
                                            {
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
                                            }
            :payables: Lista las boletas impagas (si las hay).
            :message: Describe el mensaje de respuesta
            :error: Describe el número de error. Si no surgió ningún error -> "error": 0  (error interno para determinar en dónde se originó)
    """

    try:
        req = request.get_json(force=True)
        filtro = req["payables"]["tipo_de_servicio"]
        sql1 = ""
        sql2 = ""
        #Valido si la consulta se realiza con filtro de tipo_de_servicio o no
        if filtro != "SIN FILTRO" and filtro != "":
            sql1 = ", tipo_de_servicio"
            sql2 = " AND tipo_de_servicio = '" + filtro + "'"

        # Preparo y ejecuto la consulta a la BD
        sql = "SELECT fecha_de_vencimiento, importe_del_servicio, codigo_de_barra" + sql1 + " FROM payables WHERE status_del_pago <> 'paid'" + sql2
        cursor = conexion.connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        #Valido si se encontraron registro o no
        if result == ():
            conexion.connection.commit()
            return jsonify({"message": "No se encontraron datos en su solicitud", "error": 0})
        else:
            #Preparo la lista con las boletas impagas
            list_payables = []
            for data in result:
                if filtro != "SIN FILTRO" and filtro != "":
                    payable = {"fecha_de_vencimiento": datetime.strftime(data[0], '%Y-%m-%d'),
                               "importe_del_servicio": data[1], "codigo_de_barra": data[2], "tipo_de_servicio": data[3]}
                else:
                    payable = {"fecha_de_vencimiento": datetime.strftime(data[0], '%Y-%m-%d'),
                               "importe_del_servicio": data[1], "codigo_de_barra": data[2]}
                list_payables.append(payable)
            conexion.connection.commit()
            return jsonify({"payables": list_payables, "message": "Success", "error": 0})

    except Exception as Err:
        return jsonify({"message": f"Ha ocurrido un error al consultar las boletas impagas.", "error": 3.0})


# ENDPOINT POST para listar los pagos (TRANSACCIONES) entre un periodo de fechas
@app.route('/transactions', methods=['POST'])
def transactions():
    """
    Recibo como parámetro un JSON con los datos para listar los pagos (transacciones),
    entre un período de fechas, acumulando por día.
    ESTRUCTURA DEL JSON =
                        {
                            "transactions":
                            {
                                "fecha_desde": "DATE",
                                "fecha_hasta": "DATE"
                            }
                        }
    :return: Retorno un JSON con información del resultado al consultar las transacciones
            ESTRUCTURA DEL JSON DE RESPUESTA =
                                            {
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
                                            }
            :transacciones: Lista los pagos realizados entre las fechas solicitadas.
                :fecha_de_pago: Fecha en la que se efectuó el pago de la boleta
                :importe_acumulado: Suma de los importes de los pagos efectuados con la misma fecha_de_pago
                :cantidad_de_transacciones: Cantidad de pagos efectuados en la fecha_de_pago
            :message: Describe el mensaje de respuesta
            :error: Describe el número de error. Si no surgió ningún error -> "error": 0  (error interno para determinar en dónde se originó)
    """

    try:
        req = request.get_json(force=True)
        req_keys = list(req["transactions"].keys())
        req_values = list(req["transactions"].values())

        # valido que no haya ningún dato vacío
        if "" in req_values:
            index_vacio = req_values.index("")
            return jsonify({"message": f"El valor de {req_keys[index_vacio]} no puede estar vacío.", "error": 4.1})
        else:
            # Convierto las fechas de consulta desde y hasta en formato 'AAAA-MM-DD'
            desde = req["transactions"]["fecha_desde"].replace("/", "-")
            desde = datetime.strptime(desde, '%Y-%m-%d')
            hasta = req["transactions"]["fecha_hasta"].replace("/", "-")
            hasta = datetime.strptime(hasta, '%Y-%m-%d')

            # Preparo y ejecuto la consulta a la BD
            sql = f"SELECT fecha_de_pago, sum(importe_del_pago), count(id) FROM transactions GROUP BY fecha_de_pago BETWEEN '{desde}' AND '{hasta}'"
            cursor = conexion.connection.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()

        # Valido si se encontraron registro o no
        if result == ():
            conexion.connection.commit()
            return jsonify({"message": "No se encontraron datos en su solicitud", "error": 0})
        else:
            # Preparo la lista con los pagos efectuados (transacciones)
            transactions = []
            for data in result:
                transaction = {"fecha_de_pago": datetime.strftime(data[0], '%Y-%m-%d'), "importe_acumulado": data[1], "cantidad_de_transacciones": data[2]}
                transactions.append(transaction)

            conexion.connection.commit()
            return jsonify({"transactions": transactions, "message": "Success", "error": 0})

    except Exception as Err:
        return jsonify({"message": f"Ha ocurrido un error al consultar los pagos efectuados.", "error": 4.0})


# Establezco la respuesta cuando no existe el endpoint solicitado
def pagina_no_encontrada(error):
    return jsonify({'message': "URL no encontrada", 'status': 404})

# Ejecucion del servicio Flask
if __name__ == '__main__':
    # Configuraciones
    app.config.from_object(config['development'])
    # Handler NOT FOUND
    app.register_error_handler(404, pagina_no_encontrada)
    # Inicio la App
    app.run()