def app_transactions(req):
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
        # valido que no haya ningún dato vacío
        campo_vacio = [p for p in req["transactions"] if req["transactions"][p] == ""]
        if len(campo_vacio) > 0:
            return jsonify({"message": f"El campo {campo_vacio[0]} no puede estar vacío", "error": 1.1})
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