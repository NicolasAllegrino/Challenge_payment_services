def app_create_tax(req):
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
        # valido que no haya ningún dato vacío
        campo_vacio = [p for p in req["create_tax"] if req["create_tax"][p] == ""]
        if len(campo_vacio) > 0:
            return jsonify({"message": f"El campo {campo_vacio[0]} no puede estar vacío", "error": 1.1})

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