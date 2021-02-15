from django import forms

class ChannelNameForm(forms.Form):
    channel_name = forms.CharField(label='Channel name', max_length=100)

class FirstRunForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100, required=True)
    password1 = forms.CharField(label='Password 1', max_length=32, required=True)
    password2 = forms.CharField(label='Password 2', max_length=32, required=True)

    def clean(self):
        cleaned_data = super(FirstRunForm, self).clean()

        password = cleaned_data.get('password1')
        password_confirm = cleaned_data.get('password2')

        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("The two password fields must match.")
        return cleaned_data
