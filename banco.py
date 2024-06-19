#Instalação do Mysql Connector Python
import mysql.connector
from mysql.connector import errorcode

#Estabelecer a conexão
#Atenção no usuário e senha de conexão
print("Conexão a ser estabelecida...")
try:
      conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root'
      )
except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('Usuário ou senha inválida')
      else:
            print(err)

#Criação da estrutura do banco de dados
cursor = conn.cursor()
cursor.execute("DROP DATABASE IF EXISTS `votacao`;")
cursor.execute("CREATE DATABASE `votacao`;")
cursor.execute("USE `votacao`;")

#Criar as tabelas
TABLES = {}
TABLES['Candidato'] = ('''
      CREATE TABLE `candidato` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `nome` varchar(50) NOT NULL,
      `descricao` varchar(30) NOT NULL,
      `tipoCandidato` varchar(50) NOT NULL,
      `imagem` varchar(100),
      `criacao`TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')

TABLES['voto'] = ('''
    CREATE TABLE `voto` (
        `id` INT(11) NOT NULL AUTO_INCREMENT,
        `time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `candidato_id` INT(11) NOT NULL,
        PRIMARY KEY (`id`),
        FOREIGN KEY (`candidato_id`) REFERENCES `candidato`(`id`)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')

TABLES['Usuario'] = ('''
      CREATE TABLE `usuario` (
      `id` int(11) NOT NULL AUTO_INCREMENT,                     
      `login` varchar(20) NOT NULL,
      `senha` varchar(20) NOT NULL,
      PRIMARY KEY (`id`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')

TABLES['Eleitor'] = ('''
      CREATE TABLE `eleitor` (
      `id` int(11) NOT NULL AUTO_INCREMENT,                     
      `cpf` varchar(11) NOT NULL,
      PRIMARY KEY (`id`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')

#Criação das tabelas dentro da estrutura do banco de dados
for tabelaNome in TABLES:
      tabelaSQL = TABLES[tabelaNome]
      try:
            print('Criação da tabela {}:'.format(tabelaNome), end=' ')
            cursor.execute(tabelaSQL)
      except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                  print('Já existe')
            else:
                  print(err.msg)
      else:
            print('OK')

conn.commit()
#Fechamento da conexão
cursor.close()
conn.close()

