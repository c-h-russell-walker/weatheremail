from django.shortcuts import render
from django.views.generic import View


class TestView(View):

    def dispatch(self, request, *args, **kwargs):
        return super(TestView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        h_world = 'this is our hello world message'
        context = {
            'hello_world': h_world
        }
        return render(request=request, template_name='index.html', context=context)
