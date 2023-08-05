from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Account, PhoneNumber
from .serializers import InboundSMSSerializer, OutboundSMSSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from datetime import datetime, timedelta
import redis


class InboundSMSView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = InboundSMSSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            from_number = data['from_number']
            to_number = data['to_number']
            text = data['text']

            try:
                username = request.auth.get('username', '')
                auth_id = request.auth.get('auth_id', '')
                account = Account.objects.get(username=username, auth_id=auth_id)

                if not account.phone_numbers.filter(number=to_number).exists():
                    return Response({"message": "", "error": "to parameter not found"}, status=status.HTTP_400_BAD_REQUEST)

                def handle_cache(self, from_number, to_number, text):
                    key = f'sms:{from_number}:{to_number}'
                    if 'STOP' in text:
                        redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
                        if redis_client.get(key):
                            return True
                        else:
                            redis_client.setex(key, 4*60*60, 'blocked')
                            return False
                is_blocked = handle_cache(from_number, to_number, text)
                if is_blocked:
                    return Response({"message": "", "error": "sms from {} to {} blocked by STOP request".format(from_number, to_number)}, status=status.HTTP_400_BAD_REQUEST)

                # Save the inbound SMS to the database (implement as needed)

                return Response({"message": "inbound sms ok", "error": ""}, status=status.HTTP_200_OK)

            except ObjectDoesNotExist:
                return Response({"message": "", "error": "Authentication failed"}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OutboundSMSView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = OutboundSMSSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            from_number = data['from_number']
            to_number = data['to_number']
            text = data['text']

            try:
                username = request.auth.get('username', '')
                auth_id = request.auth.get('auth_id', '')
                account = Account.objects.get(username=username, auth_id=auth_id)

                if not account.phone_numbers.filter(number=from_number).exists():
                    return Response({"message": "", "error": "from parameter not found"}, status=status.HTTP_400_BAD_REQUEST)

                limit_key = f'limit:{from_number}'
                redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
                request_count = redis_client.incr(limit_key)

                if request_count == 1:
                    # Set the expiration for the key to 24 hours from now
                    redis_client.expire(limit_key, 24 * 60 * 60)

                if request_count > 50:
                    return Response({"message": "", "error": "limit reached for from {}".format(from_number)}, status=status.HTTP_429_TOO_MANY_REQUESTS)

                return Response({"message": "outbound sms ok", "error": ""}, status=status.HTTP_200_OK)

            except ObjectDoesNotExist:
                return Response({"message": "", "error": "Authentication failed"}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
