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

from applications.create_tax import app_create_tax
from applications.pay_tax import app_pay_tax
from applications.payables import app_payables
from applications.transactions import app_transactions

# Instancio el servicio Flask
app = Flask(__name__)
# Instancio la conexion a la DB
conexion = MySQL(app)


# ENDPOINT POST para registrar uns nueva boleta de pago
@app.route('/create-tax', methods=['POST'])
def create_tax():
    req = request.get_json(force=True)
    return app_create_tax(req)

# ENDPOINT POST para efectuar el pago de un impuesto
@app.route('/pay-tax', methods=['POST'])
def pay_tax():
    req = request.get_json(force=True)
    return app_pay_tax(req)


# ENDPOINT POST para listar las boletas impagas según se detalle el tipo de servicio a consultar, o no.
@app.route('/payables', methods=['POST'])
def payables():
    req = request.get_json(force=True)
    return app_payables(req)


# ENDPOINT POST para listar los pagos (TRANSACCIONES) entre un periodo de fechas
@app.route('/transactions', methods=['POST'])
def transactions():
    req = request.get_json(force=True)
    return app_transactions(req)



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
