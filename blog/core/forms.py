from django import forms

from blog.core.models import Post, Blog

from google.appengine.api import users

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'body',)
        labels = {
            'body': ('Content')
        }
   
    def save(self, force_insert=False, force_update=False, commit=True):
        obj = super(PostForm, self).save(commit=False)
        if users.get_current_user() is not None:
            user_id = users.get_current_user().user_id()
            user_email = users.get_current_user().email()    
            obj.author_id = user_id
            obj.author_email = user_email
        if commit:
            obj.save()
        
        return obj



class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ('title', 'tagline','paginate_by')
        labels = {
            'paginate_by': ('Posts per page')
        }
