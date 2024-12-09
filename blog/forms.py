from django import forms
from .models import *

class BlogForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    class Meta:
        model = Blog
        fields = ['title', 'content', 'blog_image','status', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the blog title',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your content here...',
                'rows': 10,
            }),
            'blog_image': forms.FileInput(attrs={
                'class': 'form-control',
            }),
        }

        def clean_tags(self):
            tags = self.cleaned_data.get('tags')
            if len(tags) > 3:
                raise forms.ValidationError("You can select up to three tags.")
            return tags


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your comment...',
                'rows': 3,
            }),
        }
