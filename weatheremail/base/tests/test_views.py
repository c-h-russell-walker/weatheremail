from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory

from base.models import Location
from base.views import SignUpView


class TestSuccessView(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(TestSuccessView, cls).setUpTestData()
        cls.location, _ = Location.objects.get_or_create(city='Austin')

    def test_we_have_email_input(self):
        request = RequestFactory().get(reverse('base:signup-view'))

        response = SignUpView.as_view()(request)

        # We should probably parse the content with something like beautifulsoup to do this better
        # For now just really a sanity-check test
        self.assertIn('id_email', response.content)

    def test_we_get_success_message(self):
        email = 'victorwooten@example.com'
        post_data = {
            'email': email,
            'location': self.location.id
        }
        request = RequestFactory().post(reverse('base:signup-view'), data=post_data)
        request._dont_enforce_csrf_checks = True

        response = SignUpView.as_view()(request)

        self.assertEqual(response.status_code, 200)

        self.assertIn('Success.', response.content)

        self.assertIn(email, response.content)

