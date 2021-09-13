from django.contrib.auth import authenticate
from django.test import TestCase, Client
from django.urls import reverse


class TestViews(TestCase):

    def test_project_login(self):
        response = self.client.post("/login", {"user": "admin", "pass": "admin"})

        # client = Client()
        # response = client.post(reverse('login'), data={
        #     'user': 'admin',
        #     'pass': 'admin'
        # })
        #
        self.assertEqual(response.status_code, 200)

    def test_correct(self):
        user = authenticate(username='test', password='12test12')
        self.assertTrue((user is not None) and user.is_authenticated)

    def test_wrong_username(self):
        user = authenticate(username='wrong', password='12test12')
        self.assertFalse(user is not None and user.is_authenticated)

    def test_wrong_pssword(self):
        user = authenticate(username='test', password='wrong')
        self.assertFalse(user is not None and user.is_authenticated)
