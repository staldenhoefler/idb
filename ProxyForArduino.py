import asyncio
from bleak import BleakClient, BleakScanner
import psycopg2 as db
from datetime import datetime
import yaml

FEATHER_NAME = "CIRCUITPY"
UART_RX_CHARACTERISTIC = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

data_buffer = asyncio.Queue()


def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


async def read_ble_data():
    """
    Diese Funktion liest die Daten von der BLE-Verbindung und fügt sie in den asynchronen Buffer ein.
    """
    while True:
        try:
            print("Scanning for BLE devices...")
            devices = await BleakScanner.discover()
            feather_device = None

            for device in devices:
                if FEATHER_NAME in device.name:
                    feather_device = device
                    break

            if not feather_device:
                raise Exception("BLE Device not found")

            print(f"Found device: {feather_device.name} ({feather_device.address})")
            async with BleakClient(feather_device.address, timeout=10.0) as client:
                print("Connected to Feather!")
                while True:
                    try:
                        data = await client.read_gatt_char(UART_RX_CHARACTERISTIC)
                        message = data.decode("utf-8").strip()
                        parts = message.split(",")
                        temp = float(parts[0])
                        humidity = float(parts[1])
                        timestamp = datetime.now()

                        await data_buffer.put((temp, humidity, timestamp))
                        print(f"Read Data: Temperature: {temp}°C, Humidity: {humidity}%, Timestamp: {timestamp}")

                        await asyncio.sleep(5)
                    except Exception as e:
                        print(f"Error while reading BLE data: {e}")
                        break

        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(5)


async def upload_data_to_postgres():
    """
    Diese Funktion lädt die Daten aus dem asynchronen Buffer in die PostgreSQL-Datenbank hoch.
    """
    while True:
        try:
            data = await data_buffer.get()

            if data[0] is None or data[1] is None:
                print("Invalid data, skipping...")
                continue

            connection_data = load_config('params.yaml')['database']
            db_connection = db.connect(
                dbname=connection_data['dbname'],
                user=connection_data['user'],
                password=connection_data['password'],
                host=connection_data['host'],
                port=connection_data['port']
            )
            db_cursor = db_connection.cursor()

            db_cursor.execute(
                "INSERT INTO temp_sensor (temp, humidity, time_stamp) VALUES (%s, %s, %s)",
                data
            )
            db_connection.commit()

            print(f"Uploaded Data to Postgres: {data}")


            db_cursor.close()
            db_connection.close()

        except Exception as e:
            print(f"Failed to upload data: {e}. Retrying...")
            await data_buffer.put(data)
            await asyncio.sleep(5)


async def main():
    """
    Hauptfunktion, die die BLE-Datenlese- und Upload-Tasks startet.
    """
    read_task = asyncio.create_task(read_ble_data())
    upload_task = asyncio.create_task(upload_data_to_postgres())

    await asyncio.gather(read_task, upload_task)


if __name__ == "__main__":
    asyncio.run(main())
