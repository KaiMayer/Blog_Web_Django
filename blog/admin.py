from django import forms
from django.contrib import admin
from .models import Post, Comment, HeroPost
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Post
        fields = '__all__'


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'description', 'author', 'date_posted', 'image')
    #     list_filter = ('status', 'created', 'date_posted', 'author')
    #     search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',), 'description': ('content',)}
    #     raw_id_fields = ('author',)
    #     date_hierarchy = 'date_posted'
    #     ordering = ('status', 'date_posted')
    form = PostAdminForm


@admin.register(HeroPost)
class HeroPostAdmin(admin.ModelAdmin):
    list_display = ('main_post',)

    def has_add_permission(self, request):
        num_objects = self.model.objects.count()
        if num_objects >= 1:
            return False
        else:
            return True


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'body', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated', 'post')
    search_fields = ('author__username', 'body')


admin.site.register(Post, PostAdmin)
