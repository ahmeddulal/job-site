from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import Job, Application, Profile
from .serializers import SignupSerializer, JobSerializer, ApplicationSerializer
from rest_framework.exceptions import PermissionDenied

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({'token': token.key, 'user_id': token.user_id})

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Logged out"})

class JobListView(generics.ListAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

class ApplyJobView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, job_id):
        user = request.user
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=404)

        if user.profile.user_type != 'candidate':
            return Response({'error': 'Only candidates can apply'}, status=403)

        if Application.objects.filter(candidate=user, job=job).exists():
            return Response({'error': 'Already applied to this job'}, status=400)

        Application.objects.create(candidate=user, job=job)

        send_mail(
            subject='Job Application Submitted',
            message=f'{user.username} applied to {job.title}.',
            from_email='noreply@jobsite.com',
            recipient_list=[user.email, job.recruiter.email],
            fail_silently=True,
        )

        return Response({'message': 'Applied successfully'})

class MyApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.profile.user_type != 'recruiter':
            return Application.objects.filter(candidate=self.request.user)

class PostJobView(generics.CreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.profile.user_type != 'recruiter':
            raise PermissionDenied("Only recruiters can post jobs")
        serializer.save(recruiter=self.request.user)

class ApplicantsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.profile.user_type != 'recruiter':
            return Response({'error': 'Only recruiters can view applicants'}, status=403)

        jobs = Job.objects.filter(recruiter=request.user)
        applications = Application.objects.filter(job__in=jobs).select_related('candidate', 'job')

        data = [
            {
                'job_title': app.job.title,
                'candidate_username': app.candidate.username,
                'candidate_email': app.candidate.email,
                'applied_at': app.applied_at,
            }
            for app in applications
        ]

        return Response(data)
    

