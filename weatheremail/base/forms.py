from django import forms
from django.core.exceptions import ValidationError

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

    def clean_email(self):
        email = self.cleaned_data['email']

        if WeatherUser.objects.filter(email=email).exists():
            raise ValidationError('User has already signed up with this email.')

        return email
