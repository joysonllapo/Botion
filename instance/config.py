import os
user=os.getenv('USER')
password=os.getenv('PASSWORD')
database=os.getenv('DATABASE')
host=os.getenv('HOST')

SECRET_KEY = 'p9Bv<3Eid9%$i01'
SQLALCHEMY_DATABASE_URI = f'mysql://{user}:{password}@{host}/{database}'
#SQLALCHEMY_DATABASE_URI = 'mysql://kow32hbh1fgp:pscale_pw_hshrEYiVkFxKU9cnpCgM8CNdpqTqvsihW6ulE0B6BRc@dm651z4ad7nr8.us-east-3.psdb.cloud/koptica_db?ssl=true'
