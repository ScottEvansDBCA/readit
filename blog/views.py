from .models import Category, Post
from .forms import PostForm
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q



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



def search(request):
    """
    This will allow users to search the entire posts for any text
    """
    template = 'blogs/search.html'
    query = request.GET.get('search')
    results = Post.objects.filter(Q(content__icontains=query) | Q(title__icontains=query)).order_by('-create_date')

    context = {
        'results': results
    }

    return render(request, template, context)

        
def profile(request):
    """
    This will display users account information.
    """
    un = request.user.username
    posts = Post.objects.filter(create_by=un).order_by('-create_date')
    t = loader.get_template('blogs/account.html')
    context = {
        'posts' : posts,
    }

    return HttpResponse(t.render(context, request))
    
def createpost(request):
    if request.POST:
        title = request.POST.get('title')
        content = request.POST.get('content')
        cats_as_string = request.POST.get('categories')
        time_now = timezone.now()
        if title != "New post" and title != "":
            if content != "":
                if cats_as_string!="Categories comma seperated" and cats_as_string != "":
                    #valid input, save and continue to post page
                    categories = cats_as_string.split(",")
                    post = Post(title=title, content=content, create_date=time_now, create_by=request.user.username)
                    post.save()
                    for category in categories:
                        if category == "" or category == " ":
                            pass
                        else:
                            category = category.strip()
                            category = category.upper()
                            cat_exists = Category.objects.filter(name=category).first()
                            if cat_exists:
                                post.categories.add(cat_exists)
                                post.save()
                            else:
                                #DB must have been initialised with at least 1 category otherwise following line will fail.
                                maxid = Category.objects.all().order_by('-id')[0].id
                                maxid += 1
                                slug = category.replace(" ", "-")
                                cat = Category(name=category, slug=slug)
                                cat.save()
                                post.categories.add(cat)
                                post.save()
                    post_id = Post.objects.filter(title=title, create_by=request.user.username, create_date=time_now)[0].id
                    return HttpResponseRedirect("Posts/%s" % post_id)
                else:
                    #reject due to blank categories
                    t = loader.get_template('blogs/createpost.html')
                    context = {
                        'error': "*Post is uncategorized, please enter at least 1 category.",
                        'title': title,
                        'content': content,
                        'categories': cats_as_string,
                    }
                    return HttpResponse(t.render(context, request))
            else:
                #reject due to no content
                t = loader.get_template('blogs/createpost.html')
                context = {
                    'error': "*Post is blank, please enter some content.",
                    'title': title,
                    'content': content,
                    'categories': cats_as_string,
                }
                return HttpResponse(t.render(context, request))
        else:
            #reject due to unnamed post
            t = loader.get_template('blogs/createpost.html')
            context = {
                'error': "*Post has no title, please enter a title.",
                'title': title,
                'content': content,
                'categories': cats_as_string,
            }
            return HttpResponse(t.render(context, request))

    else:    
        t = loader.get_template('blogs/createpost.html')
        context = {
        }
        return HttpResponse(t.render(context, request))


def editpost(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.POST:
        form = PostForm(request.POST, instance=post)
        cats_as_string = request.POST.get('categories')
        categories = cats_as_string.split(',')     
        post = form.save(commit=False)
        post.categories.clear()
        for category in categories:
            category = category.strip()
            category = category.upper()
            if category == "" or category == " ":
                pass
            elif category in post.categories.all():
                pass
            else:
                cat_exists = Category.objects.filter(name=category).first()
                if cat_exists:
                    post.categories.add(cat_exists)
                    post.save()
                else:
                    #DB must have been initialised with at least 1 category otherwise following line will fail.
                    maxid = Category.objects.all().order_by('-id')[0].id
                    maxid += 1
                    slug = category.replace(" ", "-")
                    cat = Category(name=category, slug=slug)
                    cat.save()
                    post.categories.add(cat)
        if form.is_valid():
            post.save()
            return HttpResponseRedirect("/blog/Posts/%s" % pk)
    else:
        form = PostForm(instance=post)
    return render(request, "blogs/editpost.html", {'post': post, 'form': form})

def deletepost(request, pk):
    post = Post.objects.filter(pk=pk).first()
    return render(request, "blogs/delete.html", {'post': post})

def deleteconfirmed(request, pk):
    post = Post.objects.filter(pk=pk).first()
    post.delete()
    return HttpResponseRedirect("/blog/")