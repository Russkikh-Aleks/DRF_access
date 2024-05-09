from rest_framework.permissions import BasePermission


class IsOwnerAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        return request.user.is_superuser or request.user == obj.creator
       
