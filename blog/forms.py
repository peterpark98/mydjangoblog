from django import forms
from .models import Comment, Post, Category
from django_ckeditor_5.widgets import CKEditor5Widget

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '发表一条友善的评论吧...'
            }),
        }
        labels = {
            'content': ''
        }

class SearchForm(forms.Form):
    query = forms.CharField(
        label=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '搜索文章...'
        })
    )

class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) 
        super(PostForm, self).__init__(*args, **kwargs)
        
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = "请选择一个分类"

    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name='default'
            ),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }