cd /home/judge

apt-get -y install libmysql++-dev python3 python3-pip redis-server supervisor

cp src/install/onlineTestNginx.conf /etc/nginx/sites-available
cp src/install/daphne.conf /etc/supervisor/conf.d
cp src/install/runworker.conf /etc/supervisor/conf.d

cp -r src/onlineTest /home/judge
chown -R judge:judge /home/judge/onlineTest

cd /home/judge/onlineTest

pip3 install -U pip -i https://pypi.douban.com/simple/
pip3 install django==1.9.9 -i https://pypi.douban.com/simple/
pip3 install pymysql -i https://pypi.douban.com/simple/
pip3 install -i https://pypi.douban.com/simple/ asgi_redis
pip3 install -i https://pypi.douban.com/simple/ channels==1.1.8
pip3 install -i https://pypi.douban.com/simple/ python-docx
pip3 install -i https://pypi.douban.com/simple/ xlwt

mkdir -r /home/judge/log
chown -R judge:judge /home/judge/log

python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py loaddata init_data.json
python3 manage.py createsuperuser
python3 manage.py collectstatic
ln -s /etc/nginx/sites-available/onlineTestNginx.conf /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
service supervisor restart
service nginx restart

service php5-fpm stop
service memcached stop
