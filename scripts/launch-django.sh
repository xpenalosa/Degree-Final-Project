source /var/www/django/tornejos/tornejos_env/bin/activate
nohup python3 /var/www/django/tornejos/manage.py runserver > /var/log/django/django.log
echo "cd /var/www/django/tornejos"
