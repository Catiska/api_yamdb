from django.contrib import admin

from models import Review, Comment


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'score', 'text', 'pub_date', 'author', 'title')
    search_fields = ('text', 'title', 'author')
    list_filter = ('pub_date',)
    list_editable = ('title', 'text')
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'review')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('text', 'review')
    empty_value_display = '-пусто-'
