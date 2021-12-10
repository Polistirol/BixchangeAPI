from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# Create your forms here.

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)
	referralCode = forms.CharField(max_length=5,required= False,empty_value="-----" )

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		
		if commit:
			user.save()
			user.profile.usedReferral = self.cleaned_data["referralCode"]
		return user