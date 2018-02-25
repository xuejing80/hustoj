sudo apt-get install make  g++ clang libmysql++-dev apache2 mysql-server mono-gmcs subversion python3 python3-pip libapache2-mod-wsgi-py3

sudo cp -r onlineTest.conf /etc/apache2/sites-available

sudo pip3 install -i https://pypi.douban.com/simple/ django==1.9.13
sudo pip3 install -i https://pypi.douban.com/simple/ pymysql

cd /var/www/html/onlineTest
sudo python3 manage.py makemigrations
sudo python3 manage.py migrate
sudo python3 manage.py loaddata init_data.json
sudo python3 manage.py createsuperuser
sudo python3 manage.py collectstatic
sudo a2ensite onlineTest
sudo a2dissite 000-default.conf
sudo service apache2 restart

sudo rm /home/judge/log/*
sudo pkill -9 judged
sudo judged
