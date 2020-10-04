from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from PIL import Image

from ckeditor_uploader.fields import RichTextUploadingField

class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, null=False)
    content = RichTextUploadingField()
    description = models.TextField(max_length=500, default='')
    image = models.ImageField(upload_to='post_pics')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)
    # main_post = models.ForeignKey(HeroPost,)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk, 'slug': self.slug})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 1280 or img.width > 1280:
            output_size = (1280, 720)
            img.thumbnail(output_size)
            img.save(self.image.path)


class HeroPost(models.Model):
    main_post = models.OneToOneField(Post, unique=True, on_delete=models.CASCADE)
    title_color = models.CharField(max_length=7, default='#fff')
    overlay_opacity = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(0.9)], default=0.3)

    def __unicode__(self):
        return self.main_post.slug


# def validate_only_one_instance(obj):
#     model = obj.__class__
#     if (model.objects.count() > 0 and
#             obj.id != model.objects.get().id):
#         raise ValidationError("Can only create 1 %s instance, please delete the previous one first" % model.__name__)
#



    # def clean(self):
    #     validate_only_one_instance(self)
    # def save(self, *args, **kwargs):
    #     if HeroPost.objects.filter(main_post=self.main_post).count() < 1:
    #         return super(HeroPost, self).save(*args, **kwargs)
    #     raise ValidationError("HeroPost only can be one. Please delete previous first.")


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    body = models.TextField(max_length=1500)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('-created',)
        indexes = [
            models.Index(fields=['created']),
            models.Index(fields=['-created'])]

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk, 'slug': self.slug})
