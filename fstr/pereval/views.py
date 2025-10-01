from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import PerevalAdded
from .serializers import PerevalAddedSerializer, PerevalInfoSerializer, PerevalUpdateSerializer


class SubmitData(APIView):
    """
    API для работы с данными о перевалах.
    Поддерживает методы: GET, POST.
    """

    @swagger_auto_schema(
        operation_description="Получить список перевалов по email пользователя",
        manual_parameters=[
            openapi.Parameter(
                'user__email',
                openapi.IN_QUERY,
                description="Email пользователя для поиска его перевалов",
                type=openapi.TYPE_STRING,
                required=True,
                example="user@example.com"
            )
        ],
        responses={
            200: PerevalInfoSerializer(many=True),
            400: openapi.Response(
                description="Не указан параметр user__email",
                examples={
                    'application/json': {
                        'error': 'Не указан параметр user__email'
                    }
                }
            ),
            404: openapi.Response(
                description="Записи не найдены",
                examples={
                    'application/json': {
                        'message': 'Записи не найдены'
                    }
                }
            )
        }
    )
    def get(self, request):
        email = request.query_params.get('user__email')
        if not email:
            return Response(
                {'error': 'Не указан параметр user__email'},
                status=status.HTTP_400_BAD_REQUEST
            )

        perevals = PerevalAdded.objects.filter(user__email=email)
        if not perevals.exists():
            return Response(
                {'message': 'Записи не найдены'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PerevalInfoSerializer(perevals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Создать новую запись о перевале",
        request_body=PerevalAddedSerializer,
        responses={
            201: openapi.Response(
                description="Успешное создание перевала",
                examples={
                    'application/json': {
                        'status': 200,
                        'message': None,
                        'id': 1
                    }
                }
            ),
            400: openapi.Response(
                description="Неверные данные",
                examples={
                    'application/json': {
                        'status': 400,
                        'message': 'Неверные данные',
                        'errors': {
                            'title': ['Это поле обязательно.']
                        },
                        'id': None
                    }
                }
            ),
            500: openapi.Response(
                description="Ошибка сервера",
                examples={
                    'application/json': {
                        'status': 500,
                        'message': 'Ошибка при сохранении: ...',
                        'id': None
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = PerevalAddedSerializer(data=request.data)

        if serializer.is_valid():
            return self.handle_valid_data(serializer)
        return self.handle_invalid_data(serializer)

    def handle_valid_data(self, serializer):
        try:
            pereval = serializer.save()
            return Response({
                'status': 200,
                'message': None,
                'id': pereval.id
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'status': 500,
                'message': f'Ошибка при сохранении: {str(e)}',
                'id': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def handle_invalid_data(self, serializer):
        return Response({
            'status': 400,
            'message': 'Неверные данные',
            'errors': serializer.errors,
            'id': None
        }, status=status.HTTP_400_BAD_REQUEST)


class PerevalRetrieveUpdateView(APIView):
    """
    API для получения и обновления конкретной записи о перевале.
    Поддерживает методы: GET, PATCH.
    """

    @swagger_auto_schema(
        operation_description="Получить информацию о перевале по ID",
        responses={
            200: PerevalInfoSerializer,
            404: openapi.Response(
                description="Перевал не найден",
                examples={
                    'application/json': {
                        'detail': 'Страница не найдена.'
                    }
                }
            )
        }
    )
    def get(self, request, pk):
        pereval = get_object_or_404(PerevalAdded, pk=pk)
        serializer = PerevalInfoSerializer(pereval)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Редактировать перевал (только со статусом 'new')",
        request_body=PerevalUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Успешное обновление",
                examples={
                    'application/json': {
                        'state': 1
                    }
                }
            ),
            400: openapi.Response(
                description="Ошибка валидации или неверный статус",
                examples={
                    'application/json': {
                        'state': 0,
                        'message': 'Запись нельзя редактировать, так как её статус не "new"'
                    }
                }
            ),
            404: openapi.Response(
                description="Перевал не найден",
                examples={
                    'application/json': {
                        'detail': 'Страница не найдена.'
                    }
                }
            ),
            500: openapi.Response(
                description="Ошибка сервера",
                examples={
                    'application/json': {
                        'state': 0,
                        'message': 'Ошибка при сохранении: ...'
                    }
                }
            )
        }
    )
    def patch(self, request, pk):
        pereval = get_object_or_404(PerevalAdded, pk=pk)

        if pereval.status != 'new':
            return Response({
                'state': 0,
                'message': 'Запись нельзя редактировать, так как её статус не "new"'
            }, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        if 'level' in data:
            level_data = data.pop('level')
            data.update({
                'level_winter': level_data.get('winter', ''),
                'level_summer': level_data.get('summer', ''),
                'level_autumn': level_data.get('autumn', ''),
                'level_spring': level_data.get('spring', '')
            })

        serializer = PerevalUpdateSerializer(pereval, data=data, partial=True)

        if serializer.is_valid():
            try:
                serializer.save()
                return Response({'state': 1}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'state': 0,
                    'message': f'Ошибка при сохранении: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                'state': 0,
                'message': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)