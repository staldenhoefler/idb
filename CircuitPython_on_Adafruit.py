import time
import board
import digitalio
import adafruit_dht
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

dht_sensor = adafruit_dht.DHT11(board.D9)

led = digitalio.DigitalInOut(board.RED_LED)
led.direction = digitalio.Direction.OUTPUT

def get_sensor_data():
    try:
        temperature = dht_sensor.temperature
        humidity = dht_sensor.humidity
        return temperature, humidity
    except RuntimeError as e:
        print(f"Sensor error: {e}")
        return None, None

print("Starting BLE UART service...")
while True:
    if not ble.connected:
        ble.start_advertising(advertisement)
        print("Advertising BLE service...")
        led.value = True
        time.sleep(1)
        led.value = False
        time.sleep(1)
    else:
        print("Connected!")
        while ble.connected:
            temperature, humidity = get_sensor_data()
            if temperature is not None and humidity is not None:
                # Send data over BLE
                uart.write(f"{temperature:.1f},{humidity:.1f}")
                print(f"Sent: Temperature: {temperature:.1f} C, Humidity: {humidity:.1f}%")

                if humidity > 60:
                    led.value = True
                    print("LED ON: Humidity above 60%")
                else:
                    led.value = False
                    print("LED OFF: Humidity below 60%")

            time.sleep(5)
    ble.stop_advertising()
