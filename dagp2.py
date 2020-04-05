from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'Carlos Cobos',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['info@kcobos.es'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}

# Variables
TEMP_FOLDER='/tmp/p2cc/'

NETWORK='mired'

DB_SERVER='******'
# DB_USER='******'
# DB_PASS='******'
# ROOT_PASS='******'
DB_NAME='basedatos'
DB_PORT=8086

API_KEY='******'


# Inicialización del grafo DAG de tareas para el flujo de trabajo
dag = DAG(
    'Practica2_CC2',
    default_args=default_args,
    description='Segunda práctica de la asignatura CC2 del MII de la UGR 19-20',
)

# Tareas
create_env = BashOperator(
    task_id='create_env',
    # bash_command='[ -e %s ] && rm -rf %s; mkdir %s'%(TEMP_FOLDER,TEMP_FOLDER,TEMP_FOLDER),
    bash_command='[ ! -e %s ] && mkdir %s ; echo "Carpeta env creada"'%(TEMP_FOLDER,TEMP_FOLDER),
    dag=dag,
)

create_net = BashOperator(
    task_id='create_net',
    bash_command='[ `docker network ls | grep %s | wc -l` == 0 ] && docker network create %s'%(NETWORK,NETWORK) +
        ' ; echo "Red %s creada"'%(NETWORK),
    dag=dag,
)

create_db = BashOperator(
    task_id='create_db',
    # bash_command='[ `docker ps -a | grep %s | wc -l` == 0 ] &&'%(DB_SERVER) +
    #     ' docker run -d --name %s --network %s -h %s'%(DB_SERVER,NETWORK,DB_SERVER)+
    #     ' -e MYSQL_ROOT_PASSWORD=%s'%(ROOT_PASS) +
    #     ' -e MYSQL_USER=%s'%(DB_USER) +
    #     ' -e MYSQL_PASSWORD=%s'%(DB_PASS) +
    #     ' -e MYSQL_DATABASE=%s'%(DB_NAME) +
    #     ' --restart=always mysql' + 
    #     ' ; echo "Base de datos operativa"',
    bash_command='[ `docker ps -a | grep %s | wc -l` == 0 ] &&'%(DB_SERVER) +
        ' docker run -d --name %s --network %s -h %s'%(DB_SERVER,NETWORK,DB_SERVER) +
        ' -p 8086:8086'
        ' --restart=always influxdb:alpine' + 
        ' ; echo "Base de datos operativa"',
    dag=dag,
)

download_humidity = BashOperator(
    task_id='download_humidity',
    bash_command='[ ! -e %shumidity.csv.zip ] && wget https://github.com/manuparra/MaterialCC2020/raw/master/humidity.csv.zip -P %s'%(TEMP_FOLDER,TEMP_FOLDER)+
        ' ; echo "humidity descargado"',
    dag=dag,
)
download_temperature = BashOperator(
    task_id='download_temperature',
    bash_command='[ ! -e %stemperature.csv.zip ] && wget https://github.com/manuparra/MaterialCC2020/raw/master/temperature.csv.zip -P %s'%(TEMP_FOLDER,TEMP_FOLDER)+
        ' ; echo "temperature descargado"',
    dag=dag,
)

unzip_humidity = BashOperator(
    task_id='unzip_humidity',
    bash_command='[ ! -e %shumidity.csv ] && unzip -d %s %s/humidity.csv.zip'%(TEMP_FOLDER,TEMP_FOLDER,TEMP_FOLDER) +
        ' ; echo "humidity extraído"',
    dag=dag,
)
unzip_temperature = BashOperator(
    task_id='unzip_temperature',
    bash_command='[ ! -e %stemperature.csv ] && unzip -d %s %s/temperature.csv.zip'%(TEMP_FOLDER,TEMP_FOLDER,TEMP_FOLDER) +
        ' ; echo "temperature extraído"',
    dag=dag,
)

clone_extractor = BashOperator(
    task_id='clone_extractor',
    bash_command='[ ! -e %sextractor ] && git clone --single-branch --branch extractor https://github.com/kcobos/CC2-Airflow.git %sextractor'%(TEMP_FOLDER, TEMP_FOLDER) + 
        ' ; echo "Extractor clonado"',
    dag=dag,
)

build_extractor = BashOperator(
    task_id='build_extractor',
    bash_command='[ `docker images | grep extractor | wc -l` == 0 ] && docker build -t extractor %sextractor'%(TEMP_FOLDER) +
        ' ; echo "Imagen extractor creada"',
    dag=dag,
)

extractor_humidity = BashOperator(
    task_id='extractor_humidity',
    bash_command='docker run --rm --network %s -e DB_PORT=%i -e DB_HOST=%s -e DB_NAME=%s -e FILE_TO_EXTRACT=humidity.csv -e CITY="San Francisco" -v %s:/app/data/:ro extractor'%(
        NETWORK,DB_PORT,DB_SERVER,DB_NAME,TEMP_FOLDER
    ),
    dag=dag,
)

extractor_temperature = BashOperator(
    task_id='extractor_temperature',
    bash_command='docker run --rm --network %s -e DB_PORT=%i -e DB_HOST=%s -e DB_NAME=%s -e FILE_TO_EXTRACT=temperature.csv -e CITY="San Francisco" -v %s:/app/data/:ro extractor'%(
        NETWORK,DB_PORT,DB_SERVER,DB_NAME,TEMP_FOLDER
    ),
    dag=dag,
)

delete_half_data = BashOperator(
    task_id='delete_half_data',
    bash_command='docker run --rm --network %s ubuntu /bin/bash -c "apt update; apt install -y curl; '%(NETWORK) + 
        'curl --location --request GET \'%s:%i/query?db=%s&q=%s'%( 
            DB_SERVER,DB_PORT,DB_NAME,'delete%20from%20%22San%20Francisco%22%20where%20time%20%3C%20%272015-01-01%27\'"' 
        ),
    dag=dag,
)

clone_apiv1 = BashOperator(
    task_id='clone_apiv1',
    bash_command='[ ! -e %sapiv1 ] && git clone --single-branch --branch apiv1 https://github.com/kcobos/CC2-Airflow.git %sapiv1'%(TEMP_FOLDER, TEMP_FOLDER) + 
        ' ; echo "apiv1 clonado"',
    dag=dag,
)

build_apiv1 = BashOperator(
    task_id='build_apiv1',
    bash_command='[ `docker images | grep apiv1 | wc -l` == 0 ] && docker build -t apiv1 %sapiv1'%(TEMP_FOLDER) +
        ' ; echo "Imagen apiv1 creada"',
    dag=dag,
)

tests_apiv1 = BashOperator(
    task_id='tests_apiv1',
    bash_command='docker run --rm --network %s -e DB_PORT=%i -e DB_HOST=%s -e DB_NAME=%s -v %s:/app/data/ apiv1 pytest test_app.py -vv -s'%(
        NETWORK,DB_PORT,DB_SERVER,DB_NAME,TEMP_FOLDER
    ),
    dag=dag,
)

deploy_apiv1 = BashOperator(
    task_id='deploy_apiv1',
    bash_command='docker run -d --name %s --network %s -h %s -p 8081:8080 -e DB_PORT=%i -e DB_HOST=%s -e DB_NAME=%s -v %s:/app/data/ --restart=always apiv1'%(
        'apiv1',NETWORK,'apiv1',DB_PORT,DB_SERVER,DB_NAME,TEMP_FOLDER
    )+ 
    ' ; docker network connect bridge apiv1',
    dag=dag,
)

clone_apiv2 = BashOperator(
    task_id='clone_apiv2',
    bash_command='[ ! -e %sapiv2 ] && git clone --single-branch --branch apiv2 https://github.com/kcobos/CC2-Airflow.git %sapiv2'%(TEMP_FOLDER, TEMP_FOLDER) + 
        ' ; echo "apiv2 clonado"',
    dag=dag,
)

build_apiv2 = BashOperator(
    task_id='build_apiv2',
    bash_command='[ `docker images | grep apiv2 | wc -l` == 0 ] && docker build -t apiv2 %sapiv2'%(TEMP_FOLDER) +
        ' ; echo "Imagen apiv2 creada"',
    dag=dag,
)

tests_apiv2 = BashOperator(
    task_id='tests_apiv2',
    bash_command='docker run --rm --network %s -e API_KEY=%s apiv2 pytest test_app.py -vv -s'%(
        NETWORK,API_KEY
    ),
    dag=dag,
)

deploy_apiv2 = BashOperator(
    task_id='deploy_apiv2',
    bash_command='docker run -d --name %s --network %s -h %s -p 8082:8080 -e API_KEY=%s --restart=always apiv2'%(
        'apiv2',NETWORK,'apiv2',API_KEY
    )+ 
    ' ; docker network connect bridge apiv2',
    dag=dag,
)

clone_proxy = BashOperator(
    task_id='clone_proxy',
    bash_command='[ ! -e %sproxy ] && git clone --single-branch --branch proxy https://github.com/kcobos/CC2-Airflow.git %sproxy'%(TEMP_FOLDER, TEMP_FOLDER) + 
        ' ; echo "proxy clonado"',
    dag=dag,
)

proxy_nginx = BashOperator(
    task_id='proxy_nginx',
    #  -v /var/run/docker.sock:/tmp/docker.sock:ro
    bash_command='docker run -d --name proxy -p 8088:8080 --network %s -v %sproxy/nginx.conf:/etc/nginx/nginx.conf:ro --restart=always nginx'%(
        NETWORK,TEMP_FOLDER,
    )+ 
    ' ; docker network connect bridge proxy',
     dag=dag,
)

#Dependencias
create_env.set_downstream(download_humidity)
create_env.set_downstream(download_temperature)

create_net.set_downstream(create_db)

create_db.set_downstream(extractor_humidity)
create_db.set_downstream(extractor_temperature)

create_env.set_downstream(clone_extractor)
clone_extractor.set_downstream(build_extractor)
build_extractor.set_downstream(extractor_humidity)
build_extractor.set_downstream(extractor_temperature)

create_env.set_downstream(download_humidity)
download_humidity.set_downstream(unzip_humidity)
unzip_humidity.set_downstream(extractor_humidity)

create_env.set_downstream(download_temperature)
download_temperature.set_downstream(unzip_temperature)
unzip_temperature.set_downstream(extractor_temperature)

extractor_humidity.set_downstream(delete_half_data)
extractor_temperature.set_downstream(delete_half_data)

delete_half_data.set_downstream(tests_apiv1)
delete_half_data.set_downstream(tests_apiv2)

create_env.set_downstream(clone_apiv1)
clone_apiv1.set_downstream(build_apiv1)
build_apiv1.set_downstream(tests_apiv1)
tests_apiv1.set_downstream(deploy_apiv1)

create_env.set_downstream(clone_apiv2)
clone_apiv2.set_downstream(build_apiv2)
build_apiv2.set_downstream(tests_apiv2)
tests_apiv2.set_downstream(deploy_apiv2)

deploy_apiv1.set_downstream(proxy_nginx)
deploy_apiv2.set_downstream(proxy_nginx)

create_env.set_downstream(clone_proxy)
clone_proxy.set_downstream(proxy_nginx)