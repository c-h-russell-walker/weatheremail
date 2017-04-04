from django.conf.urls import url

from base import views

urlpatterns = [
    url(r'$',
        views.TestView.as_view(),
        name='test_view'),
]