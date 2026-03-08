from django import template

register = template.Library()


@register.filter(name='role_has_perm_in')
def role_has_perm_in(user, perms):
    """
    Check if the user's role contains ANY of the provided permissions.
    `perms` may be:
     • a list: ["write_assets", "read_branches"]
     • a string: "write_assets,read_branches"
     • a string: "write_assets"
    """

    # no role = no permissions
    if user.is_admin or user.is_superuser:
        return True
    
    if not hasattr(user, 'role') or user.role is None:
        return False

    # Normalize the perms input to a Python list of codes
    if isinstance(perms, str):
        perms = [p.strip() for p in perms.split(',') if p.strip()]
    elif not isinstance(perms, (list, tuple, set)):
        perms = [perms]

    return user.role.permissions.filter(code__in=perms).exists()