from django.contrib import admin
from .models import Post, Comment, Objective

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']

class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')

class ObjectiveAdmin(admin.ModelAdmin):
    list_display = ('description', 'priority', 'time_completed', 'time_estimated', 'completed')
    list_filder = ('priority', 'time_estimated' ,'completed')
    search_fields = ('description', 'body')
    prepopulated_fields = {'slug': ('description',)}


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Objective, ObjectiveAdmin)
