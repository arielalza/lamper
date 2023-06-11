import boto3
import paramiko
import time
#Investigar sobre paramiko y usuarios

# Credenciales de AWS (revisar)
ACCESS_KEY = 'TU_ACCESS_KEY'
SECRET_KEY = 'TU_SECRET_KEY'

# Configuración de la EC2
INSTANCE_AMI = 'AMI_ID'
INSTANCE_TYPE = 't2.micro'
KEY_PAIR_NAME = 'NOMBRE_DEL_KEY_PAIR'
SECURITY_GROUP_NAME = 'NOMBRE_DEL_SECURITY_GROUP'

# Configuración de SSH (revisar si es necesario llave)
SSH_USERNAME = 'ubuntu'
SSH_KEY_FILE = 'RUTA_AL_ARCHIVO_DE_LA_LLAVE_PRIVADA'

# Conexión a AWS 
ec2_client = boto3.client('ec2', region_name='us-west-2', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

# Crear instancia EC2
response = ec2_client.run_instances(
    ImageId=INSTANCE_AMI,
    InstanceType=INSTANCE_TYPE,
    MinCount=1,
    MaxCount=1,
    KeyName=KEY_PAIR_NAME,
    SecurityGroups=[SECURITY_GROUP_NAME]
)
instance_id = response['Instances'][0]['InstanceId']

# Esperando instancia en estado "running"
ec2_client.get_waiter('instance_running').wait(InstanceIds=[instance_id])

# Obtener la dirección IP pública de la instancia (revisar si es la IP publica o el DNS)
response = ec2_client.describe_instances(InstanceIds=[instance_id])
public_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']

# Conexión SSH a la instancia 
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(public_ip, username=SSH_USERNAME, key_filename=SSH_KEY_FILE)

# Ejecutar comandos en la instancia (especificar versiones a utilizar)
commands = [
    'sudo apt update',
    'sudo apt install -y apache2',
    'sudo apt install -y mysql-server',
    'sudo apt install -y python3',
    # Otros comandos de configuración que desees agregar
]
for command in commands:
    stdin, stdout, stderr = ssh_client.exec_command(command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    if output:
        print(output)
    if error:
        print(error)

# Cerrar la conexión SSH
ssh_client.close()

print("El despliegue fue lanzado correctamente")
