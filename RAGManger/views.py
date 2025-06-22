import json
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from numpy import number
from accounts.models import Profile
from .forms import UploadFileForm
import tempfile
from .tasks import process_pdf
from django.contrib import messages
import redis
from django.http import StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from .models import UserNotification
from django.http import JsonResponse
from .lancedb_utils import search_in_RAG_db


# Create your views here.

def upload_RAG_content(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            if file is not None:
                # Save the file to a temporary location
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    for chunk in file.chunks():
                        temp_file.write(chunk)
                    temp_file.flush()

                # Process the file using Celery
                process_pdf.delay(file_name=file.name, file_path=temp_file.name, user_id=request.user.id)

                messages.success(request, 'File uploaded and processing started we will notify you once it is completed.')
            else:
                messages.error(request, 'Please select a file to upload.')                
    else:
        form = UploadFileForm()
    return render(request, 'upload_RAG_content.html', {'form': form})




@login_required
def sse_notifications(request):
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
    def event_stream(user_id):
        pubsub = redis_client.pubsub()
        pubsub.subscribe(f"user_{user_id}")
        for message in pubsub.listen():
            if message['type'] == 'message':
                yield f"data: {message['data'].decode('utf-8')}\n\n"

    user_id = request.user.id
    response = StreamingHttpResponse(event_stream(user_id), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response


@login_required
def notifications_view(request):
    user = request.user

    if request.method == 'POST':
        # Get unread notifications
        notifications = UserNotification.objects.filter(user=user, is_read=False).order_by('-created_at')
                
        data = [
            {
                'id': notification.id,
                'message': notification.message,
                'is_read': notification.is_read,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for notification in notifications
        ]
        
        # Mark all notifications as read
        notifications.update(is_read=True)
        
        return JsonResponse(data, safe=False)

    else:
        # Return an error for unsupported methods
        return JsonResponse({'status': 'error', 'message': 'Method not allowed.'}, status=405)
    
@csrf_exempt
def get_RAG_content_from_db(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            api_key = data.get('api_key')
            query = data.get('query')
            number_data_retrieval = data.get('number_data_retrav')

            if not api_key or not query:
                return JsonResponse({'status': 'error', 'message': 'Missing required fields: api_key or query'}, status=400)

            profile = get_object_or_404(Profile, api_key=api_key)
            user_id = profile.user.id

            result_from_db = search_in_RAG_db(user_id=user_id, query=query, number_data_retrieval=number_data_retrieval)

            return JsonResponse(result_from_db, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed.'}, status=405)