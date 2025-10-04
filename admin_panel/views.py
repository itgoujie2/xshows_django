"""
Admin panel views for managing the xshows application.
Converted from Laravel Admin controllers.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.urls import reverse_lazy

from users.models import User
from core.models import Config, Setting
from categories.models import Category
from models_app.models import WebcamModel


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to require admin role for views"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == User.ROLE_ADMIN


class AdminLoginView(LoginView):
    """Admin login view"""
    template_name = 'admin_panel/login.html'
    success_url = reverse_lazy('admin_panel:admin_home')


class AdminLogoutView(LogoutView):
    """Admin logout view"""
    next_page = reverse_lazy('admin_panel:admin_login')


class AdminDashboardView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Admin dashboard home"""
    def get(self, request):
        context = {
            'users_count': User.objects.filter(role=User.ROLE_MEMBER).count(),
            'models_count': WebcamModel.objects.count(),
            'online_models_count': WebcamModel.objects.filter(is_online=True).count(),
            'categories_count': Category.objects.count(),
        }
        return render(request, 'admin_panel/dashboard.html', context)


# Config Views
class ConfigDetailView(AdminRequiredMixin, DetailView):
    """View config detail"""
    model = Config
    template_name = 'admin_panel/config/detail.html'


class ConfigUpdateView(AdminRequiredMixin, UpdateView):
    """Update config"""
    model = Config
    fields = ['method', 'api_url', 'data', 'is_active']
    template_name = 'admin_panel/config/edit.html'
    success_url = reverse_lazy('admin_panel:admin_home')


class ConfigStatusUpdateView(AdminRequiredMixin, View):
    """Toggle config active status"""
    def patch(self, request, pk):
        config = get_object_or_404(Config, pk=pk)
        config.is_active = not config.is_active
        config.save()
        return JsonResponse({'success': True, 'is_active': config.is_active})


# Category Views
class CategoryListView(AdminRequiredMixin, ListView):
    """List categories"""
    model = Category
    template_name = 'admin_panel/category/index.html'
    context_object_name = 'categories'


class CategoryDataTablesView(AdminRequiredMixin, View):
    """DataTables AJAX endpoint for categories"""
    def get(self, request):
        # Implement DataTables server-side processing
        # This would be similar to Laravel's DataTables implementation
        categories = Category.objects.all()
        data = [
            {
                'id': cat.id,
                'name': cat.name,
                'display_name': cat.display_name,
                'is_active': cat.is_active,
            }
            for cat in categories
        ]
        return JsonResponse({'data': data})


class CategoryDetailView(AdminRequiredMixin, DetailView):
    """View category detail"""
    model = Category
    template_name = 'admin_panel/category/detail.html'


class CategoryUpdateView(AdminRequiredMixin, UpdateView):
    """Update category"""
    model = Category
    fields = ['name', 'display_name', 'is_active', 'description', 'keywords', 'title']
    template_name = 'admin_panel/category/edit.html'
    success_url = reverse_lazy('admin_panel:categories_index')


class CategoryStatusUpdateView(AdminRequiredMixin, View):
    """Toggle category active status"""
    def patch(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.is_active = not category.is_active
        category.save()
        return JsonResponse({'success': True, 'is_active': category.is_active})


# User Management Views
class UserListView(AdminRequiredMixin, ListView):
    """List users"""
    model = User
    template_name = 'admin_panel/user/index.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.filter(role=User.ROLE_MEMBER)


class UserDataTablesView(AdminRequiredMixin, View):
    """DataTables AJAX endpoint for users"""
    def get(self, request):
        users = User.objects.filter(role=User.ROLE_MEMBER)
        data = [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat(),
            }
            for user in users
        ]
        return JsonResponse({'data': data})


class UserDetailView(AdminRequiredMixin, DetailView):
    """View user detail"""
    model = User
    template_name = 'admin_panel/user/detail.html'


class UserUpdateView(AdminRequiredMixin, UpdateView):
    """Update user"""
    model = User
    fields = ['username', 'email', 'is_active']
    template_name = 'admin_panel/user/edit.html'
    success_url = reverse_lazy('admin_panel:users_index')


class UserRestoreView(AdminRequiredMixin, View):
    """Restore soft-deleted user"""
    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.deleted_at = None
        user.save()
        return JsonResponse({'success': True, 'message': 'User restored'})


class UserChangePasswordView(AdminRequiredMixin, View):
    """Change user password"""
    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)
            user.save()
            return JsonResponse({'success': True, 'message': 'Password changed'})
        return JsonResponse({'success': False, 'message': 'No password provided'})


# Settings Views
class SettingsView(AdminRequiredMixin, ListView):
    """View settings"""
    model = Setting
    template_name = 'admin_panel/settings/index.html'
    context_object_name = 'settings'


class SettingsUpdateView(AdminRequiredMixin, View):
    """Update settings"""
    def post(self, request):
        # Process settings update
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken':
                Setting.objects.update_or_create(
                    key=key,
                    defaults={'value': value}
                )
        return redirect('admin_panel:settings_edit')
