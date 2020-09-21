from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField('Аddress',
                            unique=True,
                            help_text = 'Для просмотра записей группы '
                            'введите Address после /group/')
    description = models.TextField()

    def __str__(self):
        return str(self.title)


class Post(models.Model):
    class Meta:
        ordering = ("-pub_date",)
        
    text = models.TextField()
    pub_date = models.DateTimeField("date published", 
                                    auto_now_add=True)
    author = models.ForeignKey(User, 
                               on_delete=models.CASCADE, 
                               related_name="posts")
    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL, 
                              related_name="posts",
                              blank=True, null=True)
