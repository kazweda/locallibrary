# locallibrary
Django tutorial

https://developer.mozilla.org/ja/docs/Learn/Server-side/Django/skeleton_website

```mermaid
graph TD
    A[HTTP\n Request] -->| | B[URLS\n urls.py]
    B -->| Forward request to appropriate view| C[View\n views.py]
    D[Model\n models.py] <-->|read/write\n data| C
    C -->| | E[HTTP Response\n HTML]
    F[Template\n file.html] -->| | C
```

## Source code
[mdn/django-locallibrary-tutorial](https://github.com/mdn/django-locallibrary-tutorial)

## [Testing](Testing.md)
