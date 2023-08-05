from rest_framework import serializers
from .models import Account,PhoneNumber
from django.contrib.auth import get_user_model

class AccountCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model=get_user_model
        fields=['username']
        extra_kwargs={
            'password': {'read_only': True}
        }
    
class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model=Account
        fields='__all__'
        
        
class InboundSMSSerializer(serializers.Serializer):
    from_number = serializers.CharField(min_length=6, max_length=16)
    to_number = serializers.CharField(min_length=6, max_length=16)
    text = serializers.CharField(max_length=120)

class OutboundSMSSerializer(serializers.Serializer):
    from_number = serializers.CharField(min_length=6, max_length=16)
    to_number = serializers.CharField(min_length=6, max_length=16)
    text = serializers.CharField(max_length=120)