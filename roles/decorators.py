from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from roles.helpers import has_required_permissions

# ===== Decorator for Function-Based Views =====
def required_permission(*codes):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not has_required_permissions(request.user, codes):
                messages.warning(request, "You do not have access to this page.")
                return redirect(request.META.get("HTTP_REFERER", "/"))
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator



# @required_permission("read_system_user", "read_asset_category")
# def my_view(request):
#     return render(request, "example.html")