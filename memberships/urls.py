from django.urls import path
from .views import UserProfileView, all_members_admin_view

urlpatterns = [
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('all-members/', all_members_admin_view, name='all-members-admin'),
]