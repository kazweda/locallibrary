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
