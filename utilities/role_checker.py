from functools import wraps
from rest_framework.response import Response
from rest_framework import status

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_role = request.user.role_type
            if user_role not in allowed_roles:
                return Response({'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

