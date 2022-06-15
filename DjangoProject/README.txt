1.Download files
2.Install Django via pip (pip install django)
3.Open Pycharm
4.Open Directory "DjangoProject" as project
5.In Pycharm-Terminal run:
	5.1 python manage.py migrate
	5.2 python manage.py runserver
	
Run with HTTPS:
python manage.py runserver_plus --cert-file cert.pem --key-file key.pem --keep-meta-shutdown 0.0.0.0:443
