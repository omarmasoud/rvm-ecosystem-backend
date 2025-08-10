"""
URL configuration for rvm_ecosystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from core.web_views import home, user_signup, signup_success_view # Import from new web_views

urlpatterns = [
    path('', home, name='home'),
    path('signup/', user_signup, name='signup'), # New template signup path
    path('success/', signup_success_view, name='signup_success'), # New template signup success path
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('docs/', include_docs_urls(title='RVM Ecosystem API')),
]
