# InDJ_MIR project's README
This project is a recommendation engine in order to recommend songs, channels for user.
Some librarys are used in this project and command line

sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1
mkdir data
cd data/
mkdir source_code
sudo apt update
sudo install python3-pip
export LC_ALL=C
pip3 install librosa
pip3 install django
pip3 install djangorestframework
pip3 install markdown
pip3 install django-filter
pip3 install pandas
sudo apt install mysql-server
sudo apt install libmysqlclient-dev
pip3 install mysqlclient
pip3 install h5py
sudo apt install awscli
aws configure
pip3 install boto3
sudo apt install ffmpeg
pip3 install fastdtw
pip3 install pydub
pip3 install -U scikit-learn
pip3 install eyed3
pip3 install simplejson
pip3 install hmmlearn
pip3 install matplotlib
pip3 install youtube_dl
pip3 install xlrd
pip3 install bs4
sudo apt install python3-tk
pip3 install googletrans
pip3 install nltk
pip3 install python-forecastio
pip3 install shapely
pip3 install geopy


sudo scp -i /data/<key>.pem -r /data/workspace/indj-mir/ root@<domain>:~/data/source_code

sudo ssh -i /data/<key>.pem root@<domain

curl -X POST http://localhost:8000/batches/

curl -H "Content-Type: application/json" -X POST -d '{"sourceUID":"210039330926329109"}' http://localhost:8000/compare/source_uid/

nohup python manage.py runserver 0.0.0.0:8000 &


-------------------------------------------------------------------------------------------
MSQL
-------------------------------------------------------------------------------------------
mysql -u<user_name> -p<password> -h<domain>
mysqldump --single-transaction -h<domain> -u<user_name> -p<password> <schema> > <path_to_storage>
mysql -h<domain> -u<user_name -p<password> <schema> < <path_to_storage>



-------------------------------------------------------------------------------------------
SET PYTHON3 AS DEFAULT ENVIRONMENT
-------------------------------------------------------------------------------------------
alias python=python3
source ~/.bashrc

-------------------------------------------------------------------------------------------
INSTALL WORDNET OF NLTK LIBRARY
-------------------------------------------------------------------------------------------
In terminal write commanline 'python'
import nltk

nltk.download('wordnet')


