from django.conf.urls import url

from base import views

urlpatterns = [
    url(r'$',
        views.SignUpView.as_view(),
        name='signup_view'),
]