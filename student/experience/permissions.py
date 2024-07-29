from rest_framework import permissions

class Isowner(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        else:
            return False
    
    def has_object_permission(self, request, view, obj):
        if obj.user:
            return request.user == obj.user
        return False

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 1:
            return True
        else:
            return False

class IsPartner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 2:
            return True
        else:
            return False

class IsSupervisor(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 3:
            return True
        else:
            return False

class IsApproved(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.status == 1:
            return True
        else:
            return False

class IsPartnerOrSupervisor(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 3 or request.user.user_type == 2:
            return True
        else:
            return False

class IsStudentOrSupervisor(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 3 or request.user.user_type == 1:
            return True
        else:
            return False