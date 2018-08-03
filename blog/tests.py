import datetime
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Post, Category
from .forms import PostForm

def create_post(title, content, days, create_by, categories):
    """
    Creates a dummy post with test data.
    """
    time = timezone.now() + datetime.timedelta(days=days)
    post = Post.objects.create(title=title, content=content, create_date=time, create_by=create_by)
    for category in categories.split(','):
        post.categories.add(create_category(category))
    return post

def create_category(name):
    """
    Creates a dummy category with test data.
    """
    slug = name.replace(' ', '-')
    return Category.objects.create(name=name, slug=slug)


class  PageTests(TestCase):
    def test_login_render(self):
        """Tests that the login page works.
        """
        url = reverse('blog:login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_account_render(self):
        """Tests that the account page works.
        """
        self.client.login(username="test", password="usertesting")
        url = reverse('blog:profile_view')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blogs/account.html')

    def test_index_render(self):
        """Tests that the index page works.
        """
        url = reverse('blog:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blogs/index.html')

    def test_categories_render(self):
        """Tests that the categories page works.
        """
        url = reverse('blog:categories')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blogs/categories.html')

    def test_search_render(self):
        """Tests that the search page works. This should pass but return
        nothing in the queryset as we technically have no data to search
        through.
        """
        url = reverse('blog:search')
        response = self.client.get(url, {'search': 'hello_world'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blogs/search.html')

    def test_post_detail_render(self):
        """Tests that the detail view for a post works.
        """
        post = create_post("title","content",0,"test","one,two,three")
        url = reverse('blog:detail', args=(post.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blogs/post.html')

    def test_category_render(self):
        """Tests that the category page renders for an individual.
        We will need to create a category as the db will be empty.
        """
        category = create_category("hello")
        url = reverse('blog:category', args=(category.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blogs/category.html')
    
    def test_create_post_render(self):
        """Tests that the create post page renders.
        """
        url = reverse('blog:new_post')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blogs/createpost.html')

    def test_edit_post_render(self):
        """Test that the edit post page renders. Will need to create
        a post for this to work.
        """
        post = create_post("hello_world","hello_content",0,"test","one, two, three")
        url = reverse('blog:edit', args=(post.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blogs/editpost.html')

    def test_delete_post_render(self):
        """Test that the edit post page renders. Will need to create
        a post for this to work.
        """
        post = create_post("hello_world","hello_content",0,"test","one, two, three")
        url = reverse('blog:delete', args=(post.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blogs/delete.html')


class FormTests(TestCase):
    def test_post_form_correct_data(self):
        """Tests that the createpost form works.
        """
        form_data = {'title': 'Hello_world', 'content':'hello content', 'category_csv': 'one, two, three'}
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_post_form_missing_categories(self):
        """Tests that the createpost form does not work when passing no categories.
        """
        form_data = {'title': 'Hello_world', 'content':'hello content'}
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_post_form_missing_content(self):
        """Tests that the createpost form does not work when passing no content.
        """
        form_data = {'title': 'Hello_world', 'category_csv': 'one, two, three'}
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_post_form_missing_title(self):
        """Tests that the createpost form does not work when passing no title.
        """
        form_data = {'content':'hello content', 'category_csv': 'one, two, three'}
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())

class HtmlTests(TestCase):
    def test_content_html_valid_data(self):
        """Tests that valid html, using allowed tags is saved correctly.
        """
        content = "<h1>heading tag</h1><p>paragraph tag</p><b>bold tag</b>"
        url = reverse('blog:new_post')
        response = self.client.post(url, {'title':'hello_world', 'content':content, 'category_csv':'one, two, three'})
        self.assertEqual(response.status_code, 302)
        url2 = reverse('blog:detail', args=("1"))
        response2 = self.client.get(url2)
        self.assertTrue(response2.status_code, 200)
        self.assertContains(response2, content)

    def test_content_html_invalid_data(self):
        """Tests that invalid html, using tags that are banned are saved
        without those tags included in the content.
        """
        content = "<h1>heading tag</h1><p>paragraph tag</p><b>bold tag</b>"
        content_bad = "<script>thiscouldbedangerousjavascript</script>"
        content_total = content + content_bad
        url = reverse('blog:new_post')
        response = self.client.post(url, {'title':'hello_world', 'content':content_total, 'category_csv':'one, two, three'})
        self.assertEqual(response.status_code, 302)
        url2 = reverse('blog:detail', args=("1"))
        response2 = self.client.get(url2)
        self.assertTrue(response2.status_code, 200)
        self.assertContains(response2, content)
        self.assertNotContains(response2, content_bad)