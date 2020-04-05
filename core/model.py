from statsmodels.tsa.arima_model import ARIMA
import pandas as pd
import pmdarima as pm
from influxdb import InfluxDBClient
import os
import pickle
from datetime import datetime, timedelta

class Model:
    def __init__(self, db_port, db_host, db_name):
        self.influx = InfluxDBClient(host=db_host, port=int(db_port))
        if {'name':db_name} not in self.influx.get_list_database():
            raise Exception('No database')
        self.influx.switch_database(db_name)

        if not os.path.exists('/app/data/models'):
            os.mkdir('/app/data/models')

        if not os.path.exists('/app/data/models/temperature'):
            print("Temperature model does not exist")
            self.create_model('temperature')
        if not os.path.exists('/app/data/models/humidity'):
            print("Humidity model does not exist")
            self.create_model('humidity')

    def create_model(self, column):
        df = pd.DataFrame(self.influx.query('SELECT "%s" FROM "San Francisco"'%(column)).get_points())
        model = pm.auto_arima(df[column], start_p=1, start_q=1,
                      test='adf',       # use adftest to find optimal 'd'
                      max_p=3, max_q=3, # maximum p and q
                      m=1,              # frequency of series
                      d=None,           # let model determine 'd'
                      seasonal=False,   # No Seasonality
                      start_P=0, 
                      D=0, 
                      trace=True,
                      error_action='ignore',  
                      suppress_warnings=True, 
                      stepwise=True)
        pickle.dump(model, open('/app/data/models/%s'%column, 'wb'))
        return True
    
    def predict(self, time_range):
        model_temp = pickle.load(open('/app/data/models/temperature', "rb"))
        model_humy = pickle.load(open('/app/data/models/humidity', "rb"))
        
        temp_pred, _ = model_temp.predict(n_periods=time_range, return_conf_int=True)
        humy_pred, _ = model_humy.predict(n_periods=time_range, return_conf_int=True)

        times = []
        now = datetime.now()
        for _ in range(time_range):
            times.append(now)
            now = now + timedelta(hours=1)

        ret = []
        for time, temp, humy in zip(times, temp_pred, humy_pred):
            ret.append({
                'hour':time.strftime("%Y-%m-%d %H:%M:%S"),
                'temp': temp,
                'hum': humy,
            })
        return ret