from django.core.exceptions import PermissionDenied
from functools import wraps
from django.shortcuts import redirect,render
from django.contrib.auth.models import Permission



def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper


def staff_or_admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper


def get_role_permissions(user):
    user_profile = getattr(user, 'userprofile', None)
    role = user_profile.role if user_profile else None
    permissions = role.permissions.all() if role else Permission.objects.none()
    permissions_list = list(permissions.values_list('name', flat=True))
    return role, permissions, permissions_list




REDIRECT_MAP = {
    'category': 'category_list',
    'product': 'product_list',
    'role': 'role_list',
    'user': 'user_list',
}

def role_permission_required(permission_name, module=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            user_profile = getattr(request.user, 'userprofile', None)
            role = user_profile.role if user_profile else None
            if not role:
                return render(request, '403.html', status=403)
            permissions = list(role.permissions.values_list('name', flat=True))
            if permission_name in permissions:
                return view_func(request, *args, **kwargs)
            return render(request, '403.html', status=403)
        return _wrapped_view
    return decorator