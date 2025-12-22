from rest_framework. views import APIView
from rest_framework.response import Response
from rest_framework import status

from . serializers import RegisterSerializer, LoginSerializer


class RegisterView(APIView):
    def post(self, request):
        print("=== REGISTER ISTEĞI GELDİ ===")
        print("Gelen data:", request.data)
        print("Gelen headers:", request.headers)

        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            print("VALIDATED DATA:", serializer.validated_data)
            user = serializer.save()
            print("Kullanıcı oluşturuldu:", user.email)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        print("SERIALIZER HATALARI:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        print("=== LOGIN ISTEĞI GELDİ ===")
        print("Gelen data:", request.data)  # ← EKLE
        print("Gelen headers:", request.headers)  # ← EKLE

        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            print("Başarılı, token dönüyor:", serializer.validated_data)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        
        print("Hata:", serializer.errors)  # ← EKLE
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

