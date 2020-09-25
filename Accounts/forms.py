from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from Main.models import Users


class UsersCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = Users
        fields = ('email',)


class UsersChangeForm(UserChangeForm):
    class Meta:
        model = Users
        fields = ('email',)
