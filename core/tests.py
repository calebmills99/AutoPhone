from django.test import TestCase, Client
from django.urls import reverse


class IndexViewTest(TestCase):
    """Test the index view."""
    
    def test_index_view(self):
        """Test that index view returns 200 status code."""
        client = Client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome to AutoPhone Django Project!')
