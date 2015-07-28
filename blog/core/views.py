from django.views.generic import (
    ListView, View, DeleteView, UpdateView, CreateView, TemplateView, DetailView
)
from django.shortcuts import redirect

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from google.appengine.api import users

from blog.core.models import Post, Blog, Comment
from blog.core.forms import PostForm, BlogForm


class BlogMixin(object):
    """
    Basic mixin for all the views. Update the context with additional
    information that is required across the whole site, typically
    to render base.html properly
    """
    def get_context_data(self, *args, **kwargs):
        context = super(BlogMixin, self).get_context_data(*args, **kwargs)
        blog = Blog.get_unique()
        context.update({
            'blog': blog,
            'active_user': users.get_current_user(),
            'is_admin': users.is_current_user_admin()
        })
        return context


class AdminRequiredMixin(object):
    """
    Mixin that redirects to the login page if users are not
    authenticated or they are not administrators
    """
    def get_after_login_url(self):
        return reverse('index')

    def dispatch(self, request, *args, **kwargs):
        if not users.is_current_user_admin():
            url = users.create_login_url(self.get_after_login_url())
            return HttpResponseRedirect(url)
        return super(AdminRequiredMixin, self).dispatch(
            request, *args, **kwargs)

class UserRequiredMixin(object):
    """
    Mixin that redirects to the login page if users are not
    authenticated or they are not administrators
    """
    def get_after_login_url(self):
        return reverse('index')

    def dispatch(self, request, *args, **kwargs):
        if users.get_current_user() is None:
            url = users.create_login_url(self.get_after_login_url())
            return HttpResponseRedirect(url)
        return super(UserRequiredMixin, self).dispatch(
            request, *args, **kwargs)

class FourOFour(BlogMixin, TemplateView):
    template_name = '404.html'


class FiveOO(BlogMixin, TemplateView):
    template_name = '500.html'


class LoginView(View):
    """
    A simple login page that uses Google App Engine authentication
    """
    def get(self, request):
        index = reverse('index')
        url = users.create_login_url(index)
        return HttpResponseRedirect(url)


class LogoutView(View):
    """
    A simple logout page that uses Google App Engine authentication
    """
    def get(self, request):
        index = reverse('index')
        url = users.create_logout_url(index)
        return HttpResponseRedirect(url)


class IndexView(BlogMixin, ListView):
    """
    The index page of the site. Contains the body and the titles of
    all the posts.
    """
    template_name = 'index.html'
    context_object_name = "post_list" 
    queryset = Post.objects.all().order_by('-created_at')
    paginate_by = Blog.get_unique().paginate_by
    print paginate_by


class PostAdminCreateView(UserRequiredMixin, BlogMixin, CreateView):
    """
    Administration page to create posts.
    """
    template_name = 'form.html'
    form_class = PostForm

    def get_success_url(self):
        return reverse('index')


class BlogAdminUpdateView(AdminRequiredMixin, BlogMixin, UpdateView):
    """
    Administration page to update blog settings.
    """
    template_name = 'form.html'
    form_class = BlogForm

    def get_success_url(self):
        return reverse('index')

    def get_object(self):
        return Blog.get_unique()

class PostDetailView(BlogMixin,CreateView):
    """ A view for displaying a single post """
    template_name = 'post.html'
    model = Comment
    fields = ['body','author_name'] 
    def get_context_data(self, **kwargs):

        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['post'] =  Post.objects.get(pk=self.kwargs['pk'])
        return context
    
    def form_valid(self, form):
        # self.object = form.save()
        obj = form.save(commit=False)
        obj.parent_post = Post.objects.get(pk=self.kwargs['pk'])
        obj.save()

        return redirect('post-detail', self.kwargs['pk'])


class PostAdminDeleteView(AdminRequiredMixin, BlogMixin, DeleteView):
    """
    Delete the post with a given key
    """
    model = Post
    template_name = 'post_confirm_delete.html'

    def get_success_url(self):
        return reverse('index')


class PostAdminUpdateView(AdminRequiredMixin, BlogMixin, UpdateView):
    """
    Administration page to update posts.
    """
    template_name = 'form.html'
    form_class = PostForm
    model = Post

    def get_success_url(self):
        return reverse('index')
