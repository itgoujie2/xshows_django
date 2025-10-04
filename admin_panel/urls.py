from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Admin authentication
    path('login/', views.AdminLoginView.as_view(), name='admin_login'),
    path('logout/', views.AdminLogoutView.as_view(), name='admin_logout'),

    # Admin dashboard
    path('', views.AdminDashboardView.as_view(), name='admin_home'),

    # Config management
    path('configs/<int:pk>/', views.ConfigDetailView.as_view(), name='config_edit'),
    path('configs/<int:pk>/update/', views.ConfigUpdateView.as_view(), name='config_update'),
    path('configs/<int:pk>/update-status/', views.ConfigStatusUpdateView.as_view(), name='config_updates_status'),

    # Category management
    path('categories/', views.CategoryListView.as_view(), name='categories_index'),
    path('categories/data/', views.CategoryDataTablesView.as_view(), name='categories_datatables'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='categories_edit'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='categories_update'),
    path('categories/<int:pk>/update-status/', views.CategoryStatusUpdateView.as_view(), name='categories_updates_status'),

    # User management
    path('users/', views.UserListView.as_view(), name='users_index'),
    path('users/data/', views.UserDataTablesView.as_view(), name='users_datatables'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='users_show'),
    path('users/<int:pk>/update/', views.UserUpdateView.as_view(), name='users_update'),
    path('users/<int:pk>/restore/', views.UserRestoreView.as_view(), name='users_restore'),
    path('users/<int:pk>/change-password/', views.UserChangePasswordView.as_view(), name='users_change_password'),

    # Settings
    path('settings/', views.SettingsView.as_view(), name='settings_edit'),
    path('settings/update/', views.SettingsUpdateView.as_view(), name='settings_update'),
]
