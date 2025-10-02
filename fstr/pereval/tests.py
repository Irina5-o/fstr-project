from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import PerevalAdded, PerevalUser, PerevalCoords, PerevalImage


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

    # Базовые тесты создания
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

    # Тесты валидации данных
    def test_submit_data_invalid_email(self):
        invalid_payload = self.valid_payload.copy()
        invalid_payload['user']['email'] = 'invalid-email'

        response = self.client.post('/api/submitData/', invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_data_invalid_coords(self):
        invalid_payload = self.valid_payload.copy()
        invalid_payload['coords']['latitude'] = 'invalid-latitude'

        response = self.client.post('/api/submitData/', invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_data_empty_images(self):
        payload = self.valid_payload.copy()
        payload['images'] = []

        response = self.client.post('/api/submitData/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Тесты получения данных
    def test_get_pereval_by_id(self):
        post_response = self.client.post('/api/submitData/', self.valid_payload, format='json')
        pereval_id = post_response.data['id']

        response = self.client.get(f'/api/submitData/{pereval_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Пхия')
        self.assertEqual(response.data['status'], 'new')

    def test_get_nonexistent_pereval(self):
        response = self.client.get('/api/submitData/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_perevals_by_email(self):
        self.client.post('/api/submitData/', self.valid_payload, format='json')

        response = self.client.get('/api/submitData/?user__email=qwerty@mail.ru')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user']['email'], 'qwerty@mail.ru')

    def test_get_perevals_by_nonexistent_email(self):
        response = self.client.get('/api/submitData/?user__email=nonexistent@mail.ru')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_perevals_without_email_param(self):
        response = self.client.get('/api/submitData/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user__email', str(response.data))

    # Тесты обновления данных
    def test_update_pereval_success(self):
        post_response = self.client.post('/api/submitData/', self.valid_payload, format='json')
        pereval_id = post_response.data['id']

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

        # Проверяем, что данные действительно обновились
        get_response = self.client.get(f'/api/submitData/{pereval_id}/')
        self.assertEqual(get_response.data['title'], 'Обновленное название')
        self.assertEqual(get_response.data['coords']['latitude'], 46.0)

    def test_update_pereval_user_data_protected(self):
        post_response = self.client.post('/api/submitData/', self.valid_payload, format='json')
        pereval_id = post_response.data['id']

        update_data = {
            "title": "Новое название",
            "user": {
                "email": "newemail@mail.ru",
                "fam": "НоваяФамилия"
            }
        }
        response = self.client.patch(f'/api/submitData/{pereval_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        get_response = self.client.get(f'/api/submitData/{pereval_id}/')
        self.assertEqual(get_response.data['user']['email'], 'qwerty@mail.ru')
        self.assertEqual(get_response.data['user']['fam'], 'Пупкин')  # Фамилия не должна измениться

    def test_update_pereval_wrong_status(self):
        post_response = self.client.post('/api/submitData/', self.valid_payload, format='json')
        pereval_id = post_response.data['id']

        pereval = PerevalAdded.objects.get(id=pereval_id)
        pereval.status = 'pending'
        pereval.save()

        update_data = {"title": "Новое название"}
        response = self.client.patch(f'/api/submitData/{pereval_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['state'], 0)
        self.assertIn('статус не "new"', response.data['message'])

    def test_update_nonexistent_pereval(self):
        response = self.client.patch('/api/submitData/999/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_pereval_with_level_data(self):
        post_response = self.client.post('/api/submitData/', self.valid_payload, format='json')
        pereval_id = post_response.data['id']

        update_data = {
            "level": {
                "winter": "2А",
                "summer": "1Б",
                "autumn": "1Б",
                "spring": "2А"
            }
        }
        response = self.client.patch(f'/api/submitData/{pereval_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['state'], 1)

    # Тесты модели
    def test_pereval_user_creation(self):
        user = PerevalUser.objects.create(
            email="test@example.com",
            fam="Иванов",
            name="Петр",
            otc="Сергеевич",
            phone="+79991234567"
        )
        self.assertEqual(str(user), "Иванов Петр (test@example.com)")

    def test_pereval_coords_creation(self):
        coords = PerevalCoords.objects.create(
            latitude=45.1234,
            longitude=7.5678,
            height=1500
        )
        self.assertIn("Широта: 45.1234", str(coords))

    def test_pereval_added_creation(self):
        user = PerevalUser.objects.create(
            email="test@example.com",
            fam="Иванов",
            name="Петр"
        )
        coords = PerevalCoords.objects.create(
            latitude=45.1234,
            longitude=7.5678,
            height=1500
        )
        pereval = PerevalAdded.objects.create(
            beauty_title="пер.",
            title="Тестовый перевал",
            user=user,
            coords=coords
        )
        self.assertIn("пер. Тестовый перевал", str(pereval))

    def test_pereval_image_creation(self):
        user = PerevalUser.objects.create(
            email="test@example.com",
            fam="Иванов",
            name="Петр"
        )
        coords = PerevalCoords.objects.create(
            latitude=45.1234,
            longitude=7.5678,
            height=1500
        )
        pereval = PerevalAdded.objects.create(
            beauty_title="пер.",
            title="Тестовый перевал",
            user=user,
            coords=coords
        )
        image = PerevalImage.objects.create(
            pereval=pereval,
            title="Тестовое фото",
            image_url="https://example.com/test.jpg"
        )
        self.assertEqual(str(image), "Тестовое фото - https://example.com/test.jpg")

    def test_pereval_status_choices(self):
        """Тестируем все возможные статусы перевала"""
        user = PerevalUser.objects.create(
            email="status@example.com",
            fam="Тестов",
            name="Статус"
        )

        # Тестируем все возможные статусы с РАЗНЫМИ координатами
        statuses = ['new', 'pending', 'accepted', 'rejected']
        for i, status_choice in enumerate(statuses):
            # Создаем уникальные координаты для каждого перевала
            coords = PerevalCoords.objects.create(
                latitude=45.1234 + i * 0.1,  # Разные координаты
                longitude=7.5678 + i * 0.1,
                height=1500 + i * 100
            )

            pereval = PerevalAdded.objects.create(
                beauty_title="пер.",
                title=f"Перевал {status_choice}",
                user=user,
                coords=coords,
                status=status_choice
            )
            self.assertEqual(pereval.status, status_choice)

    def test_duplicate_user_email(self):
        """Тестируем создание перевалов с одинаковым email пользователя"""
        # Создаем первого пользователя с перевалом
        response1 = self.client.post('/api/submitData/', self.valid_payload, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        print(f"Первый перевал создан: {response1.data}")

        # Получаем созданного пользователя
        pereval1 = PerevalAdded.objects.get(id=response1.data['id'])
        original_user = pereval1.user
        print(f"Создан пользователь: {original_user.email}, {original_user.fam} {original_user.name}")

        # Создаем второй перевал с ТЕМ ЖЕ email
        second_payload = {
            "beauty_title": "пер. ",
            "title": "Второй перевал",
            "other_titles": "Другое название",
            "connect": "соединение",
            "user": {
                "email": "qwerty@mail.ru",  # ТОТ ЖЕ EMAIL
                "fam": "Пупкин",  # Те же данные (должны игнорироваться)
                "name": "Василий",
                "otc": "Иванович",
                "phone": "+7 555 55 55"
            },
            "coords": {
                "latitude": 46.3842,  # Другие координаты
                "longitude": 8.1525,
                "height": 1300
            },
            "level": {
                "winter": "1А",
                "summer": "",
                "autumn": "",
                "spring": "1А"
            },
            "images": [
                {"title": "Другое фото", "image_url": "https://example.com/photo3.jpg"}
            ]
        }

        response2 = self.client.post('/api/submitData/', second_payload, format='json')

        # ОТЛАДКА: выводим ошибку если есть
        if response2.status_code != status.HTTP_201_CREATED:
            print(f"Ошибка при создании второго перевала:")
            print(f"Status: {response2.status_code}")
            print(f"Data: {response2.data}")
            # Проверим, что говорит сериализатор
            from .serializers import PerevalAddedSerializer
            serializer = PerevalAddedSerializer(data=second_payload)
            if not serializer.is_valid():
                print(f"Ошибки сериализатора: {serializer.errors}")

        self.assertEqual(response2.status_code, status.HTTP_201_CREATED,
                         f"Второй перевал не создался. Ошибка: {response2.data if response2.status_code != 201 else ''}")

        pereval_id_2 = response2.data['id']
        print(f"Второй перевал создан: {response2.data}")

        # Проверяем, что оба перевала создались
        pereval2 = PerevalAdded.objects.get(id=pereval_id_2)

        # Проверяем, что они ссылаются на одного и того же пользователя
        self.assertEqual(pereval1.user.id, pereval2.user.id,
                         "Перевалы ссылаются на разных пользователей!")
        self.assertEqual(pereval1.user.email, pereval2.user.email,
                         "Email пользователей не совпадают!")

        # Проверяем, что данные пользователя не изменились
        self.assertEqual(pereval2.user.fam, 'Пупкин', "Фамилия пользователя изменилась!")
        self.assertEqual(pereval2.user.name, 'Василий', "Имя пользователя изменилось!")

        # Проверяем, что данные перевалов разные
        self.assertNotEqual(pereval1.title, pereval2.title, "Названия перевалов совпадают!")
        self.assertNotEqual(pereval1.coords.id, pereval2.coords.id, "Координаты перевалов совпадают!")

        print("Все проверки пройдены!")

    # Интеграционные тесты
    def test_full_workflow(self):
        # 1. Создаем перевал
        post_response = self.client.post('/api/submitData/', self.valid_payload, format='json')
        pereval_id = post_response.data['id']
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)

        # 2. Получаем созданный перевал
        get_response = self.client.get(f'/api/submitData/{pereval_id}/')
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['title'], 'Пхия')

        # 3. Обновляем перевал
        update_data = {
            "title": "Обновленное название в workflow",
            "coords": {
                "latitude": 47.0,
                "longitude": 9.0,
                "height": 2000
            }
        }
        patch_response = self.client.patch(f'/api/submitData/{pereval_id}/', update_data, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        # 4. Проверяем обновление
        updated_response = self.client.get(f'/api/submitData/{pereval_id}/')
        self.assertEqual(updated_response.data['title'], 'Обновленное название в workflow')
        self.assertEqual(updated_response.data['coords']['height'], 2000)

        # 5. Ищем по email
        email_response = self.client.get('/api/submitData/?user__email=qwerty@mail.ru')
        self.assertEqual(email_response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(item['id'] == pereval_id for item in email_response.data))

    # Тесты граничных случаев
    def test_invalid_http_methods(self):
        # Тестируем неподдерживаемые методы
        response_put = self.client.put('/api/submitData/1/', {})
        self.assertEqual(response_put.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response_delete = self.client.delete('/api/submitData/1/')
        self.assertEqual(response_delete.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_empty_payload(self):
        response = self.client.post('/api/submitData/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 400)