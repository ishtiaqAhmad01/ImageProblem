from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth import get_user_model, authenticate
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import School, ImageUpload, Notification, DailyReport
from model.main import MyModel
from .serializers import *

User = get_user_model()


# -------------------------------------------- Auth ------------------------------------------------------------

class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        
        if not email or not password:
            return Response({
                "success": False,
                "message": "Email and password are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return Response({
                    "success": True,
                    "message": "Login successful",
                    "data": UserSerializer(user).data
                })
            else:
                return Response({
                    "success": False,
                    "message": "Invalid email or password"
                }, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({
                "success": False,
                "message": "Invalid email or password"
            }, status=status.HTTP_401_UNAUTHORIZED)

class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "success": True,
                "message": "User registered successfully",
                "data": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False, 
            "message": "Registration failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
# -------------------------------------------- School ------------------------------------------------------------

class SchoolListCreateAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        schools = School.objects.all()
        serializer = SchoolSerializer(schools, many=True)
        return Response({
            "success": True,
            "message": "Schools fetched successfully",
            "data": serializer.data
        })
    
    def post(self, request):
        serializer = SchoolSerializer(data=request.data)
        if serializer.is_valid():
            school = serializer.save()
            return Response({
                "success": True,
                "message": "School created successfully",
                "data": SchoolSerializer(school).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class SchoolDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, pk):
        school = get_object_or_404(School, pk=pk)
        return Response({
            "success": True,
            "message": "School fetched successfully",
            "data": SchoolSerializer(school).data
        })
    
    def put(self, request, pk):
        school = get_object_or_404(School, pk=pk)
        serializer = SchoolSerializer(school, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "School updated successfully",
                "data": serializer.data
            })
        return Response({
            "success": False,
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        school = get_object_or_404(School, pk=pk)
        school.delete()
        return Response({
            "success": True,
            "message": "School deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)

# -------------------------------------------- User ------------------------------------------------------------

class UserListAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response({
            "success": True,
            "message": "Users fetched successfully",
            "data": serializer.data
        })

class UserDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        return Response({
            "success": True,
            "message": "User fetched successfully",
            "data": UserSerializer(user).data
        })

# -------------------------------------------- Image Upload ------------------------------------------------------------

class ImageUploadListCreateAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    
    def get(self, request):
        uploads = ImageUpload.objects.all().order_by("-upload_timestamp")
        serializer = ImageUploadSerializer(uploads, many=True)
        return Response({
            "success": True,
            "message": "Images fetched successfully",
            "data": serializer.data
        })
    
    def post(self, request):
        serializer = ImageUploadSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            upload = serializer.save()


            model = MyModel.get_model()   # it's a (static meathod) => no need to create object 
            image_path = upload.image_file.path  

            # Run head count Model
            head_count = model.predict_and_count(image_path)
            print(head_count)
            upload.head_count = head_count
            upload.save()

            return Response({
                "success": True,
                "message": "Image uploaded successfully",
                "data": ImageUploadSerializer(upload).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "Upload failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ImageUploadDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, pk):
        upload = get_object_or_404(ImageUpload, pk=pk)
        return Response({
            "success": True,
            "message": "Image fetched successfully",
            "data": ImageUploadSerializer(upload).data
        })
    
    def delete(self, request, pk):
        upload = get_object_or_404(ImageUpload, pk=pk)
        upload.delete()
        return Response({
            "success": True,
            "message": "Image deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)

class ImageUploadRecentAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        user_id = request.query_params.get("user_id")
        print(user_id)
        if not user_id:
            return Response({
                "success": False,
                "message": "user_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        uploads = ImageUpload.objects.filter(user_id=user_id).order_by("-upload_timestamp")[:10]
        serializer = ImageUploadSerializer(uploads, many=True)
        return Response({
            "success": True,
            "message": "Recent images fetched successfully",
            "data": serializer.data
        })
    
# -------------------------------------------- Notification ------------------------------------------------------------
class NotificationListCreateAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            notifs = Notification.objects.filter(user=user)
        else:
            notifs = Notification.objects.all()
        serializer = NotificationSerializer(notifs, many=True)
        return Response({
            "success": True,
            "message": "Notifications fetched successfully",
            "data": serializer.data
        })
    
    def post(self, request):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            notif = serializer.save()
            return Response({
                "success": True,
                "message": "Notification created successfully",
                "data": NotificationSerializer(notif).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "Creation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class NotificationDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk)
        return Response({
            "success": True,
            "message": "Notification fetched successfully",
            "data": NotificationSerializer(notif).data
        })
    
    def delete(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk)
        notif.delete()
        return Response({
            "success": True,
            "message": "Notification deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)

class NotificationMarkSentAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk)
        notif.status = "sent"
        notif.sent_at = timezone.now()
        notif.save()
        return Response({
            "success": True,
            "message": "Notification marked as sent",
            "data": NotificationSerializer(notif).data
        })

# -------------------- Daily Report --------------------
class DailyReportListCreateAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        reports = DailyReport.objects.all().order_by("-report_date")
        serializer = DailyReportSerializer(reports, many=True)
        return Response({
            "success": True,
            "message": "Reports fetched successfully",
            "data": serializer.data
        })
    
    def post(self, request):
        serializer = DailyReportSerializer(data=request.data)
        if serializer.is_valid():
            report = serializer.save()
            return Response({
                "success": True,
                "message": "Report created successfully",
                "data": DailyReportSerializer(report).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "Creation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class DailyReportDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, pk):
        report = get_object_or_404(DailyReport, pk=pk)
        return Response({
            "success": True,
            "message": "Report fetched successfully",
            "data": DailyReportSerializer(report).data
        })
    
    def delete(self, request, pk):
        report = get_object_or_404(DailyReport, pk=pk)
        report.delete()
        return Response({
            "success": True,
            "message": "Report deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)

class DailyReportSummaryAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        today = timezone.localdate()
        total_uploads = ImageUpload.objects.filter(upload_timestamp__date=today).count()
        total_duplicates = ImageUpload.objects.filter(upload_timestamp__date=today, status="duplicate").count()
        return Response({
            "success": True,
            "message": "Daily summary fetched successfully",
            "data": {
                "date": str(today),
                "total_uploads": total_uploads,
                "total_duplicates": total_duplicates,
            }
        })
