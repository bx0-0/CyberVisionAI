from datetime import timedelta
import os
import re
import subprocess
from bs4 import BeautifulSoup
from django.utils import timezone
import hmac
import time
import uuid
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from  accounts.models import Profile
from django.http import  Http404, HttpResponse, JsonResponse
from .models import Token, Conversation , Message, MindMap
from django.views.decorators.csrf import csrf_exempt
import json
import hashlib
from django.conf import settings
from django.core.paginator import Paginator
from django.db import transaction
from django.http import StreamingHttpResponse

# Create your views here.

def create_signature(secret_key, token, timestamp):
    data = f"{token}{timestamp}".encode('utf-8')
    return hmac.new(secret_key.encode(), data, hashlib.sha256).hexdigest()

@login_required
def streamlit_view(request):
    token = str(uuid.uuid4())
    expiration = timezone.now() + timedelta(minutes=1)
    Token.objects.create(token=token, expiration=expiration,user=request.user)

    return render(request, 'streamlit_page.html', {'token': token})

@csrf_exempt
def send_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        token = data.get('token')
        timestamp = data.get('timestamp')
        received_signature = data.get('signature')
        expected_signature = create_signature(settings.SECRET_KEY, token, str(int(timestamp)))
        print(repr(expected_signature))
        print(repr(received_signature))
        current_time = int(time.time())

        if hmac.compare_digest(expected_signature, received_signature):
            token = get_object_or_404(Token, token=token)
            user = token.user
            print(user.username)
            expiration = int(token.expiration.timestamp())

            if current_time > expiration:
                return JsonResponse({'success': False, 'error': 'Token expired'}, status=401)
            api = Profile.objects.get(user=user).api_key
            token.delete()
            print(api)
            return JsonResponse({'success': True,'api':api,'name':user.username})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid signature'}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@csrf_exempt
@transaction.atomic
def save_chat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        api_key = data.get('api_key')
        conversation_data = data.get('conversation')
        timestamp = data.get('timestamp')
        signature = data.get('signature')
        created_at = data.get('time')

        expected_signature = create_signature(settings.SECRET_KEY, api_key, str(int(timestamp)))

        if not hmac.compare_digest(expected_signature, signature):
            return JsonResponse({'success': False, 'error': 'Invalid signature'}, status=401)

        user = get_object_or_404(Profile, api_key=api_key).user
        
        conversation = Conversation.objects.create(user=user, created_at=str(created_at))
        for message in conversation_data:
            Message.objects.create(
                conversation=conversation,
                role = message.get('role'),
                content = message.get('content')
            )
        return JsonResponse({'success': True, 'message': 'Chat saved successfully!', 'slug': conversation.slug}, status=200)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)        

@login_required
def get_conversation(request,slug):
    conversation = get_object_or_404(Conversation,user = request.user,slug=slug)
    messages = Message.objects.filter(conversation=conversation)
    return render(request, 'conversation.html', {'messages': messages,'slug':slug})

@login_required
def list_conversations(request):
    conversations = Conversation.objects.filter(user = request.user).order_by('-created_at_in_DB')
    pagination = Paginator(conversations,4)
    page = request.GET.get('page')
    conversations = pagination.get_page(page)
    return render(request, 'list_conversations.html', {'conversations': conversations})

@transaction.atomic
@login_required
def delete_conversation(request,slug):
    conversation = get_object_or_404(Conversation,user = request.user,slug=slug)
    conversation.delete()
    return redirect('chat:list_conversations')

@csrf_exempt
@transaction.atomic
def create_mind_map(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        api_key = data.get('api_key')
        timestamp = data.get('timestamp')
        signature = data.get('signature')
        text = data.get('text')

        expected_signature = create_signature(settings.SECRET_KEY, api_key, str(int(timestamp)))
        if not hmac.compare_digest(expected_signature, signature):
            return JsonResponse({'success': False, 'error': 'Invalid signature'}, status=401)

        user = get_object_or_404(Profile, api_key=api_key).user

        if text:
            mind_map = MindMap.objects.create(user=user)
            mind_map_name = mind_map.slug

            user_folder = os.path.join('Mindmaps', f'user_{user.id}')
            md_filename = f"{mind_map_name}.md"
            md_path = os.path.join(settings.MEDIA_ROOT, user_folder, md_filename)
            html_filename = f"{mind_map_name}.html"
            html_path = os.path.join(settings.MEDIA_ROOT, user_folder, html_filename)

            os.makedirs(os.path.join(settings.MEDIA_ROOT, user_folder), exist_ok=True)

            with open(md_path, 'w', encoding='utf-8') as md_file:
                md_file.write(text)

            command = f'markmap "{md_path}" -o "{html_path}" --no-open '

            try:
                subprocess.run(['powershell.exe', '-Command', command], check=True)
            except subprocess.CalledProcessError:
                return JsonResponse({'success': False, 'error': 'Error creating mind map HTML'}, status=500)

            if os.path.exists(md_path):
                os.remove(md_path)

            # Process the HTML to clean it
            if os.path.exists(html_path):
                with open(html_path, 'r', encoding='utf-8') as html_file:
                    soup = BeautifulSoup(html_file, 'html.parser')

                # Remove all <link> tags
                for tag in soup.find_all('link'):
                    tag.decompose()

                # Remove <script> tags with src attribute
                for script in soup.find_all('script'):
                    if script.has_attr('src'):
                        script.decompose()

                # Save the cleaned HTML back
                with open(html_path, 'w', encoding='utf-8') as cleaned_html_file:
                    cleaned_html_file.write(str(soup))

            mind_map.file_path = os.path.join(user_folder, html_filename)
            mind_map.save()
            urls = "http://127.0.0.1:8000/chat/show_mind_map/" + mind_map.slug

            return JsonResponse({'success': True, 'file_url': urls}, status=201)
        else:
            return JsonResponse({'success': False, 'error': 'Text content is required'}, status=400)

    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


@login_required
def mind_map_view(request, slug):
    """
    عرض محتوى mind map بناءً على الـ slug والمستخدم الحالي.
    """
    # البحث عن MindMap بناءً على slug والمستخدم الحالي
    try:
        mind_map = MindMap.objects.get(slug=slug, user=request.user)
    except MindMap.DoesNotExist:
        raise Http404("Mind Map not found")

    # مسار ملف HTML بناءً على user_id و slug
    html_file_path = os.path.join(
        settings.MEDIA_ROOT, 
        f"Mindmaps/user_{request.user.id}/{slug}.html"
    )

    # التحقق من وجود الملف
    if not os.path.exists(html_file_path):
        raise Http404("Mind Map file not found")

    # قراءة محتوى HTML
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            mind_map_content = file.read()
    except Exception as e:
        return HttpResponse(f"Error reading the file: {str(e)}", status=500)

    return render(request, 'mind_map_view.html', {'mind_map_content': mind_map_content})

def search_LLm(request):
    if request.method == 'GET':
        try:
            query = request.GET.get('query', '')  
            if not query:
                return JsonResponse({'error': 'Please provide a query.'}, status=400)

            def event_stream():
                test_text = "Hello, World! This is a test text."
                for i in range(10):
                    time.sleep(1)  # Simulate delay
                    yield f"data: {json.dumps({'message': test_text + f' - {i + 1}'})}\n\n"  # SSE format

            response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
            response['Cache-Control'] = 'no-cache'
            return response
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def search_page(request):
    return render(request, 'search_pro.html')