from __future__ import absolute_import

from Accounts.tokens import account_activation_token
from Main.models import Users as user, Countries
from django.contrib.auth.models import auth
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


def register(request):
    countries_list = Countries.objects.all()
    if request.user.is_authenticated:
        return HttpResponse('user is logged in')
    else:
        if request.method == 'POST':
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            birth_date = request.POST['birth_date']
            mobile = request.POST['mobile']
            email = request.POST['email']
            password = request.POST['password']
            re_password = request.POST['re_password']
            gender = request.POST['gender']
            country = request.POST['country']
            try:
                u = user.objects.get(email=email)
                print("User" + u.email + "Already Exist")
                return render(request, 'register.html')

            except ObjectDoesNotExist:
                if password == re_password:
                    user.objects.create_user(email=email, password=password,
                                             mobile=mobile, first_name=first_name,
                                             last_name=last_name, birth_date=birth_date,
                                             gender=gender, country_id=country, role_id=3, is_active=False)
                    print("User Created")
                    u = user.objects.get(email=email)
                    current_site = get_current_site(request)
                    mail_subject = 'Activate your Onion account.'
                    message = render_to_string('acc_active_email.html', {
                        'user': u,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(u.pk)),
                        'token': account_activation_token.make_token(u),
                    })
                    email = EmailMessage(
                        mail_subject, message, to=[email]
                    )
                    print(mail_subject)
                    print(message)

                    email.send()
                    return HttpResponse('Activation link has been sent to your account.'
                                        ' please active your account to login')
        else:
            print(countries_list)
            return render(request, 'register.html', {"Countries": countries_list})


def create_user(request):
    if request.user.is_superuser:
        countries_list = Countries.objects.all()
        if request.method == 'POST':
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            birth_date = request.POST['birth_date']
            mobile = request.POST['mobile']
            email = request.POST['email']
            password = request.POST['password']
            re_password = request.POST['re_password']
            gender = request.POST['gender']
            country = request.POST['country']
            try:
                is_superuser = request.POST['is_superuser']
            except MultiValueDictKeyError:
                is_superuser = 0
            try:
                is_staff = request.POST['is_staff']
            except MultiValueDictKeyError:
                is_staff = 0
            try:
                is_active = request.POST['is_active']
            except MultiValueDictKeyError:
                is_active = 0
            try:
                u = user.objects.get(email=email)
                return HttpResponse('User Already Exist')

            except ObjectDoesNotExist:
                if password == re_password:
                    user.objects.create_user(email=email, password=password,
                                             mobile=mobile, first_name=first_name,
                                             last_name=last_name, birth_date=birth_date,
                                             gender=gender, country_id=country, role_id=3, is_active=is_active,
                                             is_superuser=is_superuser, is_staff=is_staff)
            return redirect('Accounts:create_user')
        else:
            return render(request, 'create_user.html', {"Countries": countries_list})


def login(request):
    if request.user.is_authenticated:
        return HttpResponse('user is logged in <p> logout? </p>')
    else:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            print(password)
            user = auth.authenticate(email=email, password=password)
            if user is not None:
                auth.login(request, user)
                print("authenticated user")
                return redirect('Main:user_surveys')
            else:
                print("auth  failed")
                return redirect('Accounts:login')
        else:
            return render(request, 'login.html')


def logout(request):
    if user.is_authenticated:
        auth.logout(request)
        print('successfully logged out')
        return redirect('Accounts:login')
    else:
        response = HttpResponse("User is not logged in.")
        return response


def test(request):
    if request.user.is_authenticated:
        response = HttpResponse("User is Authenticated.")
        return response
    else:
        response = HttpResponse("User is not Authenticated.")
        return response


def activate(request, uidb64, token, ):
    try:
        from Main.models import Users as user
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = user.objects.get(pk=uid)
        print(user)
    except(TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        # auth.login(request, user)
        return render(request, 'confirmation.html')
    else:
        return HttpResponse('Activation link is invalid!')


def change_password(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            old_password = request.POST.get('old_password')
            password = request.POST.get('password')
            re_password = request.POST.get('re_password')
            if old_password != password and password == re_password \
                    and old_password is not None and password is not None:
                user.set_password(password)
                user.save()
                print('password changed')
        return render(request, 'change_password.html')
    else:
        return redirect('login.html')


def change_user_status(request, user_id, status):
    if request.user.is_authenticated and request.user.is_superuser:
        user_to_change = user.objects.get(id=user_id)
        user_to_change.is_active = status
        user_to_change.save()
        return redirect('Main:users')
    return render(request, '404.html')


def change_user_privilege(request, user_id, status):
    if request.user.is_authenticated and request.user.is_superuser:
        user_to_change = user.objects.get(id=user_id)
        user_to_change.is_superuser = status
        user_to_change.save()
        return redirect('Main:users')
    return render(request, '404.html')


def update_info(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            birth_date = request.POST['birth_date']
            mobile = request.POST['mobile']
            gender = request.POST['gender']
            u = user.objects.get(pk=request.user.id)
            u.first_name = first_name
            u.last_name = last_name
            u.birth_date = birth_date
            u.mobile = mobile
            u.gender = gender
            u.save()
            return redirect('Accounts:update_info')
        else:
            return render(request, 'update_info.html')
    else:
        return redirect('Main:home')
