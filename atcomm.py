from machine import UART, Pin
from time import time, sleep_ms
from mqtt import MQTT

class ATComm:
    uart_flag = 0

    def __init__(self, port_number=0, tx=Pin(0), rx=Pin(1), baudrate=115200):
        self.port_number = port_number
        self.tx = tx
        self.rx = rx
        self.baudrate = baudrate
        
    def init_uart(self):
        # Modemle haberleşmek için gerekli uart parametreleri ayarlandı.
        self.uart0 = UART(self.port_number, tx=self.tx, rx=self.rx, baudrate=self.baudrate)
        self.uart_flag = 1
        self.uart0.read()  # modem ilk başta bir değer gönderiyor, hattı temizlemek için bir kere okuma yaptırdım
        return "OK"

    def deinit_uart(self):
        self.uart0.deinit()
        self.uart_flag = 0
        return "OK"
    
    def parse_at(self, message: str):  # Modemden dönen cevabı istediğimiz forma ayıklayan fonksiyon
        msg = message.decode('utf-8').split("\r\n")
        parsed_msg = ""
        parsed_msg += msg[0]+'\n'
        for i in range(1, (len(msg))):
            if msg[i] != "":
                parsed_msg += msg[i]+'\n'
        return parsed_msg
    
    """def parse_at(self, message: str):  # Modemden dönen cevabı istediğimiz forma ayıklayan fonksiyon
        msg = message.decode('utf-8').split("\r\n")
        parsed_msg = ""
        parsed_msg += '> '+msg[0][:-1]+'\n\n'
        for i in range(1, (len(msg))):
            if msg[i] != "":
                parsed_msg += '< '+msg[i]+'\n'
        return parsed_msg"""

    # Modeme AT komutlarının gönderildiği ve diğer gerekli fonksiyonların çağırıldığı ana fonksiyon
    def send_at(self, at_command, line_end = True):
        if not self.uart_flag:
            return "ERROR"
        initial_time = 0
        current_time = 0
        parsed_at = {}
        response = ""
        if line_end:
            at_command = f"{at_command}\r".encode()
        self.uart0.write(at_command)

    def read_at(self, timeout = 10, expected_responses=None, faulty_responses=None):
        if not self.uart_flag:
            parsed_at = {"status": "Fail", "status_code": 0, "response": ""}
            return parsed_at
        
        initial_time = time()

        while 1:
            if self.uart0.any() > 0:
                rxData = self.uart0.read()  # Modemden AT komutları alındı.
                
                response = self.parse_at(rxData)
                if faulty_responses:
                    for faulty_response in faulty_responses:
                        if faulty_response in response:
                            parsed_at = {"status": "Fail", "status_code": 6, "response": response}
                            return parsed_at
                if expected_responses:
                    for expected_response in expected_responses:
                        if str(expected_response) in response:
                            parsed_at = {"status": "Success", "status_code": 11, "response": response}
                            return parsed_at
                    parsed_at = {"status": "Fail", "status_code": 5, "response": response}
                    return parsed_at

                if "OK" in response:
                    parsed_at = {"status": "Success", "status_code": 10, "response": response}
                elif "ERROR" in response:
                    parsed_at = {"status": "Fail", "status_code": 1, "response": response}
                elif "+CME ERROR" in response:
                    parsed_at = {"status": "Fail", "status_code": 2, "response": response}
                elif "NO CARRIER" in response:
                    parsed_at = {"status": "Fail", "status_code": 3, "response": response}
                else:
                    parsed_at = {"status": "Other_status", "status_code": 20, "response": response}
                break

            current_time = time()
            if current_time - initial_time >= timeout:
                parsed_at = {"status": "Fail", "status_code": 4, "response": ""}
                break
        return parsed_at
    def intercomm_at(self, at_command, expected_responses=None, faulty_responses=None, timeout=10, line_end = True):
        self.send_at(at_command = at_command, line_end = line_end)
        sleep_ms(20)
        return self.read_at(timeout=timeout, expected_responses=expected_responses, faulty_responses=faulty_responses)

at_com = ATComm()
at_com.init_uart()
mqtt = MQTT(at_com)