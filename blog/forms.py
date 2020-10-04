from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        # remove the label
        self.fields['body'].label = ''
        # set the form size
        self.fields['body'].widget = forms.Textarea(attrs={'size': '40'})


class SearchForm(forms.Form):
    query = forms.CharField()



