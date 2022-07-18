from django.test import TestCase


# Create your tests here.
class URL_pages_Tests(TestCase):
    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_about(self):
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)

    def test_review(self):
        response = self.client.get('/review')
        self.assertEqual(response.status_code, 200)

    def test_contact(self):
        response = self.client.get('/contact')
        self.assertEqual(response.status_code, 200)

    def test_jobs(self):
        response = self.client.get('/jobs')
        self.assertEqual(response.status_code, 200)

    def test_faqs(self):
        response = self.client.get('/faqs')
        self.assertEqual(response.status_code, 200)

    def test_tandc(self):
        response = self.client.get('/tandc')
        self.assertEqual(response.status_code, 200)

    def test_privacy(self):
        response = self.client.get('/privacy')
        self.assertEqual(response.status_code, 200)

    def test_sitemap(self):
        response = self.client.get('/sitemap')
        self.assertEqual(response.status_code, 200)

    def test_sitemapseo(self):
        response = self.client.get('/sitemapseo')
        self.assertEqual(response.status_code, 200)
