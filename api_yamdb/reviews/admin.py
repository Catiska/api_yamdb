from django.contrib import admin

from models import Review, Comment, Category, Genre, Title, GenreTitle


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


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'category', 'description',)
    list_editable = ('category',)
    search_fields = ('name',)
    list_filter = ('year', 'genre', 'category',)
    empty_value_display = '-пусто-'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(GenreTitle)
class GenreTitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'genre', 'title',)
    list_editable = ('genre', 'title',)
    empty_value_display = '-пусто-'

