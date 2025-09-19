from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status


class PerevalAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            "beauty_title": "пер. ",
            "title": "Пхия",
            "other_titles": "Триев",
            "connect": "",
            "add_time": "2021-09-22 13:18:13",
            "user": {
                "email": "qwerty@mail.ru",
                "fam": "Пупкин",
                "name": "Василий",
                "otc": "Иванович",
                "phone": "+7 555 55 55"
            },
            "coords": {
                "latitude": "45.3842",
                "longitude": "7.1525",
                "height": "1200"
            },
            "level": {
                "winter": "",
                "summer": "1А",
                "autumn": "1А",
                "spring": ""
            },
            "images": [
                {"title": "Седловина", "image_url": "https://example.com/photo1.jpg"},
                {"title": "Подъём", "image_url": "https://example.com/photo2.jpg"}
            ]
        }

    def test_submit_data_success(self):
        response = self.client.post('/api/submitData/', self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 200)
        self.assertEqual(response.data['message'], 'Отправлено успешно')
        self.assertIsNotNone(response.data['id'])

    def test_submit_data_missing_required_field(self):
        invalid_payload = self.valid_payload.copy()
        del invalid_payload['title']

        response = self.client.post('/api/submitData/', invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 400)

    def test_submit_data_invalid_email(self):
        invalid_payload = self.valid_payload.copy()
        invalid_payload['user']['email'] = "invalid-email"

        response = self.client.post('/api/submitData/', invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 400)
