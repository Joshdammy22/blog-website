from django import forms
from .models import *


class BlogForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text="Select up to 5 tags."
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text="Select up to 3 categories."
    )

    class Meta:
        model = Blog
        fields = ['title', 'content', 'blog_image', 'status', 'categories', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'blog_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_categories(self):
        categories = self.cleaned_data.get('categories')
        if categories and categories.count() > 3:
            raise forms.ValidationError("You can select up to 3 categories only.")
        return categories

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if tags and tags.count() > 5:
            raise forms.ValidationError("You can select up to 5 tags only.")
        return tags


class BlogUpdateForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text="Select up to 5 tags."
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text="Select up to 3 categories."
    )

    class Meta:
        model = Blog
        fields = ['title', 'content', 'blog_image', 'status', 'categories', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'blog_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_categories(self):
        categories = self.cleaned_data.get('categories')
        if categories and categories.count() > 3:
            raise forms.ValidationError("You can select up to 3 categories only.")
        return categories

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if tags and tags.count() > 5:
            raise forms.ValidationError("You can select up to 5 tags only.")
        return tags
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Prepopulate content field with current data
        if self.instance:
            self.fields['content'].initial = self.instance.content


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

REACTION_CHOICES = [
    ('like', 'Like'),
    ('love', 'Love'),
    ('haha', 'Haha'),
    ('wow', 'Wow'),
    ('applaud', 'Applaud'),
]

class ReactionForm(forms.Form):
    reaction = forms.ChoiceField(choices=REACTION_CHOICES)
