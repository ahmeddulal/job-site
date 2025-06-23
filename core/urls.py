from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    SignupView,
    CustomAuthToken,
    LogoutView,
    JobListView,
    ApplyJobView,
    MyApplicationsView,
    PostJobView,
    ApplicantsView,
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('jobs/', JobListView.as_view(), name='job-list'),
    path('jobs/<int:job_id>/apply/', ApplyJobView.as_view(), name='apply-job'),
    path('applications/', MyApplicationsView.as_view(), name='my-applications'),
    path('post-job/', PostJobView.as_view(), name='post-job'),
    path('applicants/', ApplicantsView.as_view(), name='applicants'),
]
