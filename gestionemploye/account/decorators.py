from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def role_required(*allowed_roles):
    """
    Décorateur qui vérifie si l'utilisateur est connecté et possède l'un des rôles autorisés (admin, rh, employe).
    - Si l'utilisateur n'est pas connecté, il est redirigé vers la page de connexion.
    - Si l'utilisateur a un rôle non autorisé, il est redirigé vers son propre tableau de bord.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            user_role = getattr(request.user, 'role', None)
            
            # Un superutilisateur Django a toujours tous les accès
            if request.user.is_superuser or user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            messages.error(request, "Accès non autorisé à cette page.")
            if user_role == 'admin':
                return redirect('dashboard_admin')
            elif user_role == 'rh':
                return redirect('dashboard_rh')
            elif user_role == 'employe':
                return redirect('dashboard_employe')
            else:
                return redirect('login')
                
        return _wrapped_view
    return decorator
