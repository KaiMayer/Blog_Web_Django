import sys, os
#INTERP is present twice so that the new python interpreter
#knows the actual virtual environment path
INTERP = "/home/centrgr2/django_project/venv/bin/python3"

if sys.executable != INTERP:os.execl(INTERP, INTERP, *sys.argv)

cwd = os.getcwd()
sys.path.append(cwd)
sys.path.append(cwd + '/django_project')

sys.path.insert(0,cwd+'/venv/bin')
sys.path.insert(0,cwd+'/venv/lib/python3.6/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = "django_project.settings"
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()