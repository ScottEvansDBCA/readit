from .models import Category, Post
from .forms import PostForm
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, render, redirect, render_to_response
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.forms.utils import ErrorList
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from bs4 import BeautifulSoup

VALID_TAGS = ['strong','em','p','ul','li','br','b','h1','h2','h3','h4','h5','h6','ol','i','a','dl','s','hr','sup','sub']

class IndexView(generic.ListView):
    """
    This will be the home page, displaying the 10 most recent posts.
    """
    template_name = 'blogs/index.html'
    context_object_name = 'latest_posts_list'

    def get_queryset(self):
        """
        Return the latest 10 posts.
        """
        return Post.objects.filter(create_date__lte=timezone.now()).order_by('-create_date')[:10]

class CategoriesView(generic.ListView):
    """
    This will display all the catergories and link to a page for each.
    """
    template_name = 'blogs/categories.html'
    context_object_name = 'all_categories_list'

    def get_queryset(self):
        """
        Return all categories.
        """
        return Category.objects.all()

class CategoryView(generic.DetailView):
    """
    This will display a list of all posts for the category
    """
    model = Category
    template_name = 'blogs/category.html'


class PostView(generic.DetailView):
    """
    This will display the information for an individual post
    """
    model = Post
    template_name = 'blogs/post.html'

class SearchView(generic.ListView):
    """
    This will display the search the user has provided from the search bar on any other page.
    """
    context_object_name = 'results'
    template_name = 'blogs/search.html'

    def get_queryset(self):
        try:
            query = self.request.GET.get('search')
        except:
            query = ''
        print(query)
        if (query != ''):
            results = Post.objects.filter(Q(content__icontains=query) | Q(title__icontains=query)).order_by('-create_date')
            print(results)
        else:
            results = Post.objects.all()
        return results

class ProfileView(generic.ListView):
    """
    This will display users account information.
    """
    template_name = 'blogs/account.html'
    context_object_name = 'posts'

    def get_queryset(self):
        un = self.request.user.username
        posts = Post.objects.filter(create_by=un).order_by('-create_date')

        return posts
        
class CreatePostView(generic.CreateView):
    """
    This will handle the creation of new posts.
    """
    model = Post
    template_name = 'blogs/createpost.html'
    success_url='/'
    form_class = PostForm
    
    def form_valid(self, form):
        title = self.request.POST.get('title')
        cont = self.request.POST.get('content')
        content = sanitize_html(cont).decode('utf-8')
        cats_as_string = self.request.POST.get('category_csv')
        username=self.request.user.username
        if (cats_as_string == '' or cats_as_string == ' '):
            form.add_error(None, "Categories cannot be empty, please add at least 1.")
            print(form.errors)
            return self.render_to_response(self.get_context_data(form=form))
        time_now = timezone.now()
        categories = cats_as_string.split(",")
        post = Post(title=title, content=content, create_date=time_now, create_by=username)
        post.save()
        check_categories(categories, post)
        post_id = Post.objects.filter(title=title, create_by=username, create_date=time_now)[0].id
        return HttpResponseRedirect("Posts/%s" % post_id)
                   

class EditPostView(generic.UpdateView):
    """
    This view will allow users to edit a post.
    """
    model = Post
    template_name = 'blogs/editpost.html'
    form_class = PostForm

    def get_initial(self):
        post = self.get_object()
        return {'category_csv': Post.categories_as_string(post), 'title': post.title, 'content': post.content}


    def form_valid(self, form):
        cats_as_string = self.request.POST.get('category_csv')
        if (cats_as_string == '' or cats_as_string == ' '):
            form.add_error(None, "Categories cannot be empty, please add at least 1.")
            print(form.errors)
            return self.render_to_response(self.get_context_data(form=form))
        categories = cats_as_string.split(',')
        post = form.save(commit=False)
        new_content = self.request.POST.get('content')
        post.content = sanitize_html(new_content).decode('utf-8')
        post.categories.clear()
        check_categories(categories, post)
        post.save()
        return HttpResponseRedirect("/blog/Posts/%s" % post.id)

class DeletePostView(generic.DeleteView):
    """
    This will be used to allow users to delete a post after confirming.
    """
    template_name = 'blogs/delete.html'
    
    def get_object(self):
        id = self.kwargs.get("pk")
        return get_object_or_404(Post, id=id)

    def post(self, request, *args, **kwargs):
        """
        This is being overridden so that we can cleanup categories at the same time.
        When a user deletes a post, if any of the categories were only linked to
        that 1 post, the category itself is deleted. Just as a bit of db maintenance.
        """
        post = Post.objects.filter(id=self.kwargs.get("pk")).first()
        for category in post.categories.all():
            if category.post_set.all().count() == 1:
                category.delete()
        return self.delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:index')

def sanitize_html(value):

    soup = BeautifulSoup(value)

    for tag in soup.findAll(True):
        if tag.name not in VALID_TAGS:
            tag = tag.extract()
    return soup.renderContents()

def check_categories(categories, post):
    for category in categories:
            if category == "" or category == " ":
                pass
            else:
                category = category.strip()
                category = category.upper()
                cat_exists = Category.objects.filter(name=category).first()
                if cat_exists:
                    post.categories.add(cat_exists)
                else:
                    slug = category.replace(" ", "-")
                    cat = Category(name=category, slug=slug)
                    cat.save()
                    post.categories.add(cat)