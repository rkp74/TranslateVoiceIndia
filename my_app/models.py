from django.db import models

# Create your models here.
class Video(models.Model):
    # title=models.CharField(max_length=100)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    video_url = models.URLField(blank=True)

    # def __str__(self):
    #     return self.title

