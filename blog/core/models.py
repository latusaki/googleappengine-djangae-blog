from django.db import models
from django.core.validators import MinValueValidator

class Blog(models.Model):
    title = models.CharField(max_length=255, default='My Blog')
    tagline = models.CharField(max_length=255, null=True, blank=True)
    paginate_by = models.IntegerField(validators=[MinValueValidator(0)],default=10)
    @staticmethod
    def get_unique():
        """
        Returns the only instance of the Blog in the data store.
        If there are no Blog it creates a default one.
        """
        blog, __ = Blog.objects.get_or_create()
        return blog


class Post(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author_id =  models.CharField(max_length=255)
    author_email = models.CharField(max_length=255)

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('post-detail', args=[str(self.id)])

class Comment(models.Model):
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author_name = models.CharField(max_length=255)
    parent_post = models.ForeignKey('Post',related_name='comments')
    class Meta:
        ordering = ["-created_at"]
