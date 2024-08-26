from flask import jsonify, request, Flask
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)  # Habilitar CORS para permitir solicitudes desde diferentes dominios

# Cargar los archivos CSV
main_data = pd.read_csv("DB/main.csv")
main_json = main_data.to_dict(orient="records")

@app.route('/')
def simple_test():
    return jsonify({
        "message": "This is a simple test"
    })

# Ruta para obtener productos por ID usando la URL /products/<int:product_id>
@app.route('/products/<int:product_id>')
def get_productos(product_id):
    producto_found = [product for product in main_json if product['PRODUCTO_ID'] == product_id]
    if len(producto_found) > 0:
        response = jsonify({"records": producto_found})
        response.headers.add('Content-Type', 'application/json')
        return response
    else:
        return jsonify({"message": "Product not found"}), 404

# Ruta para ejecutar código basado en el ID del producto usando la URL /product/<int:producto_id>
@app.route('/product/<int:producto_id>')
def run_code(producto_id):
    # Verificar si el producto existe
    if producto_id not in main_data['PRODUCTO_ID'].values:
        return jsonify({"message": "Product not found"}), 404

    # Obtener el nombre del producto correspondiente al ID ingresado
    nombre_producto = main_data[main_data['PRODUCTO_ID'] == producto_id]['PRODUCTO'].values[0]

    # Filtrar las filas correspondientes al producto especificado en la base de datos principal
    producto_data = main_data[main_data['PRODUCTO_ID'] == producto_id]

    # Añadir una columna de interpretación basada en la columna '%_VARIACION'
    def interpretar_variacion(row):
        if pd.isna(row['%_VARIACION']):
            return "El precio se ha mantenido estable."
        elif row['%_VARIACION'] > 0:
            return "El precio ha subido."
        elif row['%_VARIACION'] < 0:
            return "El precio ha bajado."
        else:
            return "El precio se ha mantenido estable."

    producto_data['Interpretación'] = producto_data.apply(interpretar_variacion, axis=1)

    # Convertir los datos filtrados a JSON para responder la solicitud
    producto_json = producto_data.to_dict(orient='records')

    response = jsonify({
        'nombre_producto': nombre_producto,
        'datos_producto': producto_json
    })
    response.headers.add('Content-Type', 'application/json')
    return response, 200

# Inicialización del servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
