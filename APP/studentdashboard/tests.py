from django.test import TestCase

# Create your tests here.
class URL_pages_Tests(TestCase):
    def test_homepage(self):
        response = self.client.get('/s-dash/')
        self.assertEqual(response.status_code, 200)
    def test_buttons(self):
        response = self.client.get('/s-dash/buttons')
        self.assertEqual(response.status_code, 200)
    def test_cards(self):
        response = self.client.get('/s-dash/cards')
        self.assertEqual(response.status_code, 200)
    def test_util_color(self):
        response = self.client.get('/s-dash/util-color')
        self.assertEqual(response.status_code, 200)
    def test_util_border(self):
        response = self.client.get('/s-dash/util-border')
        self.assertEqual(response.status_code, 200)
    def test_util_animation(self):
        response = self.client.get('/s-dash/util-animation')
        self.assertEqual(response.status_code, 200)
    def test_util_other(self):
        response = self.client.get('/s-dash/util-other')
        self.assertEqual(response.status_code, 200)
    def test_charts(self):
        response = self.client.get('/s-dash/charts')
        self.assertEqual(response.status_code, 200)
    def test_tables(self):
        response = self.client.get('/s-dash/tables')
        self.assertEqual(response.status_code, 200)
    def test_blank(self):
        response = self.client.get('/s-dash/blank')
        self.assertEqual(response.status_code, 200)
    def test_404(self):
        response = self.client.get('/s-dash/404')
        self.assertEqual(response.status_code, 200)
