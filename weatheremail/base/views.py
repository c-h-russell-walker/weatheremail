from django.db import IntegrityError
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.decorators.csrf import csrf_protect

from weatheremail.base.forms import SignUpForm


class SignUpView(View):

    def dispatch(self, request, *args, **kwargs):
        return super(SignUpView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {
            'form': SignUpForm()
        }
        return render(request=request, template_name='signup.html', context=context)

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        form = SignUpForm(request.POST)
        context = {
            'form': form
        }

        if form.is_valid():
            # We have custom validation on the email to make sure user doesn't already exist
            weather_user = form.save()
            context['email'] = weather_user.email
            return render(request=request, template_name='success.html', context=context)

        # TODO - Is there more we want to do besides just show them an error?
        return render(request=request, template_name='signup.html', context=context)

