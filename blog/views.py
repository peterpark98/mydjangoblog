from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from .models import Post, Comment, Category
from .forms import CommentForm, SearchForm, PostForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
import uuid
import os
from django.http import JsonResponse
from myblog.image_utils import compress_image
# 首页视图
def home(request):
    """博客首页，显示最新发布的文章"""
    posts = Post.objects.filter(status='published').order_by('-publish')[:6]
    categories = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:5]
    popular_posts = Post.objects.filter(status='published').order_by('-views')[:4]
    
    context = {
        'posts': posts,
        'categories': categories,
        'popular_posts': popular_posts,
    }
    return render(request, 'blog/home.html', context)

# 搜索视图
def search(request):
    """文章搜索功能"""
    form = SearchForm(request.GET or None)
    query = None
    results = []
    
    if 'query' in request.GET and form.is_valid():
        query = form.cleaned_data['query']
        results = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query),
            status='published'
        ).order_by('-publish')
    
    context = {
        'form': form,
        'query': query,
        'results': results,
        'categories': Category.objects.annotate(post_count=Count('posts')).order_by('-post_count'),
    }
    return render(request, 'blog/search_results.html', context)

# 文章列表视图
class PostListView(ListView):
    """显示所有已发布的文章，支持分页"""
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_queryset(self):
        # ==================== 核心修改：只显示已发布的文章 ====================
        queryset = super().get_queryset().filter(status='published')
        # =====================================================================
        
        category_slug = self.kwargs.get('category_slug')
        author_id = self.kwargs.get('author_id')
        
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)
        
        if author_id:
            author = get_object_or_404(User, id=author_id)
            queryset = queryset.filter(author=author)
            
        return queryset
    
    def get_context_data(self,** kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        return context

# 文章详情视图
class PostDetailView(DetailView):
    """文章详情页视图，处理文章显示和评论提交"""
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        post_slug = self.kwargs.get('post')
        
        return get_object_or_404(
            Post,
            slug=post_slug,
            status='published',
            publish__year=year,
            publish__month=month,
            publish__day=day
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        post.views += 1
        post.save(update_fields=['views'])
        root_comments = post.comments.filter(active=True, parent=None).order_by('created_on')
        # 定义一个函数，用于递归地将评论树“压平”成一个带层级的列表
        def flatten_comments(comments, level=0):
            result = []
            for comment in comments:
                comment.level = level  # 为每个评论对象动态添加一个 level 属性
                result.append(comment)
                # 获取该评论的所有回复
                replies = comment.replies.filter(active=True).order_by('created_on')
                if replies:
                    # 将回复的压平结果追加到当前列表中
                    result.extend(flatten_comments(replies, level + 1))
            return result

        # 生成最终的、扁平化的评论列表
        comment_list = flatten_comments(root_comments)

        paginator = Paginator(comment_list, 5)
        page = self.request.GET.get('page')

        try:
            comments = paginator.page(page)
        except PageNotAnInteger:
            comments = paginator.page(1)
        except EmptyPage:
            comments = paginator.page(paginator.num_pages)

        context['comment_form'] = CommentForm()
        context['comments'] = comments
        context['related_posts'] = Post.objects.filter(
            category=post.category,
            status='published'
        ).exclude(id=post.id).order_by('-publish')[:3]
        context['categories'] = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        if not request.user.is_authenticated:
            messages.error(request, '请登录后发表评论。')
            return HttpResponseRedirect(self.object.get_absolute_url())

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.user = request.user
            
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    comment.parent = Comment.objects.get(id=parent_id)
                except Comment.DoesNotExist:
                    pass

            # ==================== 最终修复：手动设置时间 ====================
            # 无论 auto_now_add 是否生效，我们都在这里强制赋予当前时间
            comment.created_on = timezone.now()
            # =============================================================
            
            comment.save()
            messages.success(request, '您的评论已成功发布！')
        else:
            messages.error(request, '评论内容不能为空，请重新填写。')
            
        return HttpResponseRedirect(self.object.get_absolute_url())

# 创建文章视图
class PostCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    success_message = "新文章《%(title)s》已成功发布！"
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        
        # 检查用户点击的是哪个按钮
        if 'save_draft' in self.request.POST:
            form.instance.status = 'draft'
            messages.success(self.request, "草稿已成功保存！")
            # 保存对象
            self.object = form.save()
            # 跳转到草稿列表页
            return redirect(reverse_lazy('blog:draft_list'))
        else:
            form.instance.status = 'published'
            messages.success(self.request, "文章已成功发布！")
            
        return super().form_valid(form)
    
    def get_context_data(self,** kwargs):
        context = super().get_context_data(**kwargs)
        context['view'] = {
            'title': '创建新文章',
            'button_text': '发布文章'
        }
        return context

# 更新文章视图
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    success_message = "文章《%(title)s》已更新！"
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs
    
    def form_valid(self, form):
        # 检查用户点击的是哪个按钮
        if 'save_draft' in self.request.POST:
            form.instance.status = 'draft'
            messages.success(self.request, "草稿已成功更新！")
            # 保存对象
            self.object = form.save()
            # 跳转到草稿列表页
            return redirect(reverse_lazy('blog:draft_list'))
        else:
            form.instance.status = 'published'
            if self.get_object().status == 'draft':
                 messages.success(self.request, "文章已成功发布！")
            else:
                 messages.success(self.request, "文章已成功更新！")

        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
    def get_context_data(self,** kwargs):
        context = super().get_context_data(**kwargs)
        context['view'] = {
            'title': '编辑文章',
            'button_text': '更新文章'
        }
        return context

# 删除文章视图
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_message = "文章已成功删除！"
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    # 重写 get_success_url 方法，根据文章状态决定跳转到哪里
    def get_success_url(self):
        post = self.get_object()
        if post.status == 'draft':
            return reverse_lazy('blog:draft_list')
        else:
            return reverse_lazy('home') # 或者 'blog:post_list'

    # 重写 delete 方法，以确保 success_message 能正常工作
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(PostDeleteView, self).delete(request, *args, **kwargs)

# 作者文章列表视图
class AuthorPostListView(ListView):
    model = Post
    template_name = 'blog/author_posts.html'
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(
            author=self.author,
            status='published'
        ).order_by('-publish')
    
    def get_context_data(self,** kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        context['categories'] = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        return context

# 分类文章列表视图
class CategoryPostListView(ListView):
    model = Post
    template_name = 'blog/category_posts.html'
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(category=self.category, status='published').order_by('-publish')
    
    def get_context_data(self,** kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        return context

# 删除评论视图
@login_required
def delete_comment(request, pk):
    comment_to_delete = get_object_or_404(Comment, pk=pk)
    post_url = comment_to_delete.post.get_absolute_url()

    if comment_to_delete.user != request.user:
        messages.error(request, '您没有权限删除此评论。')
        return redirect(post_url)

    if request.method == 'POST':
        if comment_to_delete.replies.exists():
            comment_to_delete.content = "[该评论已删除]"
            comment_to_delete.user = None
            comment_to_delete.save()
            messages.info(request, '评论已删除，但其回复被保留。')
        
        else:
            parent = comment_to_delete.parent
            comment_to_delete.delete()
            messages.success(request, '评论已成功删除。')

            if parent:
                if parent.user is None and not parent.replies.exists():
                    current_parent = parent
                    while current_parent:
                        if current_parent.user is None and not current_parent.replies.exists():
                            grandparent = current_parent.parent
                            current_parent.delete()
                            current_parent = grandparent
                        else:
                            break 

        return redirect(post_url)

    return render(request, 'blog/comment_confirm_delete.html', {'comment': comment_to_delete})

@csrf_exempt
def ckeditor_upload_view(request):
    """
    一个自定义的、安全的 CKEditor 图片上传视图，整合了：
    1. 图片压缩功能。
    2. 基于 UUID 的唯一、安全文件名生成。
    3.严格的文件类型白名单检查。
    """
    if request.method == 'POST' and request.FILES.get('upload'):
        uploaded_file = request.FILES['upload']

        try:
            # 获取原始文件扩展名
            original_ext = os.path.splitext(uploaded_file.name)[1].lower()
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}

            if original_ext not in allowed_extensions:
                return JsonResponse({
                    'error': {'message': '不支持的文件类型。'}
                }, status=400)

            # 调用我们的压缩函数 ---
            _, compressed_file = compress_image(uploaded_file)
            
            # 生成基于 UUID 的安全文件名 (借鉴自您的函数) ---
            safe_filename = f"{uuid.uuid4().hex}.jpg"
            
            # 保存压缩后的图片 ---
            save_path = os.path.join('posts', safe_filename)
            
            # 使用 Django 的文件存储 API 保存文件
            actual_filename = default_storage.save(save_path, compressed_file)
            
            # 获取已保存文件的公共 URL
            file_url = default_storage.url(actual_filename)

            # 按 CKEditor 要求返回 JSON
            return JsonResponse({'url': file_url})

        except Exception as e:
            print(f"--- 图片处理/保存时出错: {e} ---")
            return JsonResponse({'error': {'message': f'服务器处理图片时出错: {e}'}}, status=500)

    return JsonResponse({'error': {'message': '无效的请求或未上传文件。'}}, status=400)

class DraftListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/draft_list.html' 
    context_object_name = 'drafts'
    paginate_by = 10

    def get_queryset(self):
        # 返回当前登录用户的、状态为'draft'的文章，按更新时间排序
        return Post.objects.filter(
            author=self.request.user, 
            status='draft'
        ).order_by('-updated')