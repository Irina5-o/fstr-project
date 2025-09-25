from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import PerevalAdded
from .serializers import PerevalAddedSerializer, PerevalInfoSerializer, PerevalUpdateSerializer


class SubmitData(APIView):
    """
    API для работы с данными о перевалах.
    Поддерживает методы: GET, POST.
    """

    def get(self, request):
        """
        GET /submitData/?user__email=<email> - получение записей по email
        """
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

    def post(self, request):
        """
        POST /submitData/ - создание новой записи о перевале.
        """
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

    def get(self, request, pk):
        """
        GET /submitData/<id> - получение одной записи по ID
        """
        pereval = get_object_or_404(PerevalAdded, pk=pk)
        serializer = PerevalInfoSerializer(pereval)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """
        PATCH /submitData/<id> - редактирование существующей записи
        """
        pereval = get_object_or_404(PerevalAdded, pk=pk)

        # Проверка статуса записи
        if pereval.status != 'new':
            return Response({
                'state': 0,
                'message': 'Запись нельзя редактировать, так как её статус не "new"'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Обрабатываем поле level если оно пришло
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