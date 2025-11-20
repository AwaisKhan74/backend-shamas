from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import FileManager
from .serializers import FileManagerSerializer


class FileManagerUploadTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            work_id='ADMIN100',
            username='adminuser',
            email='adminuser@example.com',
            password='Admin@12345',
            role='ADMIN'
        )
        login_url = reverse('users:auth-login')
        response = self.client.post(login_url, {
            'email': 'adminuser@example.com',
            'password': 'Admin@12345'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['access_token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_file_upload(self):
        upload_url = reverse('files-list')
        file_content = SimpleUploadedFile('sample.txt', b'Hello World', content_type='text/plain')
        payload = {
            'file': file_content,
            'file_type': 'DOCUMENT',
            'purpose': 'GENERAL',
            'description': 'Test file'
        }
        response = self.client.post(upload_url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(FileManager.objects.exists())
        instance = FileManager.objects.latest('id')
        serialized = FileManagerSerializer(instance).data
        self.assertEqual(serialized['file_name'], 'sample.txt')
        self.assertEqual(serialized['purpose'], 'GENERAL')
