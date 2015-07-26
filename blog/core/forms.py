from django import forms

from blog.core.models import Article, Blog


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'body')
        labels = {
            'body': ('Content')
        }
        help_texts = {
            'body': ('Write your thoughts...')
        }


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ('title', 'tagline','paginate_by')
        labels = {
            'paginate_by': ('Post per page')
        }
