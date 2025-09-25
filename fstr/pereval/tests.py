from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import PerevalAdded


class PerevalAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            "beauty_title": "пер. ",
            "title": "Пхия",
            "other_titles": "Триев",
            "connect": "",
            "user": {
                "email": "qwerty@mail.ru",
                "fam": "Пупкин",
                "name": "Василий",
                "otc": "Иванович",
                "phone": "+7 555 55 55"
            },
            "coords": {
                "latitude": 45.3842,
                "longitude": 7.1525,
                "height": 1200
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 200)
        self.assertIsNotNone(response.data['id'])

    def test_submit_data_missing_required_field(self):
        invalid_payload = self.valid_payload.copy()
        del invalid_payload['title']

        response = self.client.post('/api/submitData/', invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 400)

    def test_get_pereval_by_id(self):
        # Создаем запись
        post_response = self.client.post('/api/submitData/', self.valid_payload, format='json')
        pereval_id = post_response.data['id']

        # Получаем запись по ID
        response = self.client.get(f'/api/submitData/{pereval_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Пхия')
        self.assertEqual(response.data['status'], 'new')

    def test_get_nonexistent_pereval(self):
        response = self.client.get('/api/submitData/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_perevals_by_email(self):
        # Создаем запись
        self.client.post('/api/submitData/', self.valid_payload, format='json')

        # Получаем записи по email
        response = self.client.get('/api/submitData/?user__email=qwerty@mail.ru')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user']['email'], 'qwerty@mail.ru')

    def test_get_perevals_by_nonexistent_email(self):
        response = self.client.get('/api/submitData/?user__email=nonexistent@mail.ru')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_pereval_success(self):
        # Создаем запись
        post_response = self.client.post('/api/submitData/', self.valid_payload, format='json')
        pereval_id = post_response.data['id']

        # Обновляем запись
        update_data = {
            "title": "Обновленное название",
            "coords": {
                "latitude": 46.0,
                "longitude": 8.0,
                "height": 1500
            }
        }
        response = self.client.patch(f'/api/submitData/{pereval_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['state'], 1)

    def test_update_pereval_user_data_protected(self):
        # Создаем запись
        post_response = self.client.post('/api/submitData/', self.valid_payload, format='json')
        pereval_id = post_response.data['id']

        # Пытаемся изменить данные пользователя (должно игнорироваться)
        update_data = {
            "title": "Новое название",
            "user": {
                "email": "newemail@mail.ru",
                "fam": "НоваяФамилия"
            }
        }
        response = self.client.patch(f'/api/submitData/{pereval_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что email не изменился
        get_response = self.client.get(f'/api/submitData/{pereval_id}/')
        self.assertEqual(get_response.data['user']['email'], 'qwerty@mail.ru')

    def test_update_pereval_wrong_status(self):
        # Создаем запись
        post_response = self.client.post('/api/submitData/', self.valid_payload, format='json')
        pereval_id = post_response.data['id']

        # Меняем статус на "на модерации"
        pereval = PerevalAdded.objects.get(id=pereval_id)
        pereval.status = 'pending'
        pereval.save()

        # Пытаемся обновить
        update_data = {"title": "Новое название"}
        response = self.client.patch(f'/api/submitData/{pereval_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['state'], 0)
        self.assertIn('статус не "new"', response.data['message'])

    def test_update_nonexistent_pereval(self):
        response = self.client.patch('/api/submitData/999/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)