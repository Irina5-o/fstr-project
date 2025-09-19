from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PerevalAddedSerializer


class SubmitData(APIView):
    """
    API endpoint для добавления данных о перевале.
    Только метод POST для Спринта 1.
    """

    def post(self, request):
        serializer = PerevalAddedSerializer(data=request.data)

        if serializer.is_valid():
            try:
                pereval = serializer.save()
                response_data = {
                    'status': status.HTTP_200_OK,
                    'message': 'Отправлено успешно',
                    'id': pereval.id
                }
                return Response(response_data, status=status.HTTP_200_OK)

            except Exception as e:
                response_data = {
                    'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'message': f'Ошибка при сохранении данных: {str(e)}',
                    'id': None
                }
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            response_data = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': serializer.errors,
                'id': None
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


