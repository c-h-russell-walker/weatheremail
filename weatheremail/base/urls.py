from django.conf.urls import url

from weatheremail.base import views

urlpatterns = [
    url(r'$',
        views.SignUpView.as_view(),
        name='signup-view'),
]
