from django import forms
from . models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        widgets = {
            'text': forms.Textarea(attrs={
                "cols": 40,
                "rows": 10,
                "class": "form-control",
                "required id": "id_text",
            }),
            'group': forms.Select(attrs={
                "class": "form-control",
                "id": "id_group",
            }
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        help_texts = {'text': 'Hапишите комментарий'}
        labels = {'text': 'Комментарий'}
        widgets = {
            'text': forms.Textarea(
                attrs={'class': 'form-control'}
            )
        }
