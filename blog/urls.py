from django.conf import settings
from django.conf.urls import url, include, patterns
from django.contrib import admin
from django.views.generic import TemplateView


from core import views

admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'^_ah/', include('djangae.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^add/$', views.PostAdminCreateView.as_view(), name='post_admin_create'),
    url(r'^manage-blog/$', views.BlogAdminUpdateView.as_view(), name='blog_admin_update'),
    url(r'^delete-post/(?P<pk>[\d]+)/$', views.PostAdminDeleteView.as_view(), name='post_admin_delete'),
    url(r'^update-post/(?P<pk>[\d]+)/$', views.PostAdminUpdateView.as_view(), name='post_admin_update'),
    url(r'^post/(?P<pk>[\d]+)/$', views.PostDetailView.as_view(), name="post-detail"),
)



if not settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^500/$', views.FiveOO.as_view()),
        url(r'^404/$', views.FourOFour.as_view())
    )
