from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    category_csv = forms.CharField(required=True)

    class Meta:
        model = Post
        fields =('title', 'content', 'category_csv')