import json
import os
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "datos.json")


def cargar_datos():
  try:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  except (FileNotFoundError, json.JSONDecodeError):
    return []


def guardar_datos(registros):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(registros, f, ensure_ascii=False, indent=2)


@app.route("/")
def index():
  return render_template("index.html")


@app.route("/api/registros", methods=["GET"])
def obtener_registros():
  registros = cargar_datos()
  # Ordenar por ID numérico si es posible
  registros_ordenados = sorted(
      registros,
      key=lambda x: int(x["id"]) if str(x.get("id")).isdigit() else 999999,
  )

  ocupados = sum(
      1 for r in registros if str(r.get("estado", "")).lower() == "ocupado"
  )
  disponibles = sum(
      1 for r in registros if str(r.get("estado", "")).lower() == "disponible"
  )

  return jsonify({
      "registros": registros_ordenados,
      "stats": {"ocupados": ocupados, "disponibles": disponibles},
  })


@app.route("/api/guardar", methods=["POST"])
def guardar_o_reasignar():
  data = request.json
  rid = str(data.get("id", "")).strip()

  if not rid:
    return jsonify({"success": False, "message": "El ID es requerido"}), 400

  registros = cargar_datos()

  # Verificar si existe
  index_existente = -1
  for idx, r in enumerate(registros):
    if str(r.get("id")) == rid:
      index_existente = idx
      break

  if index_existente != -1:
    registros[index_existente] = data
    msg = f"El ID {rid} ha sido reasignado/actualizado correctamente."
  else:
    registros.append(data)
    msg = f"El ID {rid} ha sido creado correctamente."

  guardar_datos(registros)
  return jsonify({"success": True, "message": msg})


@app.route("/api/eliminar/<rid>", methods=["DELETE"])
def eliminar_registro(rid):
  registros = cargar_datos()
  registros = [r for r in registros if str(r.get("id")) != str(rid)]
  guardar_datos(registros)
  return jsonify(
      {"success": True, "message": f"El ID {rid} ha sido eliminado."}
  )


@app.route("/api/liberar/<rid>", methods=["PUT"])
def liberar_registro(rid):
  registros = cargar_datos()
  for r in registros:
    if str(r.get("id")) == str(rid):
      r["estado"] = "Disponible"
      r["nombre"] = ""
      r["apellido"] = ""
      r["observaciones"] = ""
      break
  guardar_datos(registros)
  return jsonify(
      {"success": True, "message": f"El ID {rid} ha sido liberado."}
  )


if __name__ == "__main__":
  # host='0.0.0.0' permite acceder desde el celular dentro de la misma red Wi-Fi
  app.run(host="0.0.0.0", port=5000, debug=True)