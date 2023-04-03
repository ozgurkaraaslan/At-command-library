# at_com.communicate_at('AT+QMTOPEN=0,"mqtt3.thingspeak.com",1883')
# at_com.communicate_at('AT+QMTCONN=0,"EQEZNCkcCSYdOhAnOB80FRg","EQEZNCkcCSYdOhAnOB80FRg","UOyigohG+kLhf74qpSZOIBkt"')
# at_com.communicate_at('AT+QMTPUB=0,0,0,0,"channels/1972067/publish/fields/field1"')
    
class MQTT:
    ctrl_z = '\x1A'

    def __init__(self, at_com):
        """
        Initialization of the class.
        """
        self.at_com = at_com
    
    def config(self, client_idx, host_name, port):
        command = f'AT+QMTOPEN={client_idx},\"{host_name}\",{port}'
        return self.at_com.intercomm_at(command)
    
    def connect(self, client_idx, clientID, username = None, password = None):
        if username and password:
            command = f'AT+QMTCONN={client_idx},\"{clientID}\",\"{username}\",\"{password}\"'
        else:
            command = f'AT+QMTCONN={client_idx},{clientID}'
        return self.at_com.intercomm_at(command)
    
    def publish(self, client_idx, msgID = 0, qos = 0, retain = 0, topic = ""):
        command = f'AT+QMTPUB={client_idx},{msgID},{qos},{retain},\"{topic}\"'
        return self.at_com.intercomm_at(command)
    
    def publish_data(self, msg:str):
        return self.at_com.intercomm_at(msg, line_end=False)
    
    def publish_end(self):
        return self.at_com.intercomm_at(self.ctrl_z)
    
    