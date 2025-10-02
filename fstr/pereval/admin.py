from django.contrib import admin
from .models import PerevalUser, PerevalCoords, PerevalAdded, PerevalImage


@admin.register(PerevalUser)
class PerevalUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'fam', 'name', 'otc', 'phone', 'get_pereval_count')
    search_fields = ('email', 'fam', 'name')
    list_filter = ()
    readonly_fields = ('email',)  # Запретим редактирование email

    def get_pereval_count(self, obj):
        return obj.perevals.count()

    get_pereval_count.short_description = 'Количество перевалов'


@admin.register(PerevalCoords)
class PerevalCoordsAdmin(admin.ModelAdmin):
    list_display = ('latitude', 'longitude', 'height', 'id')
    search_fields = ('latitude', 'longitude', 'height')
    list_filter = ('height',)


@admin.register(PerevalAdded)
class PerevalAddedAdmin(admin.ModelAdmin):
    list_display = ('beauty_title', 'title', 'status', 'user_email', 'add_time')
    list_filter = ('status', 'add_time')
    search_fields = ('title', 'beauty_title', 'user__email')
    readonly_fields = ('add_time',)  # Запретим редактирование времени
    list_editable = ('status',)  # Быстрое редактирование статуса

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Email пользователя'


@admin.register(PerevalImage)
class PerevalImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'pereval_title', 'image_preview', 'image_url')
    list_filter = ('pereval',)
    search_fields = ('title', 'pereval__title')

    def pereval_title(self, obj):
        return obj.pereval.title

    pereval_title.short_description = 'Название перевала'

    def image_preview(self, obj):
        if obj.image_url:
            return f'<a href="{obj.image_url}" target="_blank"><img src="{obj.image_url}" width="50" height="50" style="object-fit: cover;" /></a>'
        return "Нет изображения"

    image_preview.short_description = 'Превью'
    image_preview.allow_tags = True