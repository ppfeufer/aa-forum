# AA Forum<a name="aa-forum"></a>

[![Badge: Version]][aa-forum on pypi]
[![Badge: License]][aa-forum license]
[![Badge: Supported Python Versions]][aa-forum on pypi]
[![Badge: Supported Django Versions]][aa-forum on pypi]
![Badge: pre-commit]
[![Badge: pre-commit.ci status]][pre-commit.ci status]
[![Badge: Code Style: black]][black code formatter documentation]
[![Badge: Support Discord]][support discord]
[![Badge: Automated Tests]][automated tests on github]
[![Badge: Code Coverage]][aa-forum on codecov]
[![Badge: Translation Status]][weblate engage]
[![Badge: Contributor Covenant]][code of conduct]

[![Badge: Buy me a coffee]][ppfeufer on ko-fi]

Simple forum app for [Alliance Auth]

______________________________________________________________________

<!-- mdformat-toc start --slug=github --maxlevel=6 --minlevel=1 -->

- [AA Forum](#aa-forum)
  - [⚠️ Before You Install This Module ⚠️](#%E2%9A%A0%EF%B8%8F-before-you-install-this-module-%E2%9A%A0%EF%B8%8F)
  - [Overview](#overview)
    - [Features](#features)
    - [Screenshots](#screenshots)
      - [Forum Index](#forum-index)
      - [Topic Overview / Board Index](#topic-overview--board-index)
      - [Topic View](#topic-view)
      - [Start New Topic (ckEditor)](#start-new-topic-ckeditor)
      - [Admin View](#admin-view)
  - [Installation](#installation)
    - [Step 1: Install the Package](#step-1-install-the-package)
    - [Step 2: Configure Alliance Auth](#step-2-configure-alliance-auth)
      - [Settings in `/home/allianceserver/myauth/myauth/settings/local.py`](#settings-in-homeallianceservermyauthmyauthsettingslocalpy)
      - [Settings in `/home/allianceserver/myauth/myauth/urls.py`](#settings-in-homeallianceservermyauthmyauthurlspy)
    - [Step 3: Configure Your Webserver](#step-3-configure-your-webserver)
      - [Apache](#apache)
      - [Nginx](#nginx)
    - [Step 4: Finalizing the Installation](#step-4-finalizing-the-installation)
    - [Step 5: Setting up Permissions](#step-5-setting-up-permissions)
  - [Changelog](#changelog)
  - [Translation Status](#translation-status)
  - [Contributing](#contributing)

<!-- mdformat-toc end -->

______________________________________________________________________

## ⚠️ Before You Install This Module ⚠️<a name="%E2%9A%A0%EF%B8%8F-before-you-install-this-module-%E2%9A%A0%EF%B8%8F"></a>

This module needs quite some configuration done before working properly. You need to
modify your Apache/Nginx configuration as well as the global URL config of Alliance
Auth. So please only install if you know what you're doing/feel comfortable making
these kinds of changes. For your own sanity, and mine :-)

## Overview<a name="overview"></a>

### Features<a name="features"></a>

- Simple permission system. Only 2 permissions. ("has_access" and "can_manage")
- Simple administration, no maze to click through to get where you want to go.
- Categories and boards are sortable via drag and drop in the admin view.
- Mass creation of boards with a new category.
- Boards can be restricted to 1 or more groups, boards without restrictions are
  visible for everyone who has access to the forum.
- Announcement boards where only certain users can start topics.
- Child boards (1 Level), which inherit their access restrictions from their parent.
- CKEditor with image upload.
- Unread topics counter as a number on the "Forum" link in the left navigation.
- Optional notifications about new topics in a board via Discord webhooks.
- Forum profile for each user.
- Personal Messages.
  - Optional Discord PM for new personal messages.<br>
    This feature is disabled by default, can be enabled by each user in their forum
    profile. Needs one of the following applications installed:
    - [discordproxy]
    - [AA-Discordbot]

### Screenshots<a name="screenshots"></a>

#### Forum Index<a name="forum-index"></a>

![Screenshot: Forum Index]

#### Topic Overview / Board Index<a name="topic-overview--board-index"></a>

![Screenshot: Topic Overview / Board Index]

#### Topic View<a name="topic-view"></a>

![Screenshot: Topic View]

#### Start New Topic (ckEditor)<a name="start-new-topic-ckeditor"></a>

![Screenshot: Start new Topic]

#### Admin View<a name="admin-view"></a>

![Screenshot: Admin View]

## Installation<a name="installation"></a>

> \[!NOTE\]
>
> **AA Forum needs at least Alliance Auth v4.0.0!**
>
> Please make sure to update your Alliance Auth instance _before_ you install this
> module or update to the latest version, otherwise an update to Alliance Auth will
> be pulled in unsupervised.

**Important**: Please make sure you meet all preconditions before you proceed:

- AA Forum is a plugin for Alliance Auth. If you don't have Alliance Auth running
  already, please install it first before proceeding. (see the official
  [AA installation guide] for details)
- AA Forum needs a couple of changes made to your Webserver and Alliance Auth
  configuration. So make sure you know how to do so. The steps needed will be
  described in this document, but you need to understand what will be changed.

### Step 1: Install the Package<a name="step-1-install-the-package"></a>

Make sure you're in the virtual environment (venv) of your Alliance Auth
installation Then install the latest release directly from PyPi.

```shell
pip install aa-forum
```

### Step 2: Configure Alliance Auth<a name="step-2-configure-alliance-auth"></a>

#### Settings in `/home/allianceserver/myauth/myauth/settings/local.py`<a name="settings-in-homeallianceservermyauthmyauthsettingslocalpy"></a>

This is fairly simple, configure your AA settings (`local.py`) as follows:

```python
# AA Forum
INSTALLED_APPS += [
    "ckeditor",
    "ckeditor_uploader",
    "django_ckeditor_youtube_plugin",
    "aa_forum",  # https://github.com/ppfeufer/aa-forum
]

if "ckeditor" in INSTALLED_APPS:
    # ckEditor
    import ckeditor.configs

    MEDIA_URL = "/media/"
    MEDIA_ROOT = "/var/www/myauth/media/"

    X_FRAME_OPTIONS = "SAMEORIGIN"

    CKEDITOR_UPLOAD_PATH = "uploads/"
    CKEDITOR_RESTRICT_BY_USER = True
    CKEDITOR_ALLOW_NONIMAGE_FILES = False

    # Editor configuration
    #
    # If you already have this from another app, like `aa-bulletin-board`, you don't
    # need to define this again, just add it to the `CKEDITOR_CONFIGS` dict, see below
    #
    # You can extend and change this to your needs
    # Some of the options are commented out, feel free to play around with them
    ckeditor_default_config = {
        "width": "100%",
        "height": "45vh",
        "youtube_responsive": True,
        "youtube_privacy": True,
        "youtube_related": False,
        "youtube_width": 1920,
        "youtube_height": 1080,
        "extraPlugins": ",".join(
            [
                "uploadimage",
                # "div",
                "autolink",
                # "autoembed",
                # "embedsemantic",
                "clipboard",
                "elementspath",
                # "codesnippet",
                "youtube",
            ]
        ),
        "toolbar": [
            {
                "name": "styles",
                "items": [
                    "Styles",
                    "Format",
                    # "Font",
                    # "FontSize",
                ],
            },
            {
                "name": "basicstyles",
                "items": [
                    "Bold",
                    "Italic",
                    "Underline",
                    "Strike",
                    # "Subscript",
                    # "Superscript",
                    # "-",
                    # "RemoveFormat",
                ],
            },
            {
                "name": "clipboard",
                "items": [
                    # "Cut",
                    # "Copy",
                    # "Paste",
                    # "PasteText",
                    # "PasteFromWord",
                    # "-",
                    "Undo",
                    "Redo",
                ],
            },
            {
                "name": "links",
                "items": [
                    "Link",
                    "Unlink",
                    "Anchor",
                ],
            },
            {
                "name": "insert",
                "items": [
                    "Image",
                    "Youtube",
                    "Table",
                    "HorizontalRule",
                    "Smiley",
                    "SpecialChar",
                    # "PageBreak",
                    # "Iframe",
                ],
            },
            {
                "name": "colors",
                "items": [
                    "TextColor",
                    "BGColor",
                ],
            },
            {
                "name": "document",
                "items": [
                    # "Source",
                    # "-",
                    # "Save",
                    # "NewPage",
                    # "Preview",
                    # "Print",
                    # "-",
                    # "Templates",
                ],
            },
        ],
    }

    # Add the external YouTube plugin
    aa_forum__external_plugin_resources = [
        (
            "youtube",
            "/static/ckeditor/ckeditor/plugins/youtube/",
            "plugin.min.js",
        )
    ]

    # Put it all together
    CKEDITOR_CONFIGS = {
        "default": ckeditor.configs.DEFAULT_CONFIG,
        "aa_forum": ckeditor_default_config,
    }

    CKEDITOR_CONFIGS["aa_forum"][
        "external_plugin_resources"
    ] = aa_forum__external_plugin_resources
```

#### Settings in `/home/allianceserver/myauth/myauth/urls.py`<a name="settings-in-homeallianceservermyauthmyauthurlspy"></a>

Now let's move on to editing the global URL configuration of Alliance Auth. To do so,
you need to open `/home/allianceserver/myauth/myauth/urls.py` and change the
following block right before the `handler` definitions:

```python
# URL configuration for cKeditor
from django.apps import apps

if apps.is_installed("ckeditor"):
    # Django
    from django.contrib.auth.decorators import login_required
    from django.views.decorators.cache import never_cache

    # ckEditor
    from ckeditor_uploader import views as ckeditor_views

    urlpatterns = [
        re_path(
            r"^upload/", login_required(ckeditor_views.upload), name="ckeditor_upload"
        ),
        re_path(
            r"^browse/",
            never_cache(login_required(ckeditor_views.browse)),
            name="ckeditor_browse",
        ),
    ] + urlpatterns
```

After this, your `urls.py` should look similar to this:

```python
from django.urls import include, re_path

from allianceauth import urls

# Alliance auth urls
urlpatterns = [
    re_path(r"", include(urls)),
]

# URL configuration for cKeditor
from django.apps import apps

if apps.is_installed("ckeditor"):
    # Django
    from django.contrib.auth.decorators import login_required
    from django.views.decorators.cache import never_cache

    # ckEditor
    from ckeditor_uploader import views as ckeditor_views

    urlpatterns = [
        re_path(
            r"^upload/", login_required(ckeditor_views.upload), name="ckeditor_upload"
        ),
        re_path(
            r"^browse/",
            never_cache(login_required(ckeditor_views.browse)),
            name="ckeditor_browse",
        ),
    ] + urlpatterns

handler500 = "allianceauth.views.Generic500Redirect"
handler404 = "allianceauth.views.Generic404Redirect"
handler403 = "allianceauth.views.Generic403Redirect"
handler400 = "allianceauth.views.Generic400Redirect"
```

### Step 3: Configure Your Webserver<a name="step-3-configure-your-webserver"></a>

Your webserver needs to know from where to serve the uploaded images, of course, so we
have to tell it.

#### Apache<a name="apache"></a>

In your vhost configuration, you have a line `ProxyPassMatch ^/static !`, which tells
the server where to find all the static files. We're adding a similar line for the
media, right below that one.

Add the following right below the static proxy match:

```apache
ProxyPassMatch ^/media !
```

Now we also need to let the server know where to find the media directory we just
configured the proxy for. To do so, add a new Alias to your configuration. This can
be done right below the already existing Alias for `/static`:

```apache
Alias "/media" "/var/www/myauth/media/"
```

At last, a "Directory" rule is needed as well. Add the following code below the already
existing Directory rule for the static files:

```apache
<Directory "/var/www/myauth/media/">
    Require all granted
</Directory>
```

So the whole block should now look like this:

```apache
ProxyPassMatch ^/static !
ProxyPassMatch ^/media !  # *** NEW proxy rule
ProxyPass / http://127.0.0.1:8000/
ProxyPassReverse / http://127.0.0.1:8000/
ProxyPreserveHost On

Alias "/static" "/var/www/myauth/static/"
Alias "/media" "/var/www/myauth/media/"

<Directory "/var/www/myauth/static/">
    Require all granted
</Directory>

<Directory "/var/www/myauth/media/">
    Require all granted
</Directory>
```

Restart your Apache webserver.

#### Nginx<a name="nginx"></a>

In order to let Nginx know where to find the uploaded files, you need to add a new
location rule to the configuration. Add the following right below the definition for
your "static" location.

```nginx
location /media {
    alias /var/www/myauth/media;
    autoindex off;
}
```

Restart your Nginx webserver.

### Step 4: Finalizing the Installation<a name="step-4-finalizing-the-installation"></a>

Run static files collection and migrations

```shell
python manage.py collectstatic
python manage.py migrate
```

Restart your supervisor services for Auth

### Step 5: Setting up Permissions<a name="step-5-setting-up-permissions"></a>

Now it's time to set up access permissions for your new module. You can do so in
your admin backend.

| ID             | Description                                                      | Notes                                                                                                                                                                                                                                                                                                                                             |
| :------------- | :--------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `basic_access` | Can access the AA-Forum module                                   | Grants access to the forum                                                                                                                                                                                                                                                                                                                        |
| `manage_forum` | Can manage the AA-Forum module (Categories, topics and messages) | Users with this permission can create, edit and delete boards and categories in the "Administration" view. They can also modify and delete messages and topics in the "Forum" view. **Users with this permission are not bound by group restrictions and have access to all boards and topics, so choose wisely who is getting this permission.** |

## Changelog<a name="changelog"></a>

See [CHANGELOG.md]

## Translation Status<a name="translation-status"></a>

[![Translation status](https://weblate.ppfeufer.de/widget/alliance-auth-apps/aa-forum/multi-auto.svg)](https://weblate.ppfeufer.de/engage/alliance-auth-apps/)

Do you want to help translate this app into your language or improve the existing
translation? - [Join our team of translators][weblate engage]!

## Contributing<a name="contributing"></a>

Do you want to contribute to this project? That's cool!

Please make sure to read the [Contribution Guidelines].
(I promise, it's not much, just some basics)

<!-- Inline Links -->

[aa installation guide]: https://allianceauth.readthedocs.io/en/latest/installation/allianceauth.html
[aa-discordbot]: https://github.com/pvyParts/allianceauth-discordbot "AA-Discordbot"
[aa-forum license]: https://github.com/ppfeufer/aa-forum/blob/master/LICENSE
[aa-forum on codecov]: https://codecov.io/gh/ppfeufer/aa-forum
[aa-forum on pypi]: https://pypi.org/project/aa-forum/
[alliance auth]: https://gitlab.com/allianceauth/allianceauth
[automated tests on github]: https://github.com/ppfeufer/aa-forum/actions/workflows/automated-checks.yml
[badge: automated tests]: https://github.com/ppfeufer/aa-forum/actions/workflows/automated-checks.yml/badge.svg "Automated Tests"
[badge: buy me a coffee]: https://ko-fi.com/img/githubbutton_sm.svg "Buy me a coffee"
[badge: code coverage]: https://codecov.io/gh/ppfeufer/aa-forum/branch/master/graph/badge.svg "Code Coverage"
[badge: code style: black]: https://img.shields.io/badge/code%20style-black-000000.svg "Code Style: black"
[badge: contributor covenant]: https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg "Contributor Covenant"
[badge: license]: https://img.shields.io/github/license/ppfeufer/aa-forum "License"
[badge: pre-commit]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white "pre-commit"
[badge: pre-commit.ci status]: https://results.pre-commit.ci/badge/github/ppfeufer/aa-forum/master.svg "pre-commit.ci status"
[badge: support discord]: https://img.shields.io/discord/790364535294132234?label=discord "Support Discord"
[badge: supported django versions]: https://img.shields.io/pypi/djversions/aa-forum?label=django "Supported Django Versions"
[badge: supported python versions]: https://img.shields.io/pypi/pyversions/aa-forum "Supported Python Versions"
[badge: translation status]: https://weblate.ppfeufer.de/widget/alliance-auth-apps/aa-forum/svg-badge.svg "Translation Status"
[badge: version]: https://img.shields.io/pypi/v/aa-forum?label=release "Version"
[black code formatter documentation]: http://black.readthedocs.io/en/latest/
[changelog.md]: https://github.com/ppfeufer/aa-forum/blob/master/CHANGELOG.md
[code of conduct]: https://github.com/ppfeufer/aa-forum/blob/master/CODE_OF_CONDUCT.md
[contribution guidelines]: https://github.com/ppfeufer/aa-forum/blob/master/CONTRIBUTING.md
[discordproxy]: https://gitlab.com/ErikKalkoken/discordproxy
[ppfeufer on ko-fi]: https://ko-fi.com/N4N8CL1BY
[pre-commit.ci status]: https://results.pre-commit.ci/latest/github/ppfeufer/aa-forum/master "pre-commit.ci"
[screenshot: admin view]: https://raw.githubusercontent.com/ppfeufer/aa-forum/master/docs/images/admin-view.jpg "Admin View"
[screenshot: forum index]: https://raw.githubusercontent.com/ppfeufer/aa-forum/master/docs/images/forum-index.jpg "Forum Index"
[screenshot: start new topic]: https://raw.githubusercontent.com/ppfeufer/aa-forum/master/docs/images/start-new-topic.jpg "Start new Topic (ckEditor)"
[screenshot: topic overview / board index]: https://raw.githubusercontent.com/ppfeufer/aa-forum/master/docs/images/topic-overview.jpg "Topic Overview / Board Index"
[screenshot: topic view]: https://raw.githubusercontent.com/ppfeufer/aa-forum/master/docs/images/topic-view.jpg "Topic View"
[support discord]: https://discord.gg/zmh52wnfvM
[weblate engage]: https://weblate.ppfeufer.de/engage/alliance-auth-apps/ "Weblate Translations"
