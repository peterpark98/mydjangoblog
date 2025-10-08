from .models import Category, Post
from django.db.models import Count
from .forms import SearchForm

def common_data(request):
    """为所有模板提供通用的上下文数据"""
    # 获取分类列表（按文章数量排序）
    categories = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')

    # 获取热门文章列表（按浏览量排序）
    popular_posts = Post.objects.filter(status='published').order_by('-views')[:5]

    # 添加搜索表单
    search_form = SearchForm()

    return {
        'categories': categories,
        'popular_posts': popular_posts,
        'search_form': search_form,
    }