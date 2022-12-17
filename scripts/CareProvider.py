import dbm
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

MySQL_Hostname = os.getenv('MYSQL_HOST')
MySQL_User = os.getenv('MYSQL_USERNAME')
MySQL_Password = os.getenv('MYSQL_PASSWORD')
MySQL_Database = os.getenv('MySQL_Database')

Database = create_engine(f'mysql+pymysql://{MySQL_User}:{MySQL_Password}@{MySQL_Hostname}:3306/{MySQL_Database}')

table_prod_accounts = """
create table if not exists production_accounts(
	`id` int(11) NOT NULL AUTO_INCREMENT,
  	`username` varchar(50) NOT NULL,
  	`password` varchar(255) NOT NULL,
  	`email` varchar(100) NOT NULL,
    `account_type` varchar(50) NOT NULL,
    `mrn` varchar(50) NULL,
    `date_created` datetime NULL,
    `last_login` datetime NULL,
    PRIMARY KEY (`id`)
); 
"""
Database.execute(table_prod_accounts)
