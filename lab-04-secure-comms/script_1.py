import socket
import errno
import random
import datetime
import time
import ssl

HOST = "127.0.0.1"
PORT = 4055  # 4X5 con X=5

nombre_estudiante_1 = "Marina_Garcia_Navas_1"
nombre_estudiante_2 = "Marina_Garcia_Navas_2"

espera_1 = random.randint(1, 10)
print(f"[{nombre_estudiante_1}] Espera_1 = {espera_1} segundos")

# TLS context (cliente — verifica el certificado del servidor)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_verify_locations("certCA.pem")
context.check_hostname = False  # localhost no necesita hostname check

# 1. SOCKET
raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
raw_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    # 2. CONNECT + WRAP TLS
    cliente_socket = context.wrap_socket(raw_socket, server_hostname="127.0.0.1")
    cliente_socket.connect((HOST, PORT))
    print(f"[{nombre_estudiante_1}] Conexión TLS con Estudiante_2 establecida")

    # 3. SEND
    mensaje = f"{nombre_estudiante_2}: espera de {espera_1} segundos"
    print(f"[{nombre_estudiante_1}] Enviando: {mensaje}")
    cliente_socket.sendall(mensaje.encode("utf-8"))

    # 4. RECV
    respuesta = ""
    while True:
        recv = cliente_socket.recv(1024)
        if recv == b"":
            break
        respuesta += recv.decode("utf-8")
    print(f"[{nombre_estudiante_1}] Recibido: {respuesta}")

    # 5. PROCESAR respuesta
    if "fecha ->" in respuesta:
        try:
            partes = respuesta.split("->", 1)
            derecha = partes[1].strip()
            fecha_iso, e1, e2, e3 = derecha.split("|")

            fecha_actual = datetime.datetime.fromisoformat(fecha_iso)
            e1, e2, e3 = int(e1), int(e2), int(e3)

            print(f"[{nombre_estudiante_1}] Fecha recibida: {fecha_actual}")
            print(f"[{nombre_estudiante_1}] espera_1={e1}, espera_2={e2}, espera_3={e3}")

            # Comprobación 1
            print(f"[{nombre_estudiante_1}] Espero {e1} segundos...")
            time.sleep(e1)
            fecha1 = fecha_actual + datetime.timedelta(seconds=e1)
            print(f"[{nombre_estudiante_1}] espero {e1} segundos, computar la fecha {fecha_actual} con la espera_{e1} segundos -> {fecha1}")

            # Comprobación 2
            print(f"[{nombre_estudiante_1}] Espero {e2} segundos más...")
            time.sleep(e2)
            fecha2 = fecha_actual + datetime.timedelta(seconds=e1 + e2)
            print(f"[{nombre_estudiante_1}] espero {e1+e2} segundos, computar la fecha {fecha_actual} con la espera_{e2} segundos -> {fecha2}")

            # Comprobación 3
            print(f"[{nombre_estudiante_1}] Espero {e3} segundos más...")
            time.sleep(e3)
            fecha3 = fecha_actual + datetime.timedelta(seconds=e1 + e2 + e3)
            print(f"[{nombre_estudiante_1}] espero {e1+e2+e3} segundos, computar la fecha {fecha_actual} con la espera_{e3} segundos -> {fecha3}")

        except Exception as e:
            print(f"[{nombre_estudiante_1}] Error al interpretar la respuesta: {e}")

    # 6. SHUTDOWN
    cliente_socket.shutdown(socket.SHUT_WR)

except ssl.SSLError as e:
    print(f"[{nombre_estudiante_1}] SSL error: {e}")
except socket.error as e:
    if e.errno == errno.ECONNREFUSED:
        print(f"[{nombre_estudiante_1}] Conexión rechazada — ¿está script_2.py corriendo?")
    elif e.errno == errno.ETIMEDOUT:
        print(f"[{nombre_estudiante_1}] Timeout")
    else:
        print(f"[{nombre_estudiante_1}] Socket error: {e}")
finally:
    raw_socket.close()
    print(f"[{nombre_estudiante_1}] Conexión cerrada")
