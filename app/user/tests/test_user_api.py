from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')

def create_user(**params):

    return get_user_model().objects.create(**params)


class PublicUserAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
    
    def test_user_create_successful(self):

        payload = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'testpass123'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)


    def test_user_with_email_exists_error(self):

        create_user(
            email='test@example.com',
            password='testpass123'
        )

        payload = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_password_too_short_error(self):

        payload = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'test'
            }


        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
        email=payload['email']).exists()
        self.assertFalse(user_exists)


    def test_create_token(self):

        user_details = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'testpass123'
        }

        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password']
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)


    def test_create_token_bad_credentials(self):

        create_user(
            email='test@example.com',
            password='testpass123'
        )

        payload = {
            'email': 'test@example.com',
            'password': 'BADPASSWORD'
            }

        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    
    def test_create_token_blank_password(self):
        payload = {
        'email': 'test@example.com',
        'password':''
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)
        

