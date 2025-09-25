from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def ajax_register(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        if not (email and username and password):
            return JsonResponse({'success': False, 'message': 'Semua field wajib diisi.'})
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': 'Username sudah terdaftar.'})
        user = User.objects.create_user(username=username, email=email, password=password)
        return JsonResponse({'success': True, 'message': 'Registrasi berhasil.'})
    return JsonResponse({'success': False, 'message': 'Metode tidak diizinkan.'})

@csrf_exempt
def ajax_login(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'message': 'Login berhasil.', 'username': user.username})
        else:
            return JsonResponse({'success': False, 'message': 'Username atau password salah.'})
    return JsonResponse({'success': False, 'message': 'Metode tidak diizinkan.'})

@csrf_exempt
def ajax_logout(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'success': True, 'message': 'Logout berhasil.'})
    return JsonResponse({'success': False, 'message': 'Metode tidak diizinkan.'})
