from django import forms

from base.models import WeatherUser, Location


class SignUpForm(forms.ModelForm):

    location = forms.ModelChoiceField(
        queryset=Location.objects.all().order_by('city'),
        empty_label='Where do you live?'
    )

    class Meta:
        model = WeatherUser
        fields = [
            'email',
            'location'
        ]
        labels = {
            'email': 'Email Address',
        }

