sudo apt-get install make  g++ clang libmysql++-dev apache2 mysql-server mono-gmcs subversion python3 python3-pip libapache2-mod-wsgi-py3

cd /var/www/html/onlineTest
sudo cp -r onlineTest.conf /etc/apache2/sites-available

sudo pip3 install django==1.9.9
sudo pip3 install pymysql

sudo python3 manage.py makemigrations
sudo python3 manage.py migrate
sudo python3 manage.py loaddata init_data.json
sudo python3 manage.py createsuperuser
sudo python3 manage.py collectstatic
sudo a2ensite onlineTest
sudo service apache2 restart
sudo pkill -9 judged
sudo judged