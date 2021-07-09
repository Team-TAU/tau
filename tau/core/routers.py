from rest_framework.routers import DefaultRouter

class OptionalSlashRouter(DefaultRouter):

    def __init__(self, *args, **kwargs):
        super(DefaultRouter, self).__init__(*args, **kwargs)
        self.trailing_slash = '/?'
