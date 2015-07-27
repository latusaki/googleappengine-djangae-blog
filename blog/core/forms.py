from django import forms

from blog.core.models import Post, Blog

from google.appengine.api import users

class PostForm(forms.ModelForm):
    if users.get_current_user() is not None:
        user_id = users.get_current_user().user_id()
        user_email = users.get_current_user().email()
        author_id = forms.IntegerField(widget=forms.HiddenInput(), initial=user_id)
        author_email = forms.CharField(widget=forms.HiddenInput(), initial=user_email)

    class Meta:
        model = Post
        fields = ('title', 'body','author_id','author_email')
        labels = {
            'body': ('Content')
        }


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ('title', 'tagline','paginate_by')
        labels = {
            'paginate_by': ('Post per page')
        }
