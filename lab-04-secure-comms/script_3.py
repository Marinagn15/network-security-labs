import socket
import errno
import random
import ssl

HOST3 = "127.0.0.1"
PORT3 = 2405  # 24X con X=5

nombre_estudiante_2 = "Marina_Garcia_Navas_2"
nombre_tercero = "Tercero"

espera_3 = random.randint(1, 10)
print(f"[Tercero] Espera_3 = {espera_3} segundos")

# TLS context (servidor)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain("cert.pem", "key.pem")
context.load_verify_locations("certCA.pem")

# 1. SOCKET
raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
raw_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 2. BIND
raw_socket.bind((HOST3, PORT3))

# 3. LISTEN
raw_socket.listen(5)

while True:
    print("[Tercero] Esperando conexión...")

    # 4. ACCEPT
    conn, addr = raw_socket.accept()

    # 5. WRAP TLS
    try:
        sesion = context.wrap_socket(conn, server_side=True)
        print("[Tercero] Conexión TLS aceptada")

        # 6. RECV
        mensaje = sesion.recv(1024).decode("utf-8")
        print(f"[Tercero] Recibido: {mensaje}")

        partes = mensaje.strip().split()
        espera_recibida = int(partes[-2])
        espera_total = espera_recibida + espera_3

        respuesta = f"Estudiante_2: espera de {espera_total} segundos"
        print(f"[Tercero] Enviando: {respuesta}")

        # 7. SEND
        sesion.sendall(respuesta.encode("utf-8"))
        sesion.shutdown(socket.SHUT_WR)

    except ssl.SSLError as e:
        print(f"[Tercero] SSL error: {e}")
    except socket.error as e:
        if e.errno == errno.ECONNRESET:
            print("[Tercero] Conexión reseteada")
        elif e.errno == errno.ETIMEDOUT:
            print("[Tercero] Timeout")
        else:
            print(f"[Tercero] Socket error: {e}")
    finally:
        sesion.close()
        print("[Tercero] Conexión cerrada\n")
