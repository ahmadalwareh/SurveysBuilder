# Create your views here.
import hashlib
import json
import base64, os
import string
import random
from collections import OrderedDict
from itertools import count
from Crypto.Cipher import AES
from Main.models import Users as user, Surveys as survey, \
    Questions as question, Answers as answer, Messages as message, UsersAnswers as users_answers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template.defaultfilters import length
from django.utils.text import capfirst
from django.db.models.aggregates import Count

from Main.survey_crypto import AESCipher as aes


def home(request):
    return render(request, 'home.html')


def create_survey(request):
    global new_survey
    if user.is_authenticated:
        if request.is_ajax() and request.method == 'POST':
            json_data = request.POST
            is_private = capfirst(json_data.__getitem__('is_private'))
            survey_title = json_data.__getitem__('survey_title')
            survey_name = json_data.__getitem__('survey_name')
            survey_json_data = json_data.__getitem__('survey_data')
            data = json.loads(survey_json_data)
            new_survey = survey(title=survey_title, s_name=survey_name, s_status='waiting',
                                is_private=is_private, is_encrypted=False, user_id=request.user.id)
            new_survey.save()
            print(new_survey.title)
            for item in data:
                if item['type'] == 'checkbox-group':
                    new_question = question(question_type=item['type'], question_body=item['label'],
                                            survey_id=new_survey.id)
                    new_question.save()
                    for values in item['values']:
                        new_answer = answer(answer=values['label'], question_id=new_question.id)
                        new_answer.save()
                elif item['type'] == 'radio-group':
                    new_question = question(question_type=item['type'], question_body=item['label'],
                                            survey_id=new_survey.id)
                    new_question.save()
                    for values in item['values']:
                        new_answer = answer(answer=values['label'], question_id=new_question.id)
                        new_answer.save()
                        if values['selected']:
                            pass
                elif item['type'] == 'select':
                    new_question = question(question_type=item['type'], question_body=item['label'],
                                            survey_id=new_survey.id)
                    new_question.save()
                    for values in item['values']:
                        new_answer = answer(answer=values['label'], question_id=new_question.id)
                        new_answer.save()
                else:
                    new_question = question(question_type=item['type'], question_body=item['label'],
                                            survey_id=new_survey.id)
                    new_question.save()
            return HttpResponse('1')
        else:
            return render(request, 'create_survey.html')
    else:
        return redirect('login.html')


def end_survey(request):
    if user.is_authenticated:
        if request.method == 'POST':
            # code here
            return HttpResponse('survey created')

    else:
        return redirect('login.html')


def user_surveys(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            surveys = survey.objects.all()
            context = {'user_surveys': surveys}
            return render(request, 'user_surveys.html', context)
        else:
            surveys = survey.objects.filter(user_id=request.user.id).values('id', 's_name', 'title', 'creation_date',
                                                                            's_status', 'is_private', 'is_encrypted', 'user_id')
            context = {'user_surveys': surveys}
            return render(request, 'user_surveys.html', context)
    else:
        return redirect('Accounts:login')


def view_survey_statistics(request, survey_id):
    if request.user.is_authenticated:
        select_survey = survey.objects.get(id=survey_id)
        select_questions = question.objects.filter(survey_id=survey_id).values('id', 'question_body', 'question_type', )
        questions_id = question.objects.filter(survey_id=survey_id).values_list('id', flat=True)
        select_answers = answer.objects.filter(question_id__in=questions_id).values('question_id', 'answer', 'id')
        answers_id = answer.objects.filter(question_id__in=questions_id).values_list('id', flat=True)
        select_users_answers = users_answers.objects.filter(answer_id__in=answers_id) \
            .values('answer_id').annotate(Count('id')).order_by()

        survey_dict = {
            'select_questions': select_questions,
            'select_survey': select_survey,
            'select_answers': select_answers,
            'select_users_answers': select_users_answers,
        }
        return render(request, 'statistics.html', survey_dict)
    else:
        return redirect('login.html')


def answer_survey(request, survey_id):
    global user_id
    try:
        select_survey = survey.objects.get(id=survey_id)

        if request.method == 'POST':
            if request.user.is_authenticated:
                user_id = request.user.id
            elif request.user.is_anonymous:
                user_id = 1
            json_data = json.dumps(request.POST)
            data = json.loads(json_data)
            for key in data:
                if key.isdigit():
                    new_answer = users_answers(answer_id=key, user_id=user_id)
                    new_answer.save()
                    print(new_answer.answer_id, new_answer.user_id)
                elif key.startswith('radio'):
                    new_answer = users_answers(answer_id=data[key], user_id=user_id)
                    new_answer.save()
                    print(new_answer.answer_id, new_answer.user_id)
                elif key.startswith('csrf'):
                    pass
                else:
                    print(key, data[key])
                    question_and_answer = key.split(',')
                    create_answer = answer(answer=data[key], question_id=question_and_answer[-1])
                    create_answer.save()
                    new_answer = users_answers(answer_id=create_answer.id, user_id=user_id)
                    new_answer.save()
                    print(
                        'new users answers field ', new_answer.answer_id, new_answer.user_id
                    )
                    print(
                        'create answer field ', create_answer.id, create_answer.question_id, create_answer.answer
                    )
            return render(request, 'thank_you.html')
        elif select_survey.is_private and select_survey.is_encrypted == False \
                and select_survey.s_status == 'active':
            if request.user.is_authenticated:
                select_questions = question.objects.filter(survey_id=survey_id).values('id', 'question_body',
                                                                                       'question_type', )
                questions_id = question.objects.filter(survey_id=survey_id).values_list('id', flat=True)
                select_answers = answer.objects.filter(question_id__in=questions_id).values('question_id', 'answer',
                                                                                            'id')
                survey_dict = {
                    'questions': select_questions,
                    'survey': select_survey,
                    'answers': select_answers
                }
                return render(request, 'answer_survey.html', survey_dict)
            else:
                return render(request, 'login_first.html')
        elif select_survey.is_private == False and select_survey.is_encrypted == False \
                and select_survey.s_status == 'active':
            select_questions = question.objects.filter(survey_id=survey_id).values('id', 'question_body',
                                                                                   'question_type', )
            questions_id = question.objects.filter(survey_id=survey_id).values_list('id', flat=True)
            select_answers = answer.objects.filter(question_id__in=questions_id).values('question_id', 'answer', 'id')
            survey_dict = {
                'questions': select_questions,
                'survey': select_survey,
                'answers': select_answers
            }
            return render(request, 'answer_survey.html', survey_dict)
        else:
            return HttpResponse('You are Not Allowed To see This Survey')
    except ObjectDoesNotExist:
        return render(request, '404.html')


def change_survey_status(request, survey_id, status):
    survey_to_change_status = survey.objects.get(id=survey_id)
    if request.user.is_authenticated and request.user.is_superuser:
        survey_to_change_status.s_status = status
        survey_to_change_status.save()
        return redirect('Main:user_surveys')
    elif request.user.is_authenticated and survey_to_change_status.user_id == request.user.id and status == 'ended':
        survey_to_change_status.s_status = status
        survey_to_change_status.save()
        return redirect('Main:user_surveys')
    else:
        return render(request, '404.html')


def change_survey_privacy(request, survey_id, status):
    survey_to_change_privacy = survey.objects.get(id=survey_id)
    if request.user.is_authenticated and request.user.is_superuser or \
            request.user.is_authenticated and survey_to_change_privacy.user_id == request.user.id:
        if status == 'private':
            survey_to_change_privacy.is_private = True
            survey_to_change_privacy.save()
        elif status == 'public':
            survey_to_change_privacy.is_private = False
            survey_to_change_privacy.save()
        else:
            return HttpResponse('Survey Privacy is Wrong')
        return redirect('Main:user_surveys')
    else:
        return render(request, '404.html')


def users(request):
    if request.user.is_authenticated and request.user.is_superuser:
        get_all_users = user.objects.all()
        send_all_users = {
            'all_users': get_all_users
        }
        return render(request, 'users.html', send_all_users)
    else:
        return HttpResponse('You are Not Allowed to View This Page')


def contact_us(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            subject = request.POST['subject']
            msg = request.POST['message']
            name = request.user.first_name + request.user.last_name
            new_message = message(sender_email=request.user.email, sender_name=name,
                                  msg_subject=subject, msg_text=msg, msg_status='unread', user_id=request.user.id)
            new_message.save()
        return render(request, 'report_to_admin.html')
    else:
        if request.method == 'POST':
            name = request.POST['fullname']
            subject = request.POST['subject']
            email = request.POST['email']
            msg = request.POST['message']
            new_message = message(sender_email=email, sender_name=name,
                                  msg_subject=subject, msg_text=msg, msg_status='unread')
            new_message.save()
        return render(request, 'contact_us.html')


def show_messages(request):
    if request.user.is_authenticated and request.user.is_superuser:
        messages = message.objects.all()
        context = {
            'messages': messages
        }
        return render(request, 'messages.html', context)
    return HttpResponse('You are Not Allowed to View This Page')


def change_message_status(request, message_id, status):
    if request.user.is_authenticated and request.user.is_superuser:
        if status == 'unread' or status == 'read':
            message_to_change_status = message.objects.get(id=message_id)
            message_to_change_status.msg_status = status
            message_to_change_status.save()
            return redirect('Main:messages')
        else:
            return HttpResponse('Message Status Error Check Status Send By FrontEnd')
    return HttpResponse('You are Not Allowed to View This Page')


def generate_secret_key_for_AES_cipher(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str


def encrypt(request):
    global select_survey
    if request.user.is_authenticated:
        if request.method == 'POST':
            json_data = json.dumps(request.POST)
            data = json.loads(json_data)
            for key in data:
                if key == 'id':
                    select_survey = survey.objects.get(id=data[key])
            if request.user.id == select_survey.user_id:
                questions_id = question.objects.filter(survey_id=select_survey.id).values_list('id', flat=True)
                encryption_key = generate_secret_key_for_AES_cipher(50)
                for e in answer.objects.all():
                    if e.question_id in questions_id:
                        cipher = aes(key=encryption_key)
                        cipher_text = cipher.encryption(e.answer)
                        e.answer = cipher_text
                        e.save()
                select_survey.is_encrypted = True
                select_survey.save()
                return HttpResponse(encryption_key)
            else:
                return HttpResponse("Only Survey Owner Can Encrypt it .. !")
        else:
            return HttpResponse('Message Error Check encrypt status Send By FrontEnd')
    else:
        return render(request, 'login.html')


def decrypt(request):
    global select_survey, decryption_key
    if request.user.is_authenticated:
        if request.method == 'POST':
            json_data = json.dumps(request.POST)
            data = json.loads(json_data)
            for key in data:
                if key == 'id':
                    select_survey = survey.objects.get(id=data[key])
                elif key == 'decryption_key':
                    decryption_key = data[key]
            if request.user.id == select_survey.user_id:
                questions_id = question.objects.filter(survey_id=select_survey.id).values_list('id', flat=True)
                try:
                    for e in answer.objects.all():
                        if e.question_id in questions_id:
                            cipher = aes(key=decryption_key)
                            plain_text = cipher.decryption(e.answer)
                            e.answer = plain_text
                            print(plain_text)
                            e.save()
                    select_survey.is_encrypted = False
                    select_survey.save()
                    return HttpResponse(1)
                except UnicodeDecodeError:
                    return HttpResponse('Failed')
            else:
                return HttpResponse("Only Survey Owner Can Encrypt it .. !")
        else:
            return HttpResponse('Message Error Check encrypt status Send By FrontEnd')
    else:
        return render(request, 'login.html')


def delete(request, survey_id):
    select_survey = survey.objects.get(id=survey_id)
    if request.user.is_authenticated and request.user.id == select_survey.user_id or \
            request.user.is_authenticated and request.user.is_superuser:
        select_questions = question.objects.all().filter(survey_id=survey_id)
        select_answers = answer.objects.all().filter(question_id__in=select_questions)
        select_users_answers = users_answers.objects.all().filter(answer_id__in=select_answers)
        for ua in select_users_answers:
            ua.delete()
        for a in select_answers:
            a.delete()
        for q in select_questions:
            q.delete()
        select_survey.delete()
        return redirect('Main:user_surveys')
    else:
        return redirect(request, 'Main:404')
def error(request):
    return render(request, '404.html')
