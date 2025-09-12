from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from config.db import get_db_connection, mysql

# Crear el blueprint
tareas_bp = Blueprint("tareas", __name__)

# Crear un endpoint obtener tareas


@tareas_bp.route("/obtener", methods=["GET"])
@jwt_required()
def get():

    # Obtenemos la identidad del dueño del token
    user_id = get_jwt_identity()

    #Conectamos a la bd
    cursor = get_db_connection()

    #Ejecutar la consulta


    query = (
        " SELECT a.id_usuario, a.descripcion, b.nombre, b.email, a.creado_en"
        " FROM tareas AS a"
        " INNER JOIN usuarios AS b ON a.id_usuario = b.id_usuario"
        " WHERE a.id_usuario = %s"
    )

    cursor.execute(query, (user_id,))
    lista = cursor.fetchall()

    cursor.close()

    if not lista:
        return jsonify({"mensaje": "No tienes tareas creadas"}), 404
    else:
        return jsonify({"lista": lista}), 200

# Crear endpoint con post recibiendo datos desde el body


@tareas_bp.route("/crear", methods=["POST"])
@jwt_required()
def crear():
    # Obtener los datos del body

    data = request.get_json()

    descripcion = data.get("descripcion")

    if not descripcion:
        return jsonify({"error": "Debes teclear una descripcion"}), 400

    # Id del usuario autenticado desde el JWT
    user_id = get_jwt_identity()

    # Obtenemos el cursor
    cursor = get_db_connection()

    # Hacemos el insert
    try:
        cursor.execute(
            "INSERT INTO tareas (descripcion, id_usuario) values (%s, %s)",
            (descripcion, user_id),
        )
        cursor.connection.commit()
        return jsonify({"message": "Tarea creada"}), 201
    except Exception as e:
        return jsonify({"Error": f"No se pudo crear la tarea: {str(e)}"})
    finally:
        cursor.close()

# Crear endpoint usando PUT y pasando datos por el body y el url

@tareas_bp.route("/modificar/<int:tarea_id>", methods=["PUT"])
@jwt_required()
def modificar(tarea_id):

    # Obtenemos la identidad del dueño de la tarea
    current_user = get_jwt_identity()

    # Obtenemos los datos del body
    data = request.get_json()

    descripcion = data.get("descripcion")

    cursor = get_db_connection()

    query = "SELECT * FROM tareas WHERE id_tarea = %s"
    cursor.execute(query, (tarea_id,))
    tarea = cursor.fetchone()
    if not tarea:
        cursor.close()
        return jsonify({"error": "Tarea no encontrada"}), 404
    
    #Verificamos que la tarea pertenezca al usuario logueado
    
    if not tarea[1] == int(current_user):
        cursor.close()
        return jsonify({"error": "No tienes permiso para modificar esta tarea"}), 401
    
    # Actualizar los datos
    try:
        cursor.execute(
            "UPDATE tareas SET descripcion = %s WHERE id_tarea = %s",
            (descripcion, tarea_id),
        )
        cursor.connection.commit()
        return jsonify({"message": "Tarea modificada"}), 200

    except Exception as e:
        return jsonify({"error": f"No se pudo modificar la tarea: {str(e)}"}), 500

    finally:
        cursor.close()
