from django import forms

from base.models import WeatherUser


class SignUpForm(forms.ModelForm):

    class Meta:
        model = WeatherUser
        fields = [
            'email',
            # 'location'  # TODO - update on the actual model to get this working
        ]