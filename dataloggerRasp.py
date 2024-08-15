from smbus2 import SMBus
import time

# AHT10 default I2C address
AHT10_I2C_ADDR = 0x38

# Initialize the sensor
def aht10_init(bus):
    bus.write_i2c_block_data(AHT10_I2C_ADDR, 0xE1, [0x08, 0x00])
    time.sleep(0.02)

# Read temperature and humidity
def aht10_read(bus):
    bus.write_i2c_block_data(AHT10_I2C_ADDR, 0xAC, [0x33, 0x00])
    time.sleep(0.08)
    data = bus.read_i2c_block_data(AHT10_I2C_ADDR, 0x00, 6)

    if data[0] & 0x80 == 0:
        humidity = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
        temperature = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
        humidity = (humidity / 1048576.0) * 100
        temperature = (temperature / 1048576.0) * 200 - 50
        return temperature, humidity
    else:
        return None, None

if __name__ == "__main__":
    bus = SMBus(1)
    aht10_init(bus)
    while True:
        temp, hum = aht10_read(bus)
        if temp is not None and hum is not None:
            print(f"Temperature: {temp:.2f} C, Humidity: {hum:.2f} %")
        else:
            print("Failed to read sensor data")
        time.sleep(2)