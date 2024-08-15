import time
import smbus2

aht10 = 0x38
bus = smbus2.SMBus(1)
bus.write_i2c_block_data(aht10, 0xAC, [0x33, 0x00])
time.sleep(0.5)
data = bus.read_i2c_block_data(aht10, 0x00, 6)


temp = (( data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
humidity = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4

temp = temp * 200 /1048576 - 50
humidity = humidity * 100 / 1048576
bus.close()

print(temp)

print(humidity)
