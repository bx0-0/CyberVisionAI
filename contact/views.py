from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .models import QuestionAndAnswer
# Create your views here.


def send_massage(request):
    try:
        if request.method == "POST":
            subject = request.POST.get("subject")
            message = request.POST.get("message")
            email = request.POST.get("email")

            if subject and message and email:
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=email,  #!from
                        recipient_list=[settings.EMAIL_HOST_USER],  #! to
                        fail_silently=False,
                    )
                    messages.success(
                        request=request, message="Email has been sent successfully."
                    )

                except Exception:  # Catch the exception
                    messages.error(request=request, message="Error occurred: ")
            else:
                messages.info(request=request, message="All fields are required.")
    except Exception as e:
        messages.error(request=request, message=f"Error occurred please try again , {e}")            

    context = {}
    return render(request, "contact/contact.html", context=context)


def question_and_answer(request):
    question_and_answer = QuestionAndAnswer.objects.all()
    context = {'question_and_answer': question_and_answer}
    return render(request, "contact/q&a.html", context=context)