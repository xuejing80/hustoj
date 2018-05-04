sudo apt-get install libmysql++-dev python3 python3-pip

sudo apt-get install nginx supervisor

sudo cp -r onlineTestNginx.conf /etc/nginx/sites-available
sudo cp daphne.conf /etc/supervisor/conf.d
sudo cp runworker.conf /etc/supervisor/conf.d

cd /var/www/html/onlineTest

pip3 install -U pip -i https://pypi.douban.com/simple/
sudo pip3 install django==1.9.9 -i https://pypi.douban.com/simple/
sudo pip3 install pymysql -i https://pypi.douban.com/simple/
sudo pip3 install -i https://pypi.douban.com/simple/ channels==1.1.8
sudo pip3 install -i https://pypi.douban.com/simple/ python-docx
sudo pip3 install -i https://pypi.douban.com/simple/ xlwt
sudo pip3 install -i https://pypi.douban.com/simple/ asgi_redis

sudo chown -R judge:judge /home/judge/log

sudo python3 manage.py makemigrations
sudo python3 manage.py migrate
sudo python3 manage.py loaddata init_data.json
sudo python3 manage.py createsuperuser
sudo python3 manage.py collectstatic
sudo ln -s /etc/nginx/sites-available/onlineTestNginx.conf /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo service apache2 stop
sudo service nginx restart
sudo service supervisor restart 
sudo pkill -9 judged
sudo judged