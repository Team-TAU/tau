import os
from .common import Common
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Local(Common):
    DEBUG = True
    # Testing
    INSTALLED_APPS = Common.INSTALLED_APPS
    INSTALLED_APPS += ('django_nose',)
    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
    NOSE_ARGS = [
        BASE_DIR,
        '-s',
        '--nologcapture',
        '--with-coverage',
        '--with-progressive',
        '--cover-package=tau'
    ]
