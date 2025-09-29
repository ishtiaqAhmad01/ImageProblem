from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth import get_user_model, authenticate
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import *
from .hasing import get_sha256_from_pil
from .serializers import *
from .sendemail import send_otp_email
import uuid
import random
from datetime import timedelta
from django.utils import timezone
from model.main import MyModel
from PIL import Image

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
        print(request.data)
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
    
    def post(self, request):  # requries a user_id
        serializer = ImageUploadSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            upload = serializer.save()


            
            model = MyModel.get_model()   # it's a (static meathod) => no need to create object 
            image_path = upload.image_file.path
            # Run head count Model
            head_count = model.predict_and_count(image_path)
            upload.head_count = head_count
            upload.image_hash = get_sha256_from_pil(upload.image_file)
            exists = ImageUpload.objects.filter(image_hash=upload.image_hash).exclude(pk=upload.pk).exists()
            upload.duplicate_flag = exists
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
        # print(user_id)
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

# -------------------------------------------- Compare Images -----------------------------------------------------------


class CompareImagesAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        images = request.FILES.getlist('images')

        if len(images) < 2:
            return Response({
                "success": False,
                "message": "At least 2 images are required for comparison"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            image_hashes = {}
            for i, img in enumerate(images):
                image_hashes[f"image_{i+1}"] = get_sha256_from_pil(img)

            # Step 2: Compare all images pairwise
            comparisons = {}
            keys = list(image_hashes.keys())
            for image_name, image_hash in image_hashes.items():
                if image_hash in comparisons:
                    comparisons[image_hash].append(image_name)
                else:
                    comparisons[image_hash] = [image_name]
            
            comparisons_resutls = {}

            for i, a in enumerate(comparisons):
                comparisons_resutls[f"Group {i+1}"] = comparisons[a]


            # Head count 
            model = MyModel.get_model()
            head_counts = {}

            for i, img in enumerate(images):
                pil_image = Image.open(img)
                head_counts[f"{i+1}"] = model.predict_and_count(pil_image)

            return Response({
                "success": True,
                "message": "Images compared successfully",
                "data": {
                    "comparisons": comparisons_resutls,
                    "head_counts" : head_counts
                }
            })

        except Exception as e:
            return Response({
                "success": False,
                "message": f"Image comparison failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -------------------------------------------- Change Password ------------------------------------------------------------

class ChangePasswordAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get("email")
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        
        if not email or not old_password or not new_password:
            return Response({
                "success": False,
                "message": "Email, old password, and new password are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            
            # Check if old password is correct
            if not user.check_password(old_password):
                return Response({
                    "success": False,
                    "message": "Old password is incorrect"
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            return Response({
                "success": True,
                "message": "Password changed successfully"
            })
            
        except User.DoesNotExist:
            return Response({
                "success": False,
                "message": "User with this email does not exist"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Password change failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------------------------Request password reset-------------------------------------

class RequestPasswordResetAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        print(email)
        if not email:
            return Response({
                "success": False,
                "message": "Email is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)

            # generate 6-digit OTP
            otp = str(random.randint(100000, 999999))

            # save OTP
            PasswordResetOTP.objects.create(
                user=user,
                otp=otp,
                expires_at=timezone.now() + timedelta(minutes=5)
            )

            print("Done 1")
            # send OTP
            send_otp_email(user, otp)
            print("Done 2")

            return Response({
                "success": True,
                "message": "OTP sent to your email"
            })

        except:
            return Response({
                "success": False,
                "message": "If this email exists, an OTP has been sent."
            })


# --------------------------------------------Verify OTP ---------------------------------

class VerifyOTPAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response({
                "success": False,
                "message": "Email and OTP are required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            otp_record = PasswordResetOTP.objects.filter(
                user=user, otp=otp, expires_at__gte=timezone.now()
            ).last()

            if not otp_record:
                return Response({
                    "success": False,
                    "message": "Invalid or expired OTP"
                }, status=status.HTTP_400_BAD_REQUEST)

            # create temporary reset token
            reset_token = str(uuid.uuid4())
            otp_record.reset_token = reset_token
            otp_record.save()

            return Response({
                "success": True,
                "message": "OTP verified",
                "reset_token": reset_token
            })

        except User.DoesNotExist:
            return Response({
                "success": False,
                "message": "Invalid request"
            }, status=status.HTTP_400_BAD_REQUEST)

#---------------------------------------------Reset password OTP -------------------------------

class ResetPasswordAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        reset_token = request.data.get("reset_token")
        new_password = request.data.get("new_password")

        if not reset_token or not new_password:
            return Response({
                "success": False,
                "message": "Reset token and new password are required"
            }, status=status.HTTP_400_BAD_REQUEST)

        otp_record = PasswordResetOTP.objects.filter(
            reset_token=reset_token,
            expires_at__gte=timezone.now()
        ).last()

        if not otp_record:
            return Response({
                "success": False,
                "message": "Invalid or expired reset token"
            }, status=status.HTTP_400_BAD_REQUEST)

        user = otp_record.user
        user.set_password(new_password)
        user.save()

        # invalidate token
        otp_record.delete()

        return Response({
            "success": True,
            "message": "Password reset successful"
        })
