import os
import pandas as pd
from influxdb import InfluxDBClient

DB_PORT = os.environ['DB_PORT'] if 'DB_PORT' in os.environ else None
DB_HOST = os.environ['DB_HOST'] if 'DB_HOST' in os.environ else None
DB_NAME = os.environ['DB_NAME'] if 'DB_NAME' in os.environ else None
FILE_TO_EXTRACT = os.environ['FILE_TO_EXTRACT'] if 'FILE_TO_EXTRACT' in os.environ else None
CITY = os.environ['CITY'] if 'CITY' in os.environ else None

if __name__ == '__main__':
    if FILE_TO_EXTRACT is None or DB_PORT is None or DB_HOST is None or DB_NAME is None:
        print('No environment set')
        exit(1)
    if not os.path.exists('/app/data/'+FILE_TO_EXTRACT):
        print('No file exists')
        exit(1)

    read_frame = pd.read_csv('/app/data/'+FILE_TO_EXTRACT)

    name = FILE_TO_EXTRACT.split('.')[0]
    data_frame = pd.DataFrame(data={'datetime':read_frame['datetime'], name:read_frame[CITY]})

    data_frame = data_frame[data_frame[name].notna()]

    influx = InfluxDBClient(host=DB_HOST, port=DB_PORT)
    
    if {'name':DB_NAME} not in influx.get_list_database():
        influx.create_database(DB_NAME)
    influx.switch_database(DB_NAME)

    data = []
    for index, row in data_frame.iterrows():
        data.append(
            {
                'measurement': CITY,
                'datetime': row['datetime'],
                'fields': {
                    'name': float(row['name'])
                }
            }
        )
        print(row['datetime'], row[name])

    influx.write_points(data)