import psycopg2 as db
import time
import smbus2
from datetime import datetime


class DataLogger():
    
    def __init__(self):
        self.db_connection = None
        self.db_cursor = None
        self.aht10 = 0x38

    def make_DB_connection(self):
        connection_established = False
        while not connection_established:
            try:
                self.db_connection = db.connect(dbname="temperatur_sensor", user="postgres", password="vQVXEEnnhC", host="192.168.0.206", port="5433" )
                self.db_cursor = self.db_connection.cursor()
                connection_established = True
            except:
                print("Connection_Failed")
                time.sleep(5)
    
    def close_DB_connection(self):
        self.db_cursor.close()
        self.db_connection.close()
        
    def log_data(self, temp, humidity):
        self.make_DB_connection()
        self.db_cursor.execute("INSERT INTO temp_sensor (temp, humidity, time_stamp) VALUES (%s, %s, %s)", (temp, humidity, datetime.now()))
        self.db_connection.commit()
        self.close_DB_connection()

    def read_sensors(self):
        try:
            bus = smbus2.SMBus(1)
            bus.write_i2c_block_data(self.aht10, 0xAC, [0x33, 0x00])
            time.sleep(0.5)
            data = bus.read_i2c_block_data(self.aht10, 0x00, 6)
            
            
            temp = (( data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
            humidity = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
            
            temp = temp * 200 /1048576 - 50
            humidity = humidity * 100 / 1048576
            print(f'Temp: {temp}, Hum: {humidity}')
            bus.close()
            
            return temp, humidity
        except:
            print("Sensor Error")
            return None, None
    
    def run_one_cilce(self):
        temp, humidity = self.read_sensors()
        self.log_data(temp, humidity)

    def run_data_logger(self, intervall):
        while True:
            self.run_one_cilce()
            time.sleep(intervall)
            
data_logger = DataLogger()
data_logger.run_data_logger(intervall=5)
