from django.test import TestCase

from base.forms import SignUpForm
from base.models import Location


class SignUpFormTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(SignUpFormTestCase, cls).setUpTestData()
        cls.location, _ = Location.objects.get_or_create(city='New York')

    def test_form_does_not_sign_up_duplicate(self):

        form = SignUpForm({
            'email': 'billysheehan@example.com',
            'location': self.location.id
        })

        # We should be able to save with no error
        user = form.save()

        # Using same email more than once is not allowed
        with self.assertRaises(ValueError):
            form_two = SignUpForm({
                'email': 'billysheehan@example.com',
                'location': self.location.id
            })
            form_two.save()
