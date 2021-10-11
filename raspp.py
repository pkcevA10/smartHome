from threading import Thread
import socket
import RPi.GPIO as GPIO 
import time
import os
import fcntl
import Adafruit_DHT as dht
import pymysql
import time


conn = pymysql.connect(host='localhost', user='phpmyadmin', password='1', db = 'temp', charset='utf8')

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#핀 배열
pin_light= 13
pin_rain = 6
pin_temp = 5
I2C_SLAVE = 0x703
PM2008 = 0x28
temp_val = 0
humi_val = 0
dust_val = 0
rain_val = 0
dust1_val = 0
dust2_val = 0
dust3_val = 0

GPIO.setup(pin_light, GPIO.IN)
GPIO.setup(pin_rain, GPIO.IN)


# 스텝 모터
StepPins = [23,24,25,8]

for pin in StepPins:
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin,False)
    
    
StepCounter = 0

StepCount = 4

Seq_1 = [ [0,0,0,1],
        [0,0,1,0],
        [0,1,0,0],
        [1,0,0,0]]
Seq_2 = [[1,0,0,0],
         [0,1,0,0],
         [0,0,1,0],
         [0,0,0,1]]


def sMotor(i):
    global StepPins, StepCounter, StepCount, Seq_1, Seq_2
    #sMotor(0), sMotor(1)이냐에 따라 모터 회전 방향 결정
    if i == 0:
        Seq = Seq_1
    elif i == 1:
        Seq = Seq_2
    time_end = time.time() + (5)
    
    try:
        while 1:
            for pin in range(0,4):
                xpin = StepPins[pin]
                if Seq[StepCounter][pin] != 0:
                    GPIO.output(xpin,True)
                else:
                    GPIO.output(xpin,False)
                    
            StepCounter += 1
             
            if(StepCounter == StepCount):
                StepCounter = 0
            if(StepCounter < 0):
                StepCounter = StepCount
                 
            time.sleep(0.002)
            if time.time() > time_end:
                break
            
    except:
        print("sMotor def fail")
        GPIO.cleanup()
        

# 소켓을 사용하기 위해서는 socket을 import해야 한다.
#import socket, threading


#
def binder(client_socket, addr):
    global temp_val,humi_val,dust_val,dust1_val,dust2_val,dust3_val, rain_val
    # 커넥션이 되면 접속 주소가 나온다.
    print('Connected by', addr)
    try:
    # 접속 상태에서는 클라이언트로 부터 받을 데이터를 무한 대기한다.
    # 만약 접속이 끊기게 된다면 except가 발생해서 접속이 끊기게 된다.
        while True:
            
            # socket의 recv함수는 연결된 소켓으로부터 데이터를 받을 대기하는 함수입니다. 최초 4바이트를 대기합니다.
            data = client_socket.recv(4)
            
            # 최초 4바이트는 전송할 데이터의 크기이다. 그 크기는 little 엔디언으로 byte에서 int형식으로 변환한다.
            length = int.from_bytes(data, "little")
            # 다시 데이터를 수신한다.
            data = client_socket.recv(length)
            # 수신된 데이터를 str형식으로 decode한다.
            msg = data.decode()
            #msg[3:] 사용한 이유 앞에 계속 쓸데없는 값이 붙어서 와서 이렇게 임시방편으로 해결.
            recv_msg = msg[3:]
            # 수신된 메시지를 콘솔에 출력한다.
            print('Received from', addr, recv_msg)
            
            print('moter on')
            
            
            time.sleep(1) 
            send_msg=0
            #전송 받은 메시지에 따라 send_msg 를 결정 한 후에 앱(클라이언트)로 전송
            if recv_msg == "T":
                
                
                print("#################socket temp")
                print(temp_val)
                send_msg = 'T:' + str(temp_val)
                    
            if recv_msg == "H":
                print("#################socket humi")
                print(humi_val)
                send_msg = 'H:' + str(humi_val)
            if recv_msg == "D":
                print("#################socket dust")
                send_msg ='#D1:' + str(dust1_val) +'#D2:' +str(dust2_val) + '#D3:' + str(dust3_val)
            if recv_msg == "R":
                print("#################socket rain")
                send_msg = 'R:' + str(rain_val)
            if recv_msg == "M:0":
                sMotor(0)
            if recv_msg == "M:1":
                sMotor(1)
                
                
            
            
            # 바이너리(byte)형식으로 변환한다.
            data = send_msg.encode()
            # 바이너리의 데이터 사이즈를 구한다.
            length = len(data)
            # 데이터 사이즈를 little 엔디언 형식으로 byte로 변환한 다음 전송한다.
            client_socket.sendall(length.to_bytes(4, byteorder="little"))
            # 데이터를 클라이언트로 전송한다.
            client_socket.sendall(data)
  
            
            
    except:
        # 접속이 끊기면 except가 발생한다.
        print("except : " , addr)
    finally:
        # 접속이 끊기면 socket 리소스를 닫는다.
        client_socket.close()
    
# 소켓을 만든다.
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 소켓 레벨과 데이터 형태를 설정한다.
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# 서버는 복수 ip를 사용하는 pc의 경우는 ip를 지정하고 그렇지 않으면 None이 아닌 ''로 설정한다.
# 포트는 pc내에서 비어있는 포트를 사용한다. cmd에서 netstat -an | find "LISTEN"으로 확인할 수 있다.
server_socket.bind(('', 9999))
# server 설정이 완료되면 listen를 시작한다.
server_socket.listen()




  
#Light Sensor
class Thread1(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
    def run(self):
        global light_val
        while True:
            time.sleep(1)  
            light_val = GPIO.input(pin_light)
            print("light: ",str(light_val))

#Rain Sensor
class Thread2(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
    def run(self):
        global rain_val
        while True:
            time.sleep(1)
            rain_val = GPIO.input(pin_rain)
            print("rain: ",str(rain_val))


#Temp,Humi,Dust Seosor
class Thread3(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
    
    def run(self):
        global humi_val, temp_val, dust1_val, dust2_val, dust3
        fd = os.open('/dev/i2c-1',os.O_RDWR)
        if fd < 0 :
            print("Failed to open the i2c bus\n")
        io = fcntl.ioctl(fd,I2C_SLAVE,PM2008)
        if io < 0 :
            print("Failed to acquire bus access/or talk to salve\n")

        try:
            while True:
                
                humi_val,temp_val = dht.read_retry(dht.DHT22, pin_temp)
                if humi_val is not None and temp_val is not None :
                    print("Temperature = {0:0.1f}*C Humidity = {1:0.1f}%".format(temp_val, humi_val))
                else :
                    print('Read error')
                    
                
                data = os.read(fd,32)
                
                #print("GRIM: PM0.1=",256*int(data[7])+int(data[8]),",PM2.5= ",256*int(data[9])+int(data[10]),",PM10=",256*int(data[11])+int(data[12]),"\n")
                
                print("PM2.5 =",256*int(data[9])+int(data[10]),",PM10 =",256*int(data[11])+int(data[12]),"\n")

                temp = str(temp_val)
                humi = str(humi_val)
                
                pm1 = str(256*int(data[7])+int(data[8]))
                dust1_val = str(256*int(data[7])+int(data[8]))
                
                pm25 = str(256*int(data[9])+int(data[10]))
                dust2_val = str(256*int(data[9])+int(data[10]))
                
                pm10 = str(256*int(data[11])+int(data[12]))
                dust3_val = str(256*int(data[11])+int(data[12]))

    
                
                
            
                cur = conn.cursor()
                cur.execute("INSERT INTO TEMP VALUES ("+ temp +","+ humi +","+pm1+","+pm25+","+pm10+", NOW())")
                conn.commit()
                
                time.sleep(1)
        except KeyboardInterrupt:
            os.close(fd)



# 소켓통신 스레드. binder()함수 호출
class Thread4(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
    
    def run(self):
        try:
    # 서버는 여러 클라이언트를 상대하기 때문에 무한 루프를 사용한다.
            while True:
                # client로 접속이 발생하면 accept가 발생한다.
                # 그럼 client 소켓과 addr(주소)를 튜플로 받는다.
                client_socket, addr = server_socket.accept()
                # 쓰레드를 이용해서 client 접속 대기를 만들고 다시 accept로 넘어가서 다른 client를 대기한다.
                binder(client_socket,addr)
                print("dd")
        except:
            print("server")
        finally:
            # 에러가 발생하면 서버 소켓을 닫는다.
            server_socket.close()


  
        
            
Thread1().start()
Thread2().start()
Thread3().start()
Thread4().start()
