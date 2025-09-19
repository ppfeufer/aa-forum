# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog] and this project adheres to [Semantic Versioning].

<!--
GitHub MD Syntax:
https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax

Highlighting:
https://docs.github.com/assets/cb-41128/mw-1440/images/help/writing/alerts-rendered.webp

> [!NOTE]
> Highlights information that users should take into account, even when skimming.

> [!TIP]
> Optional information to help a user be more successful.

> [!IMPORTANT]
> Crucial information necessary for users to succeed.

> [!WARNING]
> Urgent info that needs immediate user attention to avoid problems.

> [!CAUTION]
> Advised about risks or negative outcomes of certain actions.
-->

## [In Development] - Unreleased

<!--
Section Order:

### Added
### Fixed
### Changed
### Deprecated
### Removed
### Security
-->

<!-- Your changes go here -->

### Changed

- Switch to Terser for JavaScript compression

## [2.13.0] - 2025-08-14

### Changed

- SVG sprite optimizations
- Use AA framework JS functions
- Minimum requirements
  - Alliance Auth >= 4.9.0

## [2.12.1] - 2025-08-05

### Changed

- Translations updated

## [2.12.0] - 2025-06-03

### Changed

- Translations updated

### Removed

- Cache breaker for static files. Doesn't work as expected with `django-sri`.

## [2.11.0] - 2025-05-05

### Changed

- Use `text-bg-*` instead of `bg-*` to make use of Bootstraps native color contrast detection
- Backend App renamed (AA Forum > Forum)
- JavaScript refactored
- Translations updated

## [2.10.2] - 2025-04-09

### Added

- Type hinting for managers
- Bottom margin in mobile navigation

### Removed

- Right margin from search field

## [2.10.1] - 2025-03-06

### Changed

- Templatetag code improved
- Debug check moved to function
- Check for empty messages improved
- Translations updated

## [2.10.0] - 2025-01-30

### Added

- Proper user agent for `dhooks-lite`

### Fixed

- New message badges in forum view
- Missing `li` tags

### Changed

- Some constants reworked
- Set user agent according to MDN guidelines
- Use enum for Discord embed colors
- Use `django-sri` for sri hashes
- Better JS settings merge
- Minimum requirements
  - Alliance Auth >= 4.6.0

## [2.9.2] - 2024-12-09

### Added

- Testing for Python 3.13

### Changed

- Sumoselect JS updated to the latest version

## [2.9.1] - 2024-12-06

### Added

- Optional settings for Discord Proxy

## [2.9.0] - 2024-11-14

### Fixed

- Re-enable form validation for CKEditor fields, where needed

### Changed

- Dependency updates
  - `django-ckeditor-5`>=0.2.15

## [2.8.1] - 2024-10-13

### Changed

- Improve oEmbed handling
- Improve internal forms handling
- URL config modularized
- Dependency updates
  - `django-ckeditor-5`>=0.2.14 (Fixing #219)

Remember to add the following to your `local.py`, so your users can upload files:

```python
CKEDITOR_5_FILE_UPLOAD_PERMISSION = (
    "authenticated"  # Possible values: "staff", "authenticated", "any"
)
```

## [2.8.0] - 2024-09-19

### Changed

- Switch to `django-solo` to provide the singleton for the settings model, instead of the custom implementation

## [2.7.0] - 2024-09-16

### Changed

- Dependencies updated
  - `allianceauth`>=4.3.1
- Lingua codes updated to match Alliance Auth v4.3.1

## [2.6.0] - 2024-09-09

### Changed

- The minimum required AA version is now 4.3.0
- Fill the SVG icons via CSS instead of using the `fill` attribute. This allows for
  easier theming and better compatibility with darker themes
- Japanese translation improved

## [2.5.0] - 2024-07-27

### Added

- Prepared Czech translation for when Alliance Auth supports it

### Changed

- Japanese translation improved

## [2.4.1] - 2024-07-15

### Fixed

- Dependency to `allianceauth`

## [2.4.0] - 2024-07-15

### Fixed

- Dashboard widget Bootstrap classes

### Changed

- Russian translation updated

### Removed

- Support for Python 3.8 and Python 3.9
- Common English word from the French stopwords list

## [2.3.1] - 2024-06-03

### Changed

- Chinese translation updated
- French translation updated
- German translation updated

## [2.3.0] - 2024-05-27

### Added

- Missing tooltip for `topic.has_unread_messages` marker

### Changed

- The minimum required AA version is now 4.1.0
- Using the AA framework template for the widget title

## [2.2.1] - 2024-05-16

### Changed

- Translations updated

## [2.2.0] - 2024-05-06

### Fixed

- Removed wrongfully added integrity hash from CKEditor CSS, since it's not under our
  control. Now a newer version of CKEditor will load again properly.

### Changed

- Using stopword lists downloaded from https://github.com/stopwords-iso to improve
  search results
- Require the latest version of `django-ckeditor-5` (v0.2.13)

## [2.1.1] - 2024-04-28

### Added

- Integrity hashes to our JS and CSS files to prevent tampering

### Fixed

- CKEditor image alignment

### Changed

- `Board.user_can_start_topic()` simplified to not have a variable with the same name
  as the method
- Dashboard widget JavaScript modernised

## [2.1.0] - 2024-04-21

### Added

- Bootstrap tooltips wherever it makes sense
- Close and reopen topics with a reply.
  - OPs can now close their topics with a reply.
  - Forum admins can close any topic and reopen closed topics when needed.

### Changed

- Translations updated

## [2.0.0] - 2024-03-16

> [!NOTE]
>
> **This version needs at least Alliance Auth v4.0.0!**
>
> Please make sure to update your Alliance Auth instance before
> you install this version, otherwise an update to Alliance Auth will
> be pulled in unsupervised.

> [!IMPORTANT]
>
> With this version, we switched to a new WYSIWYG editor.
> Please make sure to read the update information
> to make sure your configuration is up to date.

### Added

- Support for Alliance Auth v4.x
- Support for Django 4.0
- Native lazy loading support for images
- Unread topics dashboard widget

### Fixed

- Margins
- A bug where the topic of unread messages was displayed multiple times in the unread messages view when there was more than one unread message in the topic

### Changed

- Minimum requirements
  - `allianceauth`>=4.0.0
- Switched from CKEditor 4 to CKEditor 5 (Configuration update necessary, see below)
- Set `user` field to read-only in `ModelAdmin` for `UserProfile` to prevent accidental changes

### Removed

- Support for Alliance Auth v3.x

### Update Information

This version introduces a new WYSIWYG editor. Some configuration changes are necessary.

#### Settings in `/home/allianceserver/myauth/myauth/settings/local.py`

Please make sure to update your `local.py` with the following configuration.\
Add `"django_ckeditor_5",` to `INSTALLED_APPS` and remove the following apps
if they are present:

```python
"ckeditor",
"ckeditor_uploader",
"django_ckeditor_youtube_plugin",
```

Remove the old CKEditor configuration and replace it with the following:

```python
# Django CKEditor 5 Configuration
if "django_ckeditor_5" in INSTALLED_APPS:
    MEDIA_URL = "/media/uploads/"
    MEDIA_ROOT = "/var/www/myauth/media/uploads"

    customColorPalette = [
        {"color": "hsl(4, 90%, 58%)", "label": "Red"},
        {"color": "hsl(340, 82%, 52%)", "label": "Pink"},
        {"color": "hsl(291, 64%, 42%)", "label": "Purple"},
        {"color": "hsl(262, 52%, 47%)", "label": "Deep Purple"},
        {"color": "hsl(231, 48%, 48%)", "label": "Indigo"},
        {"color": "hsl(207, 90%, 54%)", "label": "Blue"},
    ]

    CKEDITOR_5_CONFIGS = {
        "default": {
            "toolbar": [
                "heading",
                "|",
                "bold",
                "italic",
                "link",
                "bulletedList",
                "numberedList",
                "blockQuote",
            ],
        },
        "extends": {
            "blockToolbar": [
                "paragraph",
                "heading1",
                "heading2",
                "heading3",
                "|",
                "bulletedList",
                "numberedList",
                "|",
                "blockQuote",
            ],
            "toolbar": [
                "heading",
                "|",
                "outdent",
                "indent",
                "|",
                "bold",
                "italic",
                "link",
                "underline",
                "strikethrough",
                "subscript",
                "superscript",
                "highlight",
                "|",
                "insertImage",
                "mediaEmbed",
                "|",
                "bulletedList",
                "numberedList",
                "todoList",
                "insertTable",
                "|",
                "blockQuote",
                "codeBlock",
                "|",
                "fontSize",
                "fontFamily",
                "fontColor",
                "fontBackgroundColor",
                "removeFormat",
                "|",
                "sourceEditing",
            ],
            "image": {
                "toolbar": [
                    "imageTextAlternative",
                    "|",
                    "imageStyle:alignLeft",
                    "imageStyle:alignRight",
                    "imageStyle:alignCenter",
                    "imageStyle:side",
                    "|",
                ],
                "styles": [
                    "full",
                    "side",
                    "alignLeft",
                    "alignRight",
                    "alignCenter",
                ],
            },
            "table": {
                "contentToolbar": [
                    "tableColumn",
                    "tableRow",
                    "mergeTableCells",
                    "tableProperties",
                    "tableCellProperties",
                ],
                "tableProperties": {
                    "borderColors": customColorPalette,
                    "backgroundColors": customColorPalette,
                },
                "tableCellProperties": {
                    "borderColors": customColorPalette,
                    "backgroundColors": customColorPalette,
                },
            },
            "heading": {
                "options": [
                    {
                        "model": "paragraph",
                        "title": "Paragraph",
                        "class": "ck-heading_paragraph",
                    },
                    {
                        "model": "heading1",
                        "view": "h1",
                        "title": "Heading 1",
                        "class": "ck-heading_heading1",
                    },
                    {
                        "model": "heading2",
                        "view": "h2",
                        "title": "Heading 2",
                        "class": "ck-heading_heading2",
                    },
                    {
                        "model": "heading3",
                        "view": "h3",
                        "title": "Heading 3",
                        "class": "ck-heading_heading3",
                    },
                ]
            },
        },
        "list": {
            "properties": {
                "styles": "true",
                "startIndex": "true",
                "reversed": "true",
            }
        },
    }
```

#### Settings in `/home/allianceserver/myauth/myauth/urls.py`

Also, make sure to update your `urls.py` with the following and remove the old
CKEditor URL configuration if it's present:

```python
from django.apps import apps  # Only if not already imported earlier
from django.conf import settings  # Only if not already imported earlier
from django.conf.urls.static import static  # Only if not already imported earlier
from django.urls import path  # Only if not already imported earlier

# If django_ckeditor_5 is loaded
if apps.is_installed("django_ckeditor_5"):
    # URL configuration for CKEditor 5
    urlpatterns = (
        [
            path(
                "ckeditor5/",
                include("django_ckeditor_5.urls"),
                name="ck_editor_5_upload_file",
            ),
        ]
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        + urlpatterns
    )
```

## [2.0.0-beta.3] - 2024-03-08

> [!NOTE]
>
> **This version needs at least Alliance Auth v4.0.0b2!**
>
> Please make sure to update your Alliance Auth instance before
> you install this version, otherwise an update to Alliance Auth will
> be pulled in unsupervised.

> [!IMPORTANT]
>
> New migrations have been consolidated.
>
> Please make sure to run the following command before you update to this version:
>
> ```shell
> python manage.py migrate aa_forum 0016
> ```

### Added

- Unread topics dashboard widget

### Changed

- New migrations consolidated
- Behavior for the "Administration" menu has been changed to follow the default Bootstrap
  navigation behavior. Meaning, it will no longer open on hover, you have to click
  it now.

## [2.0.0-beta.2] - 2024-03-03

> [!NOTE]
>
> **This version needs at least Alliance Auth v4.0.0b2!**
>
> Please make sure to update your Alliance Auth instance before
> you install this version, otherwise an update to Alliance Auth will
> be pulled in unsupervised.

### Fixed

- Upload directory for CKEditor (see [README.md] for details)
- New message badge appearance
- Margins
- A bug where the topic of unread messages was displayed multiple times in the
  unread messages view when there was more than one unread message in the topic

### Changed

- Set `user` field to read-only in `ModelAdmin` for `UserProfile` to prevent
  accidental changes

## [2.0.0-beta.1] - 2024-02-18

> [!NOTE]
>
> **This version needs at least Alliance Auth v4.0.0b1!**
>
> Please make sure to update your Alliance Auth instance before
> you install this version, otherwise an update to Alliance Auth will
> be pulled in unsupervised.

> [!IMPORTANT]
>
> With this version, we switched to a new WYSIWYG editor.
> Please make sure to read the update information
> to make sure your configuration is up to date.

### Added

- Support for Alliance Auth v4.x
- Support for Django 4.0
- Native lazy loading support for images

### Changed

- Minimum requirements
  - `allianceauth`>=4.0.0
- Switched from CKEditor 4 to CKEditor 5 (Configuration update necessary, see below)

### Removed

- Support for Alliance Auth v3.x

### Update Information

This version introduces a new WYSIWYG editor. Some configuration changes are necessary.

#### Settings in `/home/allianceserver/myauth/myauth/settings/local.py`

Please make sure to update your `local.py` with the following configuration.\
Add `"django_ckeditor_5",` to `INSTALLED_APPS` and remove the following apps
if they are present:

```python
"ckeditor",
"ckeditor_uploader",
"django_ckeditor_youtube_plugin",
```

Remove the old CKEditor configuration and replace it with the following:

```python
# Django CKEditor 5 Configuration
if "django_ckeditor_5" in INSTALLED_APPS:
    MEDIA_URL = "/media/uploads/"
    MEDIA_ROOT = "/var/www/myauth/media/uploads"

    customColorPalette = [
        {"color": "hsl(4, 90%, 58%)", "label": "Red"},
        {"color": "hsl(340, 82%, 52%)", "label": "Pink"},
        {"color": "hsl(291, 64%, 42%)", "label": "Purple"},
        {"color": "hsl(262, 52%, 47%)", "label": "Deep Purple"},
        {"color": "hsl(231, 48%, 48%)", "label": "Indigo"},
        {"color": "hsl(207, 90%, 54%)", "label": "Blue"},
    ]

    CKEDITOR_5_CONFIGS = {
        "default": {
            "toolbar": [
                "heading",
                "|",
                "bold",
                "italic",
                "link",
                "bulletedList",
                "numberedList",
                "blockQuote",
            ],
        },
        "extends": {
            "blockToolbar": [
                "paragraph",
                "heading1",
                "heading2",
                "heading3",
                "|",
                "bulletedList",
                "numberedList",
                "|",
                "blockQuote",
            ],
            "toolbar": [
                "heading",
                "|",
                "outdent",
                "indent",
                "|",
                "bold",
                "italic",
                "link",
                "underline",
                "strikethrough",
                "subscript",
                "superscript",
                "highlight",
                "|",
                "insertImage",
                "mediaEmbed",
                "|",
                "bulletedList",
                "numberedList",
                "todoList",
                "insertTable",
                "|",
                "blockQuote",
                "codeBlock",
                "|",
                "fontSize",
                "fontFamily",
                "fontColor",
                "fontBackgroundColor",
                "removeFormat",
                "|",
                "sourceEditing",
            ],
            "image": {
                "toolbar": [
                    "imageTextAlternative",
                    "|",
                    "imageStyle:alignLeft",
                    "imageStyle:alignRight",
                    "imageStyle:alignCenter",
                    "imageStyle:side",
                    "|",
                ],
                "styles": [
                    "full",
                    "side",
                    "alignLeft",
                    "alignRight",
                    "alignCenter",
                ],
            },
            "table": {
                "contentToolbar": [
                    "tableColumn",
                    "tableRow",
                    "mergeTableCells",
                    "tableProperties",
                    "tableCellProperties",
                ],
                "tableProperties": {
                    "borderColors": customColorPalette,
                    "backgroundColors": customColorPalette,
                },
                "tableCellProperties": {
                    "borderColors": customColorPalette,
                    "backgroundColors": customColorPalette,
                },
            },
            "heading": {
                "options": [
                    {
                        "model": "paragraph",
                        "title": "Paragraph",
                        "class": "ck-heading_paragraph",
                    },
                    {
                        "model": "heading1",
                        "view": "h1",
                        "title": "Heading 1",
                        "class": "ck-heading_heading1",
                    },
                    {
                        "model": "heading2",
                        "view": "h2",
                        "title": "Heading 2",
                        "class": "ck-heading_heading2",
                    },
                    {
                        "model": "heading3",
                        "view": "h3",
                        "title": "Heading 3",
                        "class": "ck-heading_heading3",
                    },
                ]
            },
        },
        "list": {
            "properties": {
                "styles": "true",
                "startIndex": "true",
                "reversed": "true",
            }
        },
    }
```

#### Settings in `/home/allianceserver/myauth/myauth/urls.py`

Also, make sure to update your `urls.py` with the following and remove the old
CKEditor URL configuration if it's present:

```python
from django.apps import apps  # Only if not already imported earlier
from django.conf import settings  # Only if not already imported earlier
from django.conf.urls.static import static  # Only if not already imported earlier
from django.urls import path  # Only if not already imported earlier

# If django_ckeditor_5 is loaded
if apps.is_installed("django_ckeditor_5"):
    # URL configuration for CKEditor 5
    urlpatterns = (
        [
            path(
                "ckeditor5/",
                include("django_ckeditor_5.urls"),
                name="ck_editor_5_upload_file",
            ),
        ]
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        + urlpatterns
    )
```

## [1.19.5] - 2023-11-15

> [!NOTE]
>
> **This is the last version compatible with Alliance Auth v3.**

### Fixed

- Pluralisation in a template string
- Quotation marks in some strings
- Stylelint issue: Expected shorthand property "place-content"

### Changed

- Moved topic creation from the view to the model. This will make it possible for
  3rd-Party apps to create topics in a defined board.
- Translations updated

## [1.19.4] - 2023-09-26

### Fixed

- Pylint issues
- Capitalization for translatable strings

### Changed

- Use keyword arguments wherever possible
- Translations updated
- Test suite updated

## [1.19.3] - 2023-09-02

### Changed

- Korean translation improved
- Spanish translation improved

## [1.19.2] - 2023-08-13

### Fixed

- Bootstrap CSS fix

## [1.19.1] - 2023-07-30

### Added

- Footer to promote help with the app translation

### Changed

- JavaScript modernised
- German translation improved
- Ukrainian translation improved

## [1.19.0] - 2023-04-24

### Changed

- Russian translation updated
- Moved the build process to PEP 621 / pyproject.toml

## [1.18.0] - 2023-04-16

### Added

- Russian translation

### Fixed

- Warning message in a modal window

## [1.17.2] - 2023-04-13

### Changed

- German translation updated

## [1.17.1] - 2023-01-06

### Added

- Pagination helper to reduce code duplication
- German translation

### Changed

- Use `models.TextChoices` for `Setting` fields

## [1.17.0] - 2022-10-11

### Added

- New Feature: Support for [AA Time Zones] time zone conversions of message
  date/time information ([#125])
  ![New Feature: Support for aa-timezones]

### Changed

- Switched to `SITE_URL` instead of `{{ request.scheme }}://{{ request.get_host }}`
- Minimum requirements
  - `allianceauth`>=3.2.0

## [1.16.0] - 2022-09-18

### Added

- New Feature: Discord PM for new personal messages<br>
  This feature is disabled by default but can be enabled by each user in their forum
  profile. Needs one of the following applications installed:
  - [discordproxy]
  - [AA-Discordbot]

## [1.15.2] - 2022-09-14

### Fixed

- Detection of the first message in the message loop in the topic and search result view
- Highlighting search terms breaks image and link tags in the search result view

## [1.15.1] - 2022-09-10

### Added

- Positional arguments to URL patterns

### Changed

- System messages and log messages improved

## [1.15.0] - 2022-09-01

### Fixed

- Missing transition added for hover state on personal messages

### Changed

- Minimum requirements
  - `allianceauth-app-utils`>=1.14.2
  - `django-ckeditor`>=6.5.0

### Removed

- Bundled YouTube plugin for CKEditor in favour of `django-ckeditor-youtube-plugin`
  - Apply the following changes in your `local.py`:
    - Add `"django_ckeditor_youtube_plugin",` to `INSTALLED_APPS`

    - Search for the line:

      ```python
      "/static/aa_forum/ckeditor/plugins/youtube/"
      ```

      And replace it with:

      ```python
      "/static/ckeditor/ckeditor/plugins/youtube/"
      ```

## [1.14.0] - 2022-08-31

### Fixed

- HTML syntax in `message-author` template
- "Message modified" info should be before the user's signature

### Added

- New Feature: Personal Messages

### Change

- Spacing for moderation icons
- Automated tests set to use MySQL instead of SQLite to test against:
  - mysql:5.7
  - mysql:8.0
  - mariadb:10.3
  - mariadb:10.4
  - mariadb:10.5
  - mariadb:10.6
  - mariadb:10.7
  - mariadb:10.8
  - mariadb:10.9

## [1.13.0] - 2022-08-26

### Fixed

- Some `<br>` tags that slipped through the cracks removed

### Added

- User Profile
- User's maximum signature length to global forum settings
- Forum settings made available to forum administrators

## [1.12.0] - 2022-08-25

### Fixed

- Top margin of the forum navigation (`<br>` is not for styling ...)

### Changed

- Better setting names
- Setting constants moved to their model
- Show pagination only when there is more than 1 page
- Replaced all icons that were image files with an SVG sprite to reduce the number of
  HTTP requests to the web server.
- Logic in image detection for posts to Discord to "First image to verify"
- Moved search term delimiters to variables
- Some success messages have been improved

## [1.11.0] - 2022-08-24

### Added

- Default forum settings to the admin backend
- `related_name` to foreign keys that were missing them

### Changed

- `Setting` model is now a singleton to prevent multiple settings of the same type

## [1.10.0] - 2022-08-03

### Fixed

- HTML syntax (missing mandatory label tag in global search form added)
- CSS classes in forms

### Added

- "Required Fields" hint to the forms that were missing it

### Changed

- "New Category" form in the admin page visually enhanced
- Contribution guidelines updated
- CSS modernized
- App CSS and JS moved to bundled HTML templates
- Minimum requirements:
  - Python >= 3.8
  - Alliance Auth >= 2.15.1
  - Django CKEditor >= 6.4.2

### Removed

- Unused template tags
- Tests for Alliance Auth Beta
- Deprecated `type` parameter from `script` tags
- Deprecated `type` parameter from `style` tags

## [1.9.0] - 2022-07-11

### Changed

- Package discovery for setuptools
- SumoSelect library moved to its own bundled templates
- Minimum Requirement:
  - Alliance Auth >= 2.14.0

## [1.8.1] - 2022-06-26

### Fixed

- A CSS class in an image HTML tag
- Return a dummy ID when the user is not in an alliance
- No default alliance for test fake user

### Added

- Image sizes to the character portrait image HTML tags
- Error message when submitting an invalid form on topic creation
- Better error messages for topic reply errors

### Changed

- Templates cleaned up

## [1.8.0] - 2022-04-14

### Added

- New Feature: Announcement Boards

  ![New Feature: Announcement Boards]

  - Boards marked as "Announcement Boards" have restrictions on who can start a topic
    in them. This is the already known group restriction function that is already
    used to restrict access to boards in general
  - Users with access to an announcement board still can discuss the topic itself
  - To start a topic, a user needs to be in (at least) one of the defined groups that
    are allowed to start topics
  - If no groups are defined that are allowed to start topics in the announcement
    board, only users with the `manage_forum` permission (Forum Admins) can start topics
  - These settings will not be inherited in child boards

## [1.7.0] - 2022-03-02

### Added

- Test suite for AA 3.x and Django 4

### Changed

- Switched to `setup.cfg` as config file, since `setup.py` is deprecated now

### Removed

- Deprecated settings

## [1.6.0] - 2022-02-28

### Fixed

- Compatibility Fixes (AA 3.x / Django 4):
  - ImportError: cannot import name 'ugettext_lazy' from 'django.utils.translation'
  - URL config in README updated to work with Django 4. **Please make sure to update
    your configuration accordingly!**

## [1.5.1] - 2022-01-26

### Fixed

- Escaped HTML entities in webhook messages, so that this »`That&#39;s`« doesn't
  happen anymore

## [1.5.0] - 2022-01-24

### Added

- Option: Use this Discord Webhook for replies as well? (This is a checkbox in the
  board settings. When checked, the provided Discord webhook will also be used to
  send a message for every reply in this board to Discord. Choose wisely!)

  ![Admin Board Options]

### Changed

- Webhook handling changed to dhooks-lite, so we can make our Discord messages nicer

## [1.4.3] - 2022-01-24

### Fixed

- `NoReverseMatch` error when slugs for a category, board or topic that are generated
  from the name/subject ended up being empty when only entered special chars like
  "@#$%" as name/subject

## [1.4.2] - 2022-01-23

### Fixed

- Deleting the last topic of a child board results in a `NoReverseMatch` error on
  the index page (Thanks @ErikKalkoken)

### Changed

- Refactoring of logic for updating the first and last message on board and topic
  (Thanks @ErikKalkoken)
- Demoted `Board.update_last_message()` and `Topic.update_last_message()` to private
  methods. Those should no longer be called from outside the module, because they're called implicitly by `save()` and `delete()` when needed. Except for bulk
  methods, where e.g. `save()` is not called automatically. Test now also no longer
  test this method directly. (Thanks @ErikKalkoken)

## [1.4.1] - 2022-01-19

### Changed

- JavaScript: Some `let` vs. `const` slipped through the cracks and now have been fixed

## [1.4.0] - 2022-01-12

### Added

- Tests for Python 3.11

### Fixed

- Some JS fixes
  - Removed unused parameters and variables
  - Changed `let` to `const` where appropriate
  - Set `containment` option to category drag and drop

## [1.3.0] - 2021-12-28

### Added

- Tests for model names

### Changed

- Now using jQuery UI provided by Alliance Auth
- Minimum dependencies:
  - Alliance Auth>=2.9.4

### Fixed

- Posts on a child boards weren't considered for possibly being the latest post (#78)

## [1.2.1] - 2021-12-01

### Changed

- Model signals moved to their own file

### Fixed

- Discord webhook configuration for child boards

## [1.2.0] - 2021-11-30

### Changed

- Minimum requirements
  - Python 3.7
  - Alliance Auth v2.9.3
  - Django ckEditor v6.2.0
  - Alliance Auth App Utils v1.8.2
  - Unidecode v1.3.2

## [1.1.3] - 2021-10-31

### Changed

- Minimum version for `allianceauth-app-utils` set to 1.8.1

## [1.1.2] - 2021-09-28

### Fixed

- A potential issue with one of our template tags

## [1.1.1] - 2021-09-18

### Fixed

- An issue where JavaScript and CSS could have been posted in a message

## [1.1.0] - 2021-09-13

### Added

- Optional Discord webhook configuration to boards to send messages to your Discord
  via a webhook to notify a channel about new topics created in the board

## [1.0.3] - 2021-09-10

### Added

- More details added to the admin views

### Fixed

- An issue with unicode characters in category, board or topic names

## [1.0.2] - 2021-09-05

### Fixed

- Admin models are now read-only to prevent users from creating new entries via the
  Django admin backend, which will cause issues (see issue #47)

## [1.0.1] - 2021-08-31

### Changed

- Default sort order for new categories and boards moved to a constant

### Fixed

- Marked `forum_board_new_topic` as internal URL to prevent conflicts with a possible
  topic called "New Topic"
- Error 500 when trying to create a new topic with the exact same name of a topic
  that already exists on this board

## [1.0.0] - 2021-08-21

### Changed

- Moved from Beta to Stable

## [0.1.0-beta.18] - 2021-08-13

### Fixed

- "Copy message link to clipboard" button should always be visible ...

## [0.1.0-beta.17] - 2021-08-13

### Added

- "Copy message link to clipboard" button to messages in topic view

### Removed

- Image lightbox, it breaks images that have a hyperlink

## [0.1.0-beta.16] - 2021-08-04

### Changed

- Group restrictions are now alphabetically ordered

### Fixed

- Lowering SQL query count in Board view

## [0.1.0-beta.15] - 2021-08-04

### Changed

- Users with the `manage_forum` permission can now see all boards and topics, so
  they can actually manage the forum. With that said, choose wisely who gets this
  permission!

## [0.1.0-beta.14] - 2021-08-02

### Fixed

- Mobile view

## [0.1.0-beta.13] - 2021-07-25

### Fixed

- Key in setup.py

## [0.1.0-beta.12] - 2021-07-25

### Updated

- Configuration instructions in README.md to make it easier to understand if you
  have multiple apps that use CKEditor, like `aa-bulletin-board`, and how to combine
  these configurations

## [0.1.0-beta.11] - 2021-07-24

### Changed

- Moved "Modify Topic Subject" button to a better location

## [0.1.0-beta.10] - 2021-07-20

### Fixed

- Order of some bootstrap classes and some CSS

## [0.1.0-beta.9] - 2021-07-19

### Added

- "Show all unread topics" and "Mark all topics as read" buttons above the category
  list in forum index
- "Mark all topics as read" in the unread topics view above and below the board list
- More logging
- Access check if when someone tries to reply to a topic, they lost access to while
  viewing

### Removed

- Arbitrary `user_has_access` function from `Message` model

## [0.1.0-beta.8] - 2021-07-18

### Added

- Unread topics functionality to list all unread topics for the current user

## [0.1.0-beta.7] - 2021-07-17

### Added

- Child boards (1 Level). Child boards will inherit their access restrictions from
  their parents.

## [0.1.0-beta.6] - 2021-07-16

### Fixed

- [Bootstrap] CSS class moved to the right element

## [0.1.0-beta.5] - 2021-07-15

### Changed

- CKEditor config changed to prevent possible collisions in static files (see
  [README.md] for details)

## [0.1.0-beta.4] - 2021-07-14

### Added

- Ability to change the subject of the topic (User needs to be the original poster or
  forum admin to change a topic's subject)

### Changed

- Link to a message now has the full path (category, board and topic) in its URL

### Fixed

- When the first message is deleted, the topic will be deleted as well. This is to
  prevent having topics with replies to a message that does no longer exist.

## [0.1.0-beta.3] - 2021-07-07

### Added

- YouTube embed plugin for CKEditor

### Changed

- Default config for CKEditor (see [README.md] for details) to implement the
  YouTube embed plugin and to remove the obsolete Flash embed

## [0.1.0-beta.2] - 2021-07-05

### Changed

- Setup classifier and pyupgrade check, since we aim to support AA 2.8.x with its
  current minimum Python version of 3.6

## [0.1.0-beta.1] - 2021-07-04

## \\o/ FIRST PUBLIC BETA \\o/

### Added

- Title attribute to last message in forum index
- "Mark all messages as read" button to forum index
- Counter for unread topics on a forum link in navigation

## [0.0.1-alpha.11] - 2021-06-28

### Fixed

- `Topic.MultipleObjectsReturned: get() returned more than one Topic -- it returned 2!`
  when a board was restricted to more than 1 group

## [0.0.1-alpha.10] - 2021-06-28

### ⚠️ Migration Reset ⚠️

**Before** you update to this version, run the following command:

```shell
python manage.py migrate aa_forum zero
```

**After** you updated run:

```shell
python manage.py migrate aa_forum
```

### Added

- Unread messages functionality
- Version to static files to break browser caches on version updates
- New topic view now also has the bread crumb navigation
- Ability to create new boards with a new category
- Clear form button in forms that need it

### Changed

- Search function behavior. Up until now, the search function was looking for the
  whole search phrase, which is not the desired behavior. Now it checks if at least
  one word of the search phrase is in the message. This might give you more results
  but also doesn't miss the result you were looking for.
- Slugs consolidated
- Internal URLs reworked
- Pagination URLs reworked

### Fixed

- Appearance for multi select dropdown when dark mode is used

## [0.0.1-alpha.9] - 2021-06-17

### Added

- Search functionality

### Fixed

- A bug that prevented the forum index from loading after removing a message or even
  a topic

## [0.0.1-alpha.8] - 2021-06-16

### ⚠️ Migration Reset ⚠️

**Before** you update to this version, run the following command:

```shell
python manage.py migrate aa_forum zero
```

**After** you updated run:

```shell
python manage.py migrate aa_forum
```

### Added

- SQL script to drop all tables

### Changed

- Improved model design for better data consistency, performance and compliance with
  Django conventions
- Improved queries to reduce page load time for all main views

## [0.0.1-alpha.7] - 2021-06-14

### Added

- Warning when replying on locked topics
- "Re:" on last message subject on forum index, if the last message in this board
  isn't the last message in the respective topic

### Fixed

- After creating a new topic, the user now returns to the newly created topic
  instead of the board view
- Vertical alignment of the topic names in board view

## [0.0.1-alpha.6] - 2021-06-13

### Fixed

- Date and time format in the message header
- The editor now uses the space it has and doesn't sit in its corner any longer
  Add the following to your `local.py`
  ```python
  CKEDITOR_CONFIGS = {"default": {"width": "100%", "height": "45vh"}}
  ```
- Lightbox doesn't put the complete message in the modal anymore, now just the image
  that has been clicked

## [0.0.1-alpha.5] - 2021-06-13

### Added

- Messages can now be modified by their author or anyone with the `manage_forum`
  permission
- Users with the `manage_forum` permission can now delete messages. Keep in
  mind, if the last message of a topic is deleted, the topic will be removed as well.

### Fixed

- `time_modified` timestamps for messages
- Topic doesn't exist error when trying to view a topic that indeed doesn't exist
  (anymore)
- An issue where the initialization of the lightbox modal would interfere with other
  modals in a topic view. Even when there was no image that needs a lightbox.
- Consistent button style

## [0.0.1-alpha.4] - 2021-06-12

### Added

- A note when replying to a topic while not being on the last page of it
- Ability to lock and unlock topics for forum managers
- Ability to set/unset topics as "Sticky" for forum managers
- Ability to delete topics for forum managers
- Some "read_by" marker in preparation for the "Unread Messages" functionality

### Changed

- Implemented a simpler way to get a setting from the DB

## [0.0.1-alpha.3] - 2021-06-11

### Added

- Topic pagination in board view

### REMOVED

- Page number from pagination links when navigating to the first page. It's not
  needed there ...

## [0.0.1-alpha.2] - 2021-06-11

### Fixed

- Missing prefix added to "New Category" form

## [0.0.1-alpha.1] - 2021-06-11

### Added

- First version for Alpha testing

<!-- Links to be updated upon release -->

[#125]: https://github.com/ppfeufer/aa-forum/issues/125 "Localization of forum time"
[0.0.1-alpha.1]: https://github.com/ppfeufer/aa-forum/releases/edit/v0.0.1-alpha.1 "v0.0.1-alpha.1"
[0.0.1-alpha.10]: https://github.com/ppfeufer/aa-forum/compare/v0.0.1-alpha.9...v0.0.1-alpha.10 "v0.0.1-alpha.10"
[0.0.1-alpha.11]: https://github.com/ppfeufer/aa-forum/compare/v0.0.1-alpha.10...v0.0.1-alpha.11 "v0.0.1-alpha.11"
[0.0.1-alpha.2]: https://github.com/ppfeufer/aa-forum/compare/v0.0.1-alpha.1...v0.0.1-alpha.2 "v0.0.1-alpha.2"
[0.0.1-alpha.3]: https://github.com/ppfeufer/aa-forum/compare/v0.0.1-alpha.2...v0.0.1-alpha.3 "v0.0.1-alpha.3"
[0.0.1-alpha.4]: https://github.com/ppfeufer/aa-forum/compare/v0.0.1-alpha.3...v0.0.1-alpha.4 "v0.0.1-alpha.4"
[0.0.1-alpha.5]: https://github.com/ppfeufer/aa-forum/compare/v0.0.1-alpha.4...v0.0.1-alpha.5 "v0.0.1-alpha.5"
[0.0.1-alpha.6]: https://github.com/ppfeufer/aa-forum/compare/v0.0.1-alpha.5...v0.0.1-alpha.6 "v0.0.1-alpha.6"
[0.0.1-alpha.7]: https://github.com/ppfeufer/aa-forum/compare/v0.0.1-alpha.6...v0.0.1-alpha.7 "v0.0.1-alpha.7"
[0.0.1-alpha.8]: https://github.com/ppfeufer/aa-forum/compare/v0.0.1-alpha.7...v0.0.1-alpha.8 "v0.0.1-alpha.8"
[0.0.1-alpha.9]: https://github.com/ppfeufer/aa-forum/compare/v0.0.1-alpha.8...v0.0.1-alpha.9 "v0.0.1-alpha.9"
[0.1.0-beta.1]: https://github.com/ppfeufer/aa-forum/compare/v0.0.1-alpha.11...v0.1.0-beta.1 "v0.1.0-beta.1"
[0.1.0-beta.10]: https://github.com/ppfeufer/aa-forum/compare/v0.1.0-beta.9...v0.1.0-beta.10 "v0.1.0-beta.10"
[0.1.0-beta.11]: https://github.com/ppfeufer/aa-forum/compare/v0.1.0-beta.10...v0.1.0-beta.11 "v0.1.0-beta.11"
[0.1.0-beta.12]: https://github.com/ppfeufer/aa-forum/compare/v0.1.0-beta.11...v0.1.0-beta.12 "v0.1.0-beta.12"
[0.1.0-beta.13]: https://github.com/ppfeufer/aa-forum/compare/v0.1.0-beta.12...v0.1.0-beta.13 "v0.1.0-beta.13"
[0.1.0-beta.14]: https://github.com/ppfeufer/aa-forum/compare/v0.1.0-beta.13...v0.1.0-beta.14 "v0.1.0-beta.14"
[0.1.0-beta.15]: https://github.com/ppfeufer/aa-forum/compare/v0.1.0-beta.14...v0.1.0-beta.15 "v0.1.0-beta.15"
[0.1.0-beta.16]: https://github.com/ppfeufer/aa-forum/compare/v0.1.0-beta.15...v0.1.0-beta.16 "v0.1.0-beta.16"
[0.1.0-beta.17]: https://github.com/ppfeufer/aa-forum/compare/v0.1.0-beta.16...v0.1.0-beta.17 "v0.1.0-beta.17"
[0.1.0-beta.18]: https://github.com/ppfeufer/aa-forum/compare/v0.1.0-beta.17...v0.1.0-beta.18 "v0.1.0-beta.18"
[0.1.0-beta.2]: https://github.com/ppfeufer/aa-forum/compare/v0.1.0-beta.1...v0.1.0-beta.2 "v0.1.0-beta.2"
[0.1.0-beta.3]: https://github.com/ppfeufer/aa-forum/compare/v0.1.0-beta.2...v0.1.0-beta.3 "v0.1.0-beta.3"
[0.1.0-beta.4]: https://github.com/ppfeufer/aa-forum/compare/v0.1.0-beta.3...v0.1.0-beta.4 "v0.1.0-beta.4"
[0.1.0-beta.5]: https://github.com/ppfeufer/aa-forum/compare/v0.1.0-beta.4...v0.1.0-beta.5 "v0.1.0-beta.5"
[0.1.0-beta.6]: https://github.com/ppfeufer/aa-forum/compare/v0.1.0-beta.5...v0.1.0-beta.6 "v0.1.0-beta.6"
[0.1.0-beta.7]: https://github.com/ppfeufer/aa-forum/compare/v0.1.0-beta.6...v0.1.0-beta.7 "v0.1.0-beta.7"
[0.1.0-beta.8]: https://github.com/ppfeufer/aa-forum/compare/v0.1.0-beta.7...v0.1.0-beta.8 "v0.1.0-beta.8"
[0.1.0-beta.9]: https://github.com/ppfeufer/aa-forum/compare/v0.1.0-beta.8...v0.1.0-beta.9 "v0.1.0-beta.9"
[1.0.0]: https://github.com/ppfeufer/aa-forum/compare/v0.1.0-beta.18...v1.0.0 "v1.0.0"
[1.0.1]: https://github.com/ppfeufer/aa-forum/compare/v1.0.0...v1.0.1 "v1.0.1"
[1.0.2]: https://github.com/ppfeufer/aa-forum/compare/v1.0.1...v1.0.2 "v1.0.2"
[1.0.3]: https://github.com/ppfeufer/aa-forum/compare/v1.0.2...v1.0.3 "v1.0.3"
[1.1.0]: https://github.com/ppfeufer/aa-forum/compare/v1.0.3...v1.1.0 "v1.1.0"
[1.1.1]: https://github.com/ppfeufer/aa-forum/compare/v1.1.0...v1.1.1 "v1.1.1"
[1.1.2]: https://github.com/ppfeufer/aa-forum/compare/v1.1.1...v1.1.2 "v1.1.2"
[1.1.3]: https://github.com/ppfeufer/aa-forum/compare/v1.1.2...v1.1.3 "v1.1.3"
[1.10.0]: https://github.com/ppfeufer/aa-forum/compare/v1.9.0...v1.10.0 "v1.10.0"
[1.11.0]: https://github.com/ppfeufer/aa-forum/compare/v1.10.0...v1.11.0 "v1.11.0"
[1.12.0]: https://github.com/ppfeufer/aa-forum/compare/v1.11.0...v1.12.0 "v1.12.0"
[1.13.0]: https://github.com/ppfeufer/aa-forum/compare/v1.12.0...v1.13.0 "v1.13.0"
[1.14.0]: https://github.com/ppfeufer/aa-forum/compare/v1.13.0...v1.14.0 "v1.14.0"
[1.15.0]: https://github.com/ppfeufer/aa-forum/compare/v1.14.0...v1.15.0 "v1.15.0"
[1.15.1]: https://github.com/ppfeufer/aa-forum/compare/v1.15.0...v1.15.1 "v1.15.1"
[1.15.2]: https://github.com/ppfeufer/aa-forum/compare/v1.15.1...v1.15.2 "v1.15.2"
[1.16.0]: https://github.com/ppfeufer/aa-forum/compare/v1.15.2...v1.16.0 "v1.16.0"
[1.17.0]: https://github.com/ppfeufer/aa-forum/compare/v1.16.0...v1.17.0 "v1.17.0"
[1.17.1]: https://github.com/ppfeufer/aa-forum/compare/v1.17.0...v1.17.1 "v1.17.1"
[1.17.2]: https://github.com/ppfeufer/aa-forum/compare/v1.17.1...v1.17.2 "v1.17.2"
[1.18.0]: https://github.com/ppfeufer/aa-forum/compare/v1.17.2...v1.18.0 "v1.18.0"
[1.19.0]: https://github.com/ppfeufer/aa-forum/compare/v1.18.0...v1.19.0 "v1.19.0"
[1.19.1]: https://github.com/ppfeufer/aa-forum/compare/v1.19.0...v1.19.1 "v1.19.1"
[1.19.2]: https://github.com/ppfeufer/aa-forum/compare/v1.19.1...v1.19.2 "v1.19.2"
[1.19.3]: https://github.com/ppfeufer/aa-forum/compare/v1.19.2...v1.19.3 "v1.19.3"
[1.19.4]: https://github.com/ppfeufer/aa-forum/compare/v1.19.3...v1.19.4 "v1.19.4"
[1.19.5]: https://github.com/ppfeufer/aa-forum/compare/v1.19.4...v1.19.5 "v1.19.5"
[1.2.0]: https://github.com/ppfeufer/aa-forum/compare/v1.1.3...v1.2.0 "v1.2.0"
[1.2.1]: https://github.com/ppfeufer/aa-forum/compare/v1.2.0...v1.2.1 "v1.2.1"
[1.3.0]: https://github.com/ppfeufer/aa-forum/compare/v1.2.1...v1.3.0 "v1.3.0"
[1.4.0]: https://github.com/ppfeufer/aa-forum/compare/v1.3.0...v1.4.0 "v1.4.0"
[1.4.1]: https://github.com/ppfeufer/aa-forum/compare/v1.4.0...v1.4.1 "v1.4.1"
[1.4.2]: https://github.com/ppfeufer/aa-forum/compare/v1.4.1...v1.4.2 "v1.4.2"
[1.4.3]: https://github.com/ppfeufer/aa-forum/compare/v1.4.2...v1.4.3 "v1.4.3"
[1.5.0]: https://github.com/ppfeufer/aa-forum/compare/v1.4.3...v1.5.0 "v1.5.0"
[1.5.1]: https://github.com/ppfeufer/aa-forum/compare/v1.5.0...v1.5.1 "v1.5.1"
[1.6.0]: https://github.com/ppfeufer/aa-forum/compare/v1.5.1...v1.6.0 "v1.6.0"
[1.7.0]: https://github.com/ppfeufer/aa-forum/compare/v1.6.0...v1.7.0 "v1.7.0"
[1.8.0]: https://github.com/ppfeufer/aa-forum/compare/v1.7.0...v1.8.0 "v1.8.0"
[1.8.1]: https://github.com/ppfeufer/aa-forum/compare/v1.8.0...v1.8.1 "v1.8.1"
[1.9.0]: https://github.com/ppfeufer/aa-forum/compare/v1.8.1...v1.9.0 "v1.9.0"
[2.0.0]: https://github.com/ppfeufer/aa-forum/compare/v1.19.5...v2.0.0 "v2.0.0"
[2.0.0-beta.1]: https://github.com/ppfeufer/aa-forum/compare/v1.19.5...v2.0.0-beta.1 "v2.0.0-beta.1"
[2.0.0-beta.2]: https://github.com/ppfeufer/aa-forum/compare/v2.0.0-beta.1...v2.0.0-beta.2 "v2.0.0-beta.2"
[2.0.0-beta.3]: https://github.com/ppfeufer/aa-forum/compare/v2.0.0-beta.2...v2.0.0-beta.3 "v2.0.0-beta.3"
[2.1.0]: https://github.com/ppfeufer/aa-forum/compare/v2.0.0...v2.1.0 "v2.1.0"
[2.1.1]: https://github.com/ppfeufer/aa-forum/compare/v2.1.0...v2.1.1 "v2.1.1"
[2.10.0]: https://github.com/ppfeufer/aa-forum/compare/v2.9.2...v2.10.0 "v2.10.0"
[2.10.1]: https://github.com/ppfeufer/aa-forum/compare/v2.10.0...v2.10.1 "v2.10.1"
[2.10.2]: https://github.com/ppfeufer/aa-forum/compare/v2.10.1...v2.10.2 "v2.10.2"
[2.11.0]: https://github.com/ppfeufer/aa-forum/compare/v2.10.2...v2.11.0 "v2.11.0"
[2.12.0]: https://github.com/ppfeufer/aa-forum/compare/v2.11.0...v2.12.0 "v2.12.0"
[2.12.1]: https://github.com/ppfeufer/aa-forum/compare/v2.12.0...v2.12.1 "v2.12.1"
[2.13.0]: https://github.com/ppfeufer/aa-forum/compare/v2.12.1...v2.13.0 "v2.13.0"
[2.2.0]: https://github.com/ppfeufer/aa-forum/compare/v2.1.1...v2.2.0 "v2.2.0"
[2.2.1]: https://github.com/ppfeufer/aa-forum/compare/v2.2.0...v2.2.1 "v2.2.1"
[2.3.0]: https://github.com/ppfeufer/aa-forum/compare/v2.2.1...v2.3.0 "v2.3.0"
[2.3.1]: https://github.com/ppfeufer/aa-forum/compare/v2.3.0...v2.3.1 "v2.3.1"
[2.4.0]: https://github.com/ppfeufer/aa-forum/compare/v2.3.1...v2.4.0 "v2.4.0"
[2.4.1]: https://github.com/ppfeufer/aa-forum/compare/v2.4.0...v2.4.1 "v2.4.1"
[2.5.0]: https://github.com/ppfeufer/aa-forum/compare/v2.4.1...v2.5.0 "v2.5.0"
[2.6.0]: https://github.com/ppfeufer/aa-forum/compare/v2.5.0...v2.6.0 "v2.6.0"
[2.7.0]: https://github.com/ppfeufer/aa-forum/compare/v2.6.0...v2.7.0 "v2.7.0"
[2.8.0]: https://github.com/ppfeufer/aa-forum/compare/v2.7.0...v2.8.0 "v2.8.0"
[2.8.1]: https://github.com/ppfeufer/aa-forum/compare/v2.8.0...v2.8.1 "v2.8.1"
[2.9.0]: https://github.com/ppfeufer/aa-forum/compare/v2.8.1...v2.9.0 "v2.9.0"
[2.9.1]: https://github.com/ppfeufer/aa-forum/compare/v2.9.0...v2.9.1 "v2.9.1"
[2.9.2]: https://github.com/ppfeufer/aa-forum/compare/v2.9.1...v2.9.2 "v2.9.2"
[aa time zones]: https://github.com/ppfeufer/aa-timezones "AA Time Zones"
[aa-discordbot]: https://github.com/pvyParts/allianceauth-discordbot "AA-Discordbot"
[admin board options]: https://raw.githubusercontent.com/ppfeufer/aa-forum/master/docs/images/admin-board-options.jpg "Admin Board Options"
[discordproxy]: https://gitlab.com/ErikKalkoken/discordproxy "discordproxy"
[in development]: https://github.com/ppfeufer/aa-forum/compare/v2.13.0...HEAD "In Development"
[keep a changelog]: http://keepachangelog.com/ "Keep a Changelog"
[new feature: announcement boards]: https://raw.githubusercontent.com/ppfeufer/aa-forum/master/docs/images/feature-announcement-board.jpg "New Feature: Announcement Boards"
[new feature: support for aa-timezones]: https://user-images.githubusercontent.com/2989985/195106607-8caf39c1-7343-404b-a926-e3253558b1ce.png "New Feature: Support for aa-timezones"
[readme.md]: https://github.com/ppfeufer/aa-forum/blob/development/README.md "README.md"
[semantic versioning]: http://semver.org/ "Semantic Versioning"
