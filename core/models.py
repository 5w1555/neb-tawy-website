from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Booking(models.Model):
    SERVICE_CHOICES = [
        ('focused_reading',    'Focused Reading'),
        ('indepth_guidance',   'In-Depth Guidance'),
        ('signature_guidance', 'Signature Guidance'),
        ('zoom_session',       'Zoom Session'),
    ]

    service = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    date = models.DateField()
    time_slot = models.CharField(max_length=5, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)  
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField(blank=True)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} — {self.date} ({self.service})"