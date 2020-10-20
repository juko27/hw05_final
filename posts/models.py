from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import validate_image_file_extension

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(verbose_name='web-адрес',
                            unique=True,
                            help_text = 'Для просмотра записей группы '
                            'введите Address после /group/')
    description = models.TextField()

    def __str__(self):
        return str(self.title)


class Post(models.Model):
    class Meta:
        ordering = ('-pub_date',)
        
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(verbose_name='Дата публикации',
                                    auto_now_add=True)
    author = models.ForeignKey(User, 
                               verbose_name='Автор',
                               on_delete=models.CASCADE, 
                               related_name='posts')
    group = models.ForeignKey(Group,
                              verbose_name='Группа',
                              on_delete=models.SET_NULL, 
                              related_name='posts',
                              blank=True, null=True)
    image = models.ImageField(verbose_name='Изображение',
                              upload_to='posts/', 
                              blank=True, 
                              null=True)  


class Comment(models.Model):
    post =  models.ForeignKey(Post,
                              verbose_name='Публикация',
                              on_delete=models.CASCADE,
                              related_name='comments',
                              blank=True, null=True)
    author = models.ForeignKey(User, 
                               verbose_name='Автор',
                               on_delete=models.CASCADE, 
                               related_name='comments')
    text = models.TextField()
    created = models.DateTimeField(verbose_name='Опубликовано в',
                                   auto_now_add=True)

                                
class Follow(models.Model):
    class Meta:
        unique_together = ('user', 'author',)

    user =  models.ForeignKey(User, 
                               verbose_name='Подписан',
                               on_delete=models.CASCADE, 
                               related_name='follower')
    author = models.ForeignKey(User, 
                               verbose_name='Подписчиков',
                               on_delete=models.CASCADE, 
                               related_name='following')
    