def normalize_codes(codes):
    """Remove whitespace and lowercase for comparison."""
    return [code.strip().lower() for code in codes]


def has_required_permissions(user, required_codes):
    """Check if user's role has all required permission codes."""
    if not hasattr(user, "role"):
        return False
    if not user.role.is_active:
        return False

    user_codes = [
        p.code.strip().lower() 
        for p in user.role.permissions.filter(is_active=True)
    ]
    return all(code in user_codes for code in normalize_codes(required_codes))