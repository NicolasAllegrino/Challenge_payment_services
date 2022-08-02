def app_payables(req):
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