from django.db import models
from django.utils import timezone

class PerevalUser(models.Model):
    email = models.EmailField()
    fam = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    otc = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.fam} {self.name} ({self.email})"

class PerevalCoords(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    height = models.IntegerField()

    def __str__(self):
        return f"Широта: {self.latitude}, Долгота: {self.longitude}, Высота: {self.height}"

class PerevalAdded(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('pending', 'На модерации'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
    ]

    beauty_title = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    other_titles = models.CharField(max_length=255, blank=True)
    connect = models.TextField(blank=True)
    add_time = models.DateTimeField(default=timezone.now)
    level_winter = models.CharField(max_length=3, blank=True)
    level_summer = models.CharField(max_length=3, blank=True)
    level_autumn = models.CharField(max_length=3, blank=True)
    level_spring = models.CharField(max_length=3, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')

    user = models.ForeignKey(PerevalUser, on_delete=models.CASCADE, related_name='perevals')
    coords = models.OneToOneField(PerevalCoords, on_delete=models.CASCADE, related_name='pereval')

    def __str__(self):
        return f"{self.beauty_title} {self.title} ({self.add_time.strftime('%Y-%m-%d')})"

class PerevalImage(models.Model):
    pereval = models.ForeignKey('PerevalAdded', on_delete=models.CASCADE, related_name='images')
    title = models.CharField(max_length=100)
    image_url = models.URLField()

    def __str__(self):
        return f"{self.title} - {self.image_url}"
