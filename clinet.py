#소켓통신 외부 테스트 용도


# 소켓을 사용하기 위해서는 socket을 import해야 한다.
import socket
import time

HOST = '121.144.6.113'

# port는 위 서버에서 설정한 9999로 접속을 한다.
PORT = 9999
# 소켓을 만든다.
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect함수로 접속을 한다.
client_socket.connect((HOST, PORT))

while True :

    # 메시지는 hello로 보낸다.
    msg = 'TEST'
    # 메시지를 바이너리(byte)형식으로 변환한다.
    data = msg.encode()
    # 메시지 길이를 구한다.
    length = len(data)
    # server로 리틀 엔디언 형식으로 데이터 길이를 전송한다.
    client_socket.sendall(length.to_bytes(4, byteorder="little"))
    # 데이터를 전송한다.
    client_socket.sendall(data)
    # server로 부터 전송받을 데이터 길이를 받는다.
    data = client_socket.recv(4)
    # 데이터 길이는 리틀 엔디언 형식으로 int를 변환한다.
    length = int.from_bytes(data, "little")
    # 데이터 길이를 받는다.
    data = client_socket.recv(length)
    # 데이터를 수신한다.
    msg = data.decode()
    # 데이터를 출력한다.
    print('Received from : ', msg)
client_socket.close()




