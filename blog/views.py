import redis
from django.conf import settings
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import TrigramSimilarity
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template.loader import render_to_string
from django.http import Http404, HttpResponse, response, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.utils.translation import gettext as _
from django.views.generic import (ListView, )
from .models import Post, Comment, HeroPost
from .forms import CommentForm, SearchForm

# connect to redis
r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)


def post_search(request):
    form = SearchForm()
    search = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            search = form.cleaned_data['query']
            results = Post.objects.annotate(
                similarity=TrigramSimilarity('title', search),
            ).order_by('-similarity')
    return render(request, 'blog/search.html',
                  {'form': form, 'search': search, 'results': results})


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_context_data(self, **kwargs):
        self.hero = get_object_or_404(HeroPost)
        context = super(PostListView, self).get_context_data(**kwargs)
        context['main_post'] = self.hero.main_post
        context['title_color'] = self.hero.title_color
        context['overlay_opacity'] = self.hero.overlay_opacity
        return context


def post_detail(request, pk, slug):
    post = get_object_or_404(Post, slug=slug, id=pk)
    # increment total post views by 1
    total_views = r.incr(f'post:{post.id}:views')
    # incremment post ranking by 1
    r.zincrby('post_ranking', 1, post.id)
    # get latest posts
    latest_posts = Post.objects.all().order_by('-date_posted')[:5]
    next_post = (Post.objects.filter(id__gt=post.id).exclude(id=post.id).order_by('id').first())
    previous_post = (Post.objects.filter(id__lt=post.id).exclude(id=post.id).order_by('-id').first())
    comments = post.comments.filter(active=True)
    page = request.GET.get('page', 1)
    paginator = Paginator(comments, 4)
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)
    context = {
        'comments': comments,
        'post': post,
        'latest_posts': latest_posts,
        'next_post': next_post,
        'previous_post': previous_post,
        'total_views': total_views,
    }
    return render(request, 'blog/post_detail.html', context)


def post_ranking(request):
    post_ranking = r.zrange('post_ranking', 0, -1, desc=True)[:10]
    post_ranking_ids = [int(id) for id in post_ranking]
    most_viewed = list(Post.objects.filter(id__in=post_ranking_ids))
    most_viewed.sort(key=lambda x: post_ranking_ids.index(x.id))
    return render(request, 'blog/ranking.html', {'most_viewed': post_ranking_ids})


@login_required
def post_comment(request, pk, slug):
    # List of comments for this post
    post = get_object_or_404(Post, slug=slug, id=id)
    new_comment = None
    comments = Comment.objects.filter(active=True)
    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            new_comment.author = request.user
            new_comment.email = request.user.email
            # Save the comment to the database
            new_comment.save()
            messages.success(request, _(f'Your comment has been added!'))
            return redirect('post-detail', slug=slug, pk=pk)
    else:
        comment_form = CommentForm()
    return render(request, 'blog/post_comment.html',
                  {'comments': comments, 'new_comment': new_comment,
                   'comment_form': comment_form, 'site_key': settings.RECAPTCHA_SITE_KEY})


@login_required
def edit_comment(request, comment_id, slug, pk):
    post = get_object_or_404(Post, slug=slug, id=pk)
    comment = get_object_or_404(Comment, id=comment_id)
    comment.post = post
    if comment.author != request.user:
        raise Http404

    if request.method != 'POST':
        form = CommentForm(instance=comment)
    else:
        form = CommentForm(instance=comment, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('post-detail', slug=slug, pk=pk)

    context = {'comment': comment, 'form': form}
    return render(request, 'blog/edit_comment.html', context)


@login_required
def delete_comment(request, comment_id, slug, pk):
    post = get_object_or_404(Post, slug=slug, id=pk)
    comment = get_object_or_404(Comment, id=comment_id)
    comment.post = post

    if comment.author != request.user:
        raise Http404

    if request.method == 'POST':
        comment.delete()
        return redirect('post-detail', slug=slug, pk=pk)

    context = {'slug': comment.post.slug, 'pk': comment.post.id}
    return render(request, 'blog/comment_confirm_delete.html', context)


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})


def directions(request):
    return render(request, 'blog/directions.html', {'title': 'Directions'})


def privacy_policy(request):
    return render(request, 'blog/privacy_policy.html', {'title': 'Privacy Policy'})
