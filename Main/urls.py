from django.urls import path

from . import views

app_name = 'Main'
urlpatterns = [
    path('', views.home, name='home'),
    path('create_survey', views.create_survey, name='create_survey'),
    path('view_survey/statistics/<int:survey_id>', views.view_survey_statistics, name='view_survey_statistics'),
    path('user_surveys', views.user_surveys, name='user_surveys'),
    path('answer_survey/<int:survey_id>', views.answer_survey, name='answer_survey'),
    path('delete/<int:survey_id>', views.delete, name='delete'),
    path('users', views.users, name='users'),
    path('contact_us', views.contact_us, name='contact_us'),
    path('messages', views.show_messages, name='messages'),
    path('change_survey_status/<int:survey_id>/<str:status>', views.change_survey_status, name='change_survey_status'),
    path('change_message_status/<int:message_id>/<str:status>', views.change_message_status,
         name='change_message_status'),
    path('decrypt', views.decrypt, name='decrypt'),
    path('encrypt', views.encrypt, name='encrypt'),
    path('change_survey_privacy/<int:survey_id>/<str:status>', views.change_survey_privacy,
         name='change_survey_privacy'),
    path('404', views.error, name='404'),
]
