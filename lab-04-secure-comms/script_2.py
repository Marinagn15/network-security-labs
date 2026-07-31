import socket
import errno
import random
import datetime
import ssl

HOST2 = "127.0.0.1"
PORT2 = 4055  # 4X5 con X=5

HOST3 = "127.0.0.1"
PORT3 = 2405  # 24X con X=5

nombre_estudiante_1 = "Marina_Garcia_Navas_1"
nombre_estudiante_2 = "Marina_Garcia_Navas_2"
nombre_tercero = "Tercero"

espera_2 = random.randint(1, 10)
print(f"[{nombre_estudiante_2}] Espera_2 = {espera_2} segundos")

# TLS context como SERVIDOR (para Estudiante_1)
ctx_server = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx_server.load_cert_chain("cert.pem", "key.pem")
ctx_server.load_verify_locations("certCA.pem")

# TLS context como CLIENTE (para conectar con Tercero)
ctx_client = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx_client.load_verify_locations("certCA.pem")
ctx_client.check_hostname = False  # localhost no necesita hostname check

# 1. SOCKET servidor (para Estudiante_1)
raw_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
raw_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 2. BIND
raw_server.bind((HOST2, PORT2))

# 3. LISTEN
raw_server.listen(5)

while True:
    print(f"[{nombre_estudiante_2}] Esperando conexión de Estudiante_1...")

    # 4. ACCEPT + WRAP TLS
    conn, addr = raw_server.accept()

    try:
        sesion = ctx_server.wrap_socket(conn, server_side=True)
        print(f"[{nombre_estudiante_2}] Conexión TLS con Estudiante_1 aceptada")

        # 5. RECV mensaje de Estudiante_1
        mensaje = sesion.recv(1024).decode("utf-8")
        print(f"[{nombre_estudiante_2}] Recibido de Estudiante_1: {mensaje}")

        try:
            partes = mensaje.strip().split()
            espera_1 = int(partes[-2])
        except Exception as e:
            print(f"[{nombre_estudiante_2}] Error al interpretar espera_1: {e}")
            sesion.close()
            continue

        suma_1_2 = espera_1 + espera_2
        print(f"[{nombre_estudiante_2}] espera_1={espera_1}, espera_2={espera_2}, suma={suma_1_2}")

        # --- Conectar con Tercero (como cliente TLS) ---
        raw_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_cliente.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            cliente_tercero = ctx_client.wrap_socket(raw_cliente, server_hostname="127.0.0.1")
            cliente_tercero.connect((HOST3, PORT3))
            print(f"[{nombre_estudiante_2}] Conexión TLS con Tercero establecida")

            mensaje_tercero = f"{nombre_tercero}: espera de {suma_1_2} segundos"
            print(f"[{nombre_estudiante_2}] Enviando a Tercero: {mensaje_tercero}")
            cliente_tercero.sendall(mensaje_tercero.encode("utf-8"))

            respuesta = ""
            while True:
                recv = cliente_tercero.recv(1024)
                if recv == b"":
                    break
                respuesta += recv.decode("utf-8")
            print(f"[{nombre_estudiante_2}] Recibido de Tercero: {respuesta}")

            try:
                partes_t = respuesta.strip().split()
                suma_1_2_3 = int(partes_t[-2])
            except Exception as e:
                print(f"[{nombre_estudiante_2}] Error al interpretar respuesta de Tercero: {e}")
                suma_1_2_3 = suma_1_2

            espera_3 = suma_1_2_3 - suma_1_2
            cliente_tercero.shutdown(socket.SHUT_WR)

        except ssl.SSLError as e:
            print(f"[{nombre_estudiante_2}] SSL error con Tercero: {e}")
            espera_3 = 0
        except socket.error as e:
            print(f"[{nombre_estudiante_2}] Socket error con Tercero: {e}")
            espera_3 = 0
        finally:
            raw_cliente.close()
            print(f"[{nombre_estudiante_2}] Conexión con Tercero cerrada")

        # --- Respuesta final a Estudiante_1 ---
        fecha_actual = datetime.datetime.now()
        respuesta_est1 = (
            f"{nombre_estudiante_1}: mi sistema muestra la siguiente fecha -> "
            f"{fecha_actual.isoformat()}|{espera_1}|{espera_2}|{espera_3}"
        )

        print(f"[{nombre_estudiante_2}] Enviando a Estudiante_1: {respuesta_est1}")
        sesion.sendall(respuesta_est1.encode("utf-8"))
        sesion.shutdown(socket.SHUT_WR)

    except ssl.SSLError as e:
        print(f"[{nombre_estudiante_2}] SSL error con Estudiante_1: {e}")
    except socket.error as e:
        print(f"[{nombre_estudiante_2}] Socket error: {e}")
    finally:
        sesion.close()
        print(f"[{nombre_estudiante_2}] Conexión con Estudiante_1 cerrada\n")
