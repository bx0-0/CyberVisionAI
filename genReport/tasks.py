from celery import shared_task # type: ignore
from .report_templates import generate_report_template , get_structure 
from .toolkit import get_assistant_response
from .models import Report
from django.contrib.auth.models import User

@shared_task
def generate_report_task(user_id,bug_name, asset, step_to_reproduce, POC, severity, model):
    if model == "X":
        bug_info = f"bug name: {bug_name}, asset: {asset}, step to reproduce: {step_to_reproduce}, POC: {POC}"
        structure = get_structure(bug_info)
        response = get_assistant_response(bug_info, structure, "X")
        report_template = generate_report_template(bug_name, asset, step_to_reproduce, POC, severity, response)
    else:
        bug_info = f"bug name: {bug_name}, asset: {asset}, step to reproduce: {step_to_reproduce}, POC: {POC}"
        structure = get_structure(bug_name)
        response = get_assistant_response(bug_info, structure, "X-mini")
        report_template = generate_report_template(bug_name, asset, step_to_reproduce, POC, severity, response)
    
    user = User.objects.get(id=user_id)
    print(user)
    print(report_template)
    report = Report(user=user, bug_name=bug_name, asset=asset, step_to_reproduce=step_to_reproduce, POC=POC, report_file=report_template, severity=severity)
    report.save()