import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'acm_hackathon.settings')


application = get_wsgi_application()
# This safely handles loading all CSS, JS, and image assets on Render
application = WhiteNoise(application, root=os.path.join(os.path.dirname(__file__), 'staticfiles'))
