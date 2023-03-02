# Testing Models
## seUpTestData
テストを通して利用する（変更しない）オブジェクト生成

## フィールドラベル(first nameなど)を取得して検証
```
def test_first_name_label(self):
    author = Author.objects.get(id=1)
    field_label = author._meta.get_field('first_name').verbose_name
    self.assertEqual(field_label, 'first name')
```
## 最大文字数の検証
```
def test_first_name_max_length(self):
    author = Author.objects.get(id=1)
    max_length = author._meta.get_field('first_name').max_length
    self.assertEqual(max_length, 100)
```
## 絶対パスの検証
```
def test_get_absolute_url(self):
    author = Author.objects.get(id=1)
    # This will also fail if the urlconf is not defined.
    self.assertEqual(author.get_absolute_url(), '/catalog/author/1')
```

# Testing Forms
## 過去の日付で更新に失敗すること
```
def test_renew_form_date_in_past(self):
    date = datetime.date.today() - datetime.timedelta(days=1)
    form = RenewBookForm(data={'renewal_date': date})
    self.assertFalse(form.is_valid())
```
## 今日の日付で更新できること
```
def test_renew_form_date_today(self):
    date = datetime.date.today()
    form = RenewBookForm(data={'renewal_date': date})
    self.assertTrue(form.is_valid())
```
# Testing Views
## pagination tests
```
def setUpTestData(cls):
    # Create 13 authors for pagination tests
    number_of_authors = 13

    for author_id in range(number_of_authors):
        Author.objects.create(
            first_name=f'Dominique {author_id}',
            last_name=f'Surname {author_id}',
        )
```
## viewのurlが存在すること
```
def test_view_url_exists_at_desired_location(self):
    response = self.client.get('/catalog/authors/')
    self.assertEqual(response.status_code, 200)
```
## 指定のテンプレートが使用されていること
```
def test_view_uses_correct_template(self):
    response = self.client.get(reverse('authors'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'catalog/author_list.html')
```
## ページネーションで１０件まで表示されること
```
def test_pagination_is_ten(self):
    response = self.client.get(reverse('authors'))
    self.assertEqual(response.status_code, 200)
    self.assertTrue('is_paginated' in response.context)
    self.assertTrue(response.context['is_paginated'] == True)
    self.assertEqual(len(response.context['author_list']), 10)
```
## 最終ページに残り件数が表示されること
```
def test_lists_all_authors(self):
    # Get second page and confirm it has (exactly) remaining 3 items
    response = self.client.get(reverse('authors')+'?page=2')
    self.assertEqual(response.status_code, 200)
    self.assertTrue('is_paginated' in response.context)
    self.assertTrue(response.context['is_paginated'] == True)
    self.assertEqual(len(response.context['author_list']), 3)
```
## アクセス制限の検証
```
def setUp(self):
    # Create two users
    test_user1 = User.objects.create_user(username='testuser1', ...)
    test_user2 = User.objects.create_user(username='testuser2', ...)
    test_user1.save()
    test_user2.save()
    
    # Bookの作成
    # Genreの作成
    # Bookinstanceの作成（ループでuser1, user2を交互に割り当てるなど）
```
## ログインしていない場合のリダイレクト
```
def test_redirect_if_not_logged_in(self):
    response = self.client.get(reverse('my-borrowed'))
    self.assertRedirects(response, '/accounts/login/?next=/catalog/mybooks/')
```
## ログインしている場合のレスポンス
```
def test_logged_in_uses_correct_template(self):
    login = self.client.login(username='testuser1', ...)
    response = self.client.get(reverse('my-borrowed'))
    
    self.assertEqual(str(response.context['user']), 'testuser1')
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'catalog/bookinstance_list_borrowed_user.html')
```

# Testing view with forms
フォームと組み合わせてビューをテスト

```
from catalog.forms import RenewBookForm

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        book_renewal_form = RenewBookForm(request.POST)
        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        book_renewal_form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'book_renewal_form': book_renewal_form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)
```
ちなみに、
```
from django.shortcuts import get_object_or_404
```
です。

続いて `/catalog/tests/test_views.py` に以下の内容を追加。
```
class RenewBookInstancesViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(...)
        test_user2 = User.objects.create_user(...)
        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()
        
        # Create a book（省略）
        # Create genre
        # Create a BookInstance object for test_user1
        # Create a BookInstance object for test_user２
```
続いてテストコード。
```
def test_redirect_if_not_logged_in(self):
    # ログインしていない場合
    self.assertEqual(response.status_code, 302)
    
def test_forbidden_if_logged_in_but_not_correct_permission(self):
    # 更新権限を持たない場合
    self.assertEqual(response.status_code, 403)

def test_logged_in_with_permission_borrowed_book(self):
    # 更新権限を持つ場合、自分が借りた本
    self.assertEqual(response.status_code, 200)

def test_logged_in_with_permission_another_users_borrowed_book(self):
    # 更新権限を持つ場合、他のユーザーが借りた本
    self.assertEqual(response.status_code, 200)

def test_HTTP404_for_invalid_book_if_logged_in(self):
    # 本のUIDが存在しない場合
    self.assertEqual(response.status_code, 404)

def test_uses_correct_template(self):
    # 正しいテンプレートが適用されている
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(
        response, 'catalog/book_renew_librarian.html')

def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
    # 更新予定日が既定の3週間先の日付になっている
    self.assertEqual(response.status_code, 200)
    ...
    self.assertEqual(
        response.context['form'].initial['renewal_date'], 
        date_3_weeks_in_future)

def test_redirects_to_all_borrowed_book_list_on_success(self):
    # 日付の更新が完了すると借りている本の一覧にリダイレクトされること
    self.assertRedirects(response, reverse('all-borrowed'))

def test_form_invalid_renewal_date_past(self):
    # 更新日に過去の日付を指定するとフォームエラーが返ること
    self.assertEqual(response.status_code, 200)
    self.assertFormError(
        response, 
        'form', 
        'renewal_date', 
        'Invalid date - renewal in past')

def test_form_invalid_renewal_date_future(self):
    # 更新日に既定よりも先の日付を指定するとフォームエラーが返ること
    self.assertEqual(response.status_code, 200)
    self.assertFormError(
        response, 
        'form', 
        'renewal_date', 
        'Invalid date - renewal more than 4 weeks ahead')
```
