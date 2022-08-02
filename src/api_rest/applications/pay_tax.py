def app_pay_tax(req):
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
        # valido que no haya ningún dato vacío
        campo_vacio = [p for p in req["pay_tax"] if req["pay_tax"][p] == ""]
        if len(campo_vacio) > 0:
            if (('card' in req["pay_tax"]["metodo_de_pago"]) and ("numero_de_tarjeta" in campo_vacio)):
                return jsonify({"message": f"El valor de {campo_vacio[0]} no puede estar vacío.", "error": 2.2})
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