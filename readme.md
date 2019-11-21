#Sensoriando
**Hub de Sensores**

##Plano de negocio
Consiste em vender sensores pronto, acabados e prontos para o uso para o publico não técnico.

Cada sensor vendido ou montado terá um numero de identificacao unico (serialkey) que vai permitir enviar os dados.

O sensor envia seu serialkey e recebe uma string para fazer o publishe, esse procedimento deve ser executado sempre que o sensor for ligado, desta forma pode sofrer as devidas atualizações com relação ao webservice (nome, local etc).

Todo sensor vendido devera estar previamento cadastrado no webservice, porque a serialkey será gerado com o id da conta + id do sensor em hash MD5, onde:

-  O nome padrao da conta é CONVIDADO (que será alterado quando o usuário se cadastrar no site e informar um serialkey para que a conta seja localizada, como cada sensor será vendido e entregue, já estará cadastrado a cidade e estado.

- Todas as contas por padrão são PUBLICAS (que pode ser alterado mediante pagamento)

- Todas as contas tem pelo menos um local chamado BASE (que pode ser alterado ou novos podem ser adicionados)

O webservice já terá pre cadastrado os tipos de sensores (categorias) para obter dados especificos, como casas de precisão, unidade etc, também terá dois tipos de conta, a publica (gratuita) e a privada (paga), caracteristicas dos planos:

- Account Public: consultar os dados via site ou app, os dados são publicos e terceiros podem ser (sem identificacao).

- Account Private: Para todos os planos os dados não são publicos e pode-se configurar trigger, já para o PlanoB pode fazer datamining nos dados publicos, TODOS OS PLANOS EXPORT DATA.

- Trigger é quando algum setpoint é atingido e o webservice publish para todos os subscribe do broker.

Tentar fazer o custo por sensor PlanoB = PlanoA * n.

O dono do sensor tem que ter a opção de informar manualmente um broker caso não quera usar o nosso ou replicar, se usar um outro broker tem que solicitar para desativar a conta para os dados não serem publicados mas sempre serão coletados.

O app vai ser somente um subscribe que após informar usuário e senha, recebe os sensores cadastrados e mostra os dados.

##Requeriments
```console
sudo apt-get update
sudo apt-get upgrade
```

###Database
```console
sudo apt-get postgresql
```

###Framework
```console
sudo apt-get install python3-pip
pip install django psycopg2 psycopg2-binary
sudo apt-get install python-psycopg2
```

###Broker MQTT
```console
sudo apt-get install mosquitto mosquitto-clients
```

###NTP
```console
sudo apt-get install ntp
sudo timedatectl set-timezone America/Sao_Paulo
sudo apt-get install ntpdate
service ntp stop
sudo service ntp stop
sudo ntpdate a.ntp.br
sudo service ntp start
```

###Development
```console
sudo apt-get install build-essential gcc make cmake cmake-gui cmake-curses-gui
sudo apt-get install libssl-dev 
sudo apt-get install doxygen

git clone https://github.com/eclipse/paho.mqtt.c.git
cd paho.mqtt.c
make
make html
sudo make install
```

