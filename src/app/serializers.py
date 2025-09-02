from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import School, ImageUpload, Notification, DailyReport
from django.utils.crypto import get_random_string

User = get_user_model() # As we have cutom user 



# ----------------------------------------------------------------------------
class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = "__all__"


# ----------------------------------------------------------------------------

class UserCreateSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=True, min_length=8)
    school = serializers.PrimaryKeyRelatedField(queryset=School.objects.all(), required=True)

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "password", "role", "school"]

        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        email = validated_data.get("email") or ""
        base_username = email.split("@")[0] if "@" in email else email
        username = base_username or "user"
        
        # ensure uniqueness
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{get_random_string(6)}"

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    

# ----------------------------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):

    school = SchoolSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "full_name", "email", "role", "school"]
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
# ----------------------------------------------------------------------------

class ImageUploadSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user", write_only=True, required=False
    )
    image_file = serializers.ImageField()
    upload_timestamp = serializers.DateTimeField(read_only=True)
    original_filename = serializers.CharField(read_only=True)
    
    class Meta:
        model = ImageUpload
        fields = "__all__"

    
    def create(self, validated_data):
        request = self.context.get("request", None)
        user = validated_data.pop("user", None)
        if user is None and request and request.user and request.user.is_authenticated:
            user = request.user
        
        image_file = validated_data.get("image_file")
        if image_file:
            validated_data["original_filename"] = getattr(image_file, "name", "")
        
        instance = ImageUpload.objects.create(user=user, **validated_data)
        return instance

# ----------------------------------------------------------------------------

class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user", write_only=True, required=False
    )
    image = ImageUploadSerializer(read_only=True)
    image_id = serializers.PrimaryKeyRelatedField(
        queryset=ImageUpload.objects.all(), source="image", write_only=True, required=False, allow_null=True
    )
    
    class Meta:
        model = Notification
        fields = "__all__"

# ----------------------------------------------------------------------------

class DailyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyReport
        fields = "__all__"

# ----------------------------------------------------------------------------
