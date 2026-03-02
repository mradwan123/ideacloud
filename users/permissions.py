from rest_framework.permissions import BasePermission

class IsAdminOrUser(BasePermission):
    
    def has_user_permission(self, request, user=None):
        """
        Allow delete user account for admin OR user owner
        """
        #allows admins(staff+superuser) to do all actions
        if request.user and request.user.is_staff:
            return True
        
        # allow user account owner to delete their own account
        if request.method == 'DELETE':
            return user == request.user
        
        # allow user to retrieve user info
        if request.method == 'GET':
            return user == request.user
        
        # for other methods, use other permissions
        return False
        
class CanUpdateUser(BasePermission):
    """
    Docstring for CanUpdateUser: Custom permission for user details. 
    has_object_ermission & check_object_permission() used in views for more custom designs.
    """
    def has_object_permission(self, request, view, object):
        if request.method in ['GET', 'PUT', 'PATCH', 'DELETE']:  
            # owner can update
            return request.user == object
        return False
            