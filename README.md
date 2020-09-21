# Single Cell Explorer (ver 1.1.0)
Thank you for visiting wiki of Single Cell Explorer. 
Singel Cell Explorer is available open-source under the GNU LGPLv3 license. This web application only run on Linux. 

Authors: Di Feng, Dechao Shan

Contact: di_feng@yahoo.com

### Site URL: 
##### http://singlecellexplorer.org

##### http:18.204.165.197

### Source code, database files, python scripts for Jupyter notebook
http://18.204.165.197/download.html

### Jupyter Notebook walkthrough 
http://18.204.165.197/analysis.html

### Installation guide 
http://18.204.165.197/install.html

### Installation of Single Cell Explorer from Source

##### quickest way: run setup shell scripts from http://18.204.165.197/downloads/setupSCexplorer.sh

### From console (step by step)
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
###### wget http://18.204.165.197/downloads/scDB.zip
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

###### wget http://18.204.165.197/downloads/singleCellExplorer.zip
###### unzip singleCellExplorer.zip
###### cd singleCellExplorer

###### python3 manage.py runserver 0.0.0.0:8000

# usage
--For Data registration: 
The following items are mandatory.
study: The name of the study, which should include all the samples as a collection. 
species: Human, Mouse, etc
tissue: The biological source of the samples (blood, inflamed, uninvolved etc). 
mapType:  Currently, we support tsne, umap, and phate.
name: The map name will be used in the single cell explorer map viewer.  

The following information is optional, but we encourage you to use.
disease: This help to create a collected atlas of normal tissue or disease tissue.
source: You can use internal or external to distinguish the data source.
author: This indicate the contact person of the data or author who created the map in single cell explorer. 
subjectid: Subject ID, which represent the each donor in the study, should be unique. Sometime, there are multiple tissue samples could be collected from the same individual or subject ID. 
  
Usage:
For a study that collect blood, uninvolved, and involved samples from multiple subjects. We can create the following dictionary. You can also add more meta information in the dictionary.    

mapinfo={       
          “study”:”Disease Collection”,
          “species”: “Homo sapien”,
          “tissue”: “involved”,
          “mapType”:”tsne”,
          “name”:”involved sample”, 
          “source”:”public data”,
          “author”:”Me”,
          “subjectid”:”CT0001”,
          “comment”:””       
         }

--Multiple Sample Comparison
Once you registered all the samples from a study. You can cross-compare gene expression among multiple donor/subjects within that study.  You can select 1) the study 2) the right tissue to compare, 3) the cell type 4) the gene of interest for comparison.    

