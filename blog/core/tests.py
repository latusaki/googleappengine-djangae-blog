from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase as DjangoTestCase
from google.appengine.ext import testbed

from blog.core.models import Blog, Post


User = get_user_model()


class TestCase(DjangoTestCase):
    """
    Custom TestCase that allows the usage of Google's user stub
    """
    def _pre_setup(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_user_stub()
        super(TestCase, self)._pre_setup()

    def _post_teardown(self):
        super(TestCase, self)._post_teardown()
        self.testbed.deactivate()

    def users_login(self, email, user_id=None, is_admin=False):
        self.testbed.setup_env(
            USER_EMAIL=email,
            USER_ID=user_id or '98211821748316341',  # Random ID
            USER_IS_ADMIN=str(int(is_admin)),
            AUTH_DOMAIN='testbed',
            overwrite=True,
        )


def create_blog(**kwargs):
    """
    Helper function to create a blog in tests
    """
    default_kwargs = {
        'title': 'blog_title',
        'tagline': 'blog_tagline'
    }
    default_kwargs.update(kwargs)
    return Blog.objects.create(**default_kwargs)


def create_post(**kwargs):
    """
    Helper function to create an post in tests
    """
    default_kwargs = {
        'title': 'post_title',
        'body': 'post_body'
    }
    default_kwargs.update(kwargs)
    return Post.objects.create(**default_kwargs)


class TestBlogModel(TestCase):
    def test_get_unique_no_blogs(self):
        blog = Blog.get_unique()
        self.assertEqual(blog.title, 'My Blog')
        self.assertEqual(blog.tagline, None)
        self.assertEqual(Blog.objects.all().count(), 1)

    def test_get_unique_one_blogs(self):
        create_blog(title='Existing Blog', tagline='123')
        blog = Blog.get_unique()
        self.assertEqual(blog.title, 'Existing Blog')
        self.assertEqual(blog.tagline, '123')
        self.assertEqual(Blog.objects.all().count(), 1)


class TestIndexPage(TestCase):
    url = reverse('index')

    def test_name_and_tagline_in_page(self):
        create_blog()
        resp = self.client.get(self.url)
        self.assertContains(resp, 'blog_title')
        self.assertContains(resp, 'blog_tagline')

    def test_no_posts(self):
        resp = self.client.get(self.url)
        self.assertContains(resp, 'This blog looks empty!')

    def test_posts_title_in_page(self):
        create_post(title='title_post_one', body='body_one')
        create_post(title='title_post_two',  body='body_two')
        resp = self.client.get(self.url)
        self.assertContains(resp, 'title_post_one')
        self.assertContains(resp, 'title_post_two')

    def test_posts_body_in_page(self):
        create_post(title='title_post_one', body='body_one')
        create_post(title='title_post_two',  body='body_two')
        resp = self.client.get(self.url)
        self.assertContains(resp, 'body_one')
        self.assertContains(resp, 'body_two')

    def test_visible_menu_when_admin(self):
        self.users_login('user@localhost', is_admin=True)
        resp = self.client.get(self.url)
        self.assertContains(resp, 'Index')
        self.assertContains(resp, 'Settings')
        self.assertContains(resp, 'Add post')
        self.assertContains(resp, 'Logout')
        self.assertNotContains(resp, 'Login')

    def test_visible_menu_when_not_admin(self):
        self.users_login('user@localhost', is_admin=False)
        resp = self.client.get(self.url)
        self.assertContains(resp, 'Index')
        self.assertContains(resp, 'Logout')
        self.assertNotContains(resp, 'Login')
        self.assertNotContains(resp, 'Settings')
        self.assertNotContains(resp, 'Add post')

    def test_visible_menu_when_not_authenticated(self):
        resp = self.client.get(self.url)
        self.assertContains(resp, 'Index')
        self.assertContains(resp, 'Login')
        self.assertNotContains(resp, 'Settings')
        self.assertNotContains(resp, 'Add post')
        self.assertNotContains(resp, 'Logout')

    def test_tagline_not_displayed_if_its_none(self):
        create_blog(title='Existing Blog', tagline=None)

        resp = self.client.get(self.url)

        self.assertNotContains(resp, 'None')


class TestUpdateBlog(TestCase):
    url = reverse('blog_admin_update')

    def setUp(self):
        create_blog()

    def test_user_not_admin(self):
        self.users_login('user@localhost', is_admin=False)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)

    def test_user_not_authenticated(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)

    def test_post_no_title(self):
        self.users_login('admin@localhost', is_admin=True)
        data = {'tagline': 'new_tagline'}

        self.client.post(self.url, data)

        self.assertEqual(Blog.get_unique().title, 'blog_title')
        self.assertEqual(Blog.get_unique().tagline, 'blog_tagline')

    def test_post_valid(self):
        self.users_login('admin@localhost', is_admin=True)
        data = {'title': 'new_blog_title', 'tagline': 'new_tagline'}

        resp = self.client.post(self.url, data)

        blog = Blog.get_unique()
        self.assertRedirects(resp, reverse('index'))
        self.assertEqual(blog.title, 'new_blog_title')
        self.assertEqual(blog.tagline, 'new_tagline')


class TestUpdatePost(TestCase):
    def setUp(self):
        create_blog()
        self.post = create_post(title='title123', body='body123')
        self.url = reverse(
            'post_admin_update',
            kwargs={'pk': self.post.pk}
        )

    def test_user_not_admin(self):
        self.users_login('user@localhost', is_admin=False)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)

    def test_user_not_authenticated(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)

    def test_form_contains_post_title_and_body(self):
        self.users_login('admin@localhost', is_admin=True)
        resp = self.client.get(self.url)
        self.assertContains(resp, 'title123')
        self.assertContains(resp, 'body123')

    def test_post_no_body(self):
        self.users_login('admin@localhost', is_admin=True)
        data = {'title': 'new_title'}

        self.client.post(self.url, data)

        post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(post.title, 'title123')
        self.assertEqual(post.body, 'body123')

    def test_post_no_title(self):
        self.users_login('admin@localhost', is_admin=True)
        data = {'body': 'new_body'}

        self.client.post(self.url, data)

        post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(post.title, 'title123')
        self.assertEqual(post.body, 'body123')

    def test_post_valid(self):
        self.users_login('admin@localhost', is_admin=True)
        data = {'body': 'new_body', 'title': 'new_title'}

        self.client.post(self.url, data)

        post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(post.title, 'new_title')
        self.assertEqual(post.body, 'new_body')


class TestDeletePost(TestCase):
    def setUp(self):
        create_blog()
        self.post = create_post()

    def test_user_not_admin_get(self):
        self.users_login('user@localhost', is_admin=False)
        url = reverse('post_admin_delete', kwargs={'pk': self.post.pk})

        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Post.objects.all().count(), 1)

    def test_user_not_admin_post(self):
        self.users_login('user@localhost', is_admin=False)
        url = reverse('post_admin_delete', kwargs={'pk': self.post.pk})

        resp = self.client.post(url, data={})

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Post.objects.all().count(), 1)

    def test_user_not_authenticated_get(self):
        url = reverse('post_admin_delete', kwargs={'pk': self.post.pk})

        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Post.objects.all().count(), 1)

    def test_user_not_authenticated_post(self):
        url = reverse('post_admin_delete', kwargs={'pk': self.post.pk})

        resp = self.client.post(url)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Post.objects.all().count(), 1)

    def test_post_does_not_exist_get(self):
        self.users_login('admin@localhost', is_admin=True)
        url = reverse(
            'post_admin_delete', kwargs={'pk': self.post.pk + 1}
        )

        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(Post.objects.all().count(), 1)

    def test_post_does_not_exist_post(self):
        self.users_login('admin@localhost', is_admin=True)
        url = reverse(
            'post_admin_delete', kwargs={'pk': self.post.pk + 1}
        )

        resp = self.client.post(url)

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(Post.objects.all().count(), 1)

    def test_post_exist_get(self):
        self.users_login('admin@localhost', is_admin=True)
        url = reverse('post_admin_delete', kwargs={'pk': self.post.pk})

        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Post.objects.all().count(), 1)

    def test_post_exist_post(self):
        self.users_login('admin@localhost', is_admin=True)
        url = reverse('post_admin_delete', kwargs={'pk': self.post.pk})

        resp = self.client.post(url)

        self.assertRedirects(resp, reverse('index'))
        self.assertEqual(Post.objects.all().count(), 0)
