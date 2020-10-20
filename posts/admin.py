from django.contrib import admin

from .models import Post, Group, Comment


class PostAdmin(admin.ModelAdmin):
    
    list_display = ("pk", "text", "pub_date", "author") 
    search_fields = ("text",) 
    list_filter = ("pub_date",) 
    empty_value_display = "-пусто-"

admin.site.register(Post, PostAdmin) 


class GroupAdmin(admin.ModelAdmin):
    
    list_display = ('pk', 'title', 'slug', 'description') 
    search_fields = ('title',) 
    list_filter = ('slug',) 
    prepopulated_fields = {'slug': ('title',)}
    
admin.site.register(Group, GroupAdmin) 


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'post', 'author', 'created')  
    search_fields = ('text',) 
    list_filter = ('created',) 
    empty_value_display = '-пусто-'
    
admin.site.register(Comment, CommentAdmin) 
