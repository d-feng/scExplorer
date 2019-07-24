# Single Cell Explorer 
Thank you for visiting wiki of Single Cell Explorer. 

Authors: Di Feng, Dechao Shan

Contact: di_feng@yahoo.com

### Site URL: 
##### http://singlecellexplorer.org

##### http://54.159.6.229:8000/

### source code, database files, python scripts for Jupyter notebook
http://54.159.6.229/download.html

### Notebook URL: 
http://54.159.6.229/analysis.html

### Installation guide 
http://54.159.6.229/install.html

### Installation of Single Cell Explorer from Source
#### Update (based on ubuntu 18.04 or 16.04)

###### sudo apt-get update
###### sudo apt-get install -y build-essential
###### sudo apt-get install -y ssh libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev zip unzip libfftw3-dev libcurl3 openssl

#### Install python3

###### sudo apt-get install -y python3 python3-pip python3-dev

#### Install MongoDB, create database paths, and start MongoDB server
###### cd ~
###### mkdir -p mongodb
###### cd mongodb
###### wget https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1604-4.0.10.tgz
###### tar -zxvf mongodb-linux-x86_64-ubuntu1604-4.0.10.tgz
###### mkdir scdb
###### mkdir log
###### sudo ./mongodb-linux-x86_64-ubuntu1604-4.0.10/bin/mongod --dbpath "./scdb" --port 27017 --wiredTigerCacheSizeGB 1 --fork --logpath "./log/scdb.log"

#### Load database schema & sample data into MongoDB
###### cd ~/mongodb/
###### wget http://54.159.6.229/downloads/scDB.zip
###### unzip scDB.zip
###### mkdir dumpfiles
###### mv scDB dumpfiles
###### mongodb-linux-x86_64-ubuntu1604-4.0.10/bin/mongorestore dumpfiles

#### Launch Single Cell Explorer web application

###### sudo pip3 install --upgrade pip
###### sudo pip3 install numpy gunicorn pymongo sklearn pandas django==2.2 torchvision 

###### cd ~
###### mkdir singleCell
###### cd singleCell

###### wget http://54.159.6.229/downloads/singleCellExplorer.zip
###### unzip singleCellExplorer.zip
###### cd singleCellExplorer

###### python3 manage.py runserver 0.0.0.0:8000
    
