"""requisition URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from user import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('register/', views.registerpage, name='registerpage'),
    path('login/', views.loginpage, name='loginpage'),
    path('logout/', views.logoutuser, name='logoutuser'),
    path('profile/', views.profile, name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),






    path('all_requisitions/', views.userpage, name='userpage'),
    path('', views.userpage0, name='userpage0'),
    # path('dashboard_detail/', views.userpage1, name='dashboard_detail'),




    path('admin/', admin.site.urls),


    # path('', views.home, name='home'),
    path('requisitions/<str:pk>', views.requisitions, name='requisitions'),
    # path('user/<str:pk>/', views.employee, name='employee'),
    path('create_requisition/<str:pk>', views.create_requisition, name='create_requisition'),
    path('delete_requisition/<str:pk>', views.delete_requisition, name='delete_requisition'),
    path('update_requisition/<str:pk>', views.update_requisition, name='update_requisition'),
    path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/', views.activate, name='activate'),  
    
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)