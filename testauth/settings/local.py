"""
Test settings
"""

# flake8: noqa

########################################################
# local.py settings
# Every setting in base.py can be overloaded by redefining it here.

from .base import *

PACKAGE = "aa_forum"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
# STATICFILES_DIRS = [os.path.join(PROJECT_DIR, f"{PACKAGE}/static")]
STATICFILES_DIRS = [
    f"{PACKAGE}/static",
]

SITE_URL = "https://example.com"
CSRF_TRUSTED_ORIGINS = [SITE_URL]

DISCORD_BOT_TOKEN = "My_Dummy_Token"
# These are required for Django to function properly. Don't touch.
ROOT_URLCONF = "testauth.urls"
WSGI_APPLICATION = "testauth.wsgi.application"
SECRET_KEY = "t$@h+j#yqhmuy$x7$fkhytd&drajgfsb-6+j9pqn*vj0)gq&-2"

# This is where css/images will be placed for your webserver to read
STATIC_ROOT = "/var/www/testauth/static/"

# Change this to change the name of the auth site displayed
# in page titles and the site header.
SITE_NAME = "testauth"

# Change this to enable/disable debug mode, which displays
# useful error messages but can leak sensitive data.
DEBUG = False

LOGGING = False

NOTIFICATIONS_REFRESH_TIME = 30
NOTIFICATIONS_MAX_PER_USER = 50

if os.environ.get("USE_MYSQL", True) is True:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "tox_allianceauth",
        "USER": os.environ.get("DB_USER", "user"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "password"),
        "HOST": os.environ.get("DB_HOST", ""),
        "PORT": os.environ.get("DB_PORT", ""),
        "OPTIONS": {"charset": "utf8mb4"},
        "TEST": {
            "CHARSET": "utf8mb4",
            "NAME": "test_tox_allianceauth",
        },
    }

# Add any additional apps to this list.
INSTALLED_APPS += [
    PACKAGE,
    "django_ckeditor_5",  # https://github.com/hvlads/django-ckeditor-5
    "timezones",
]

# By default, apps are prevented from having public views for security reasons.
# If you want to allow specific apps to have public views,
# you can put their names here (same name as in INSTALLED_APPS).
#
# Note:
#   » The format is the same as in INSTALLED_APPS
#   » The app developer must explicitly allow public views for his app
APPS_WITH_PUBLIC_VIEWS = []

# ------------------------------------------------------------------------------------ #
#
#                                  ESI Settings
#
# ------------------------------------------------------------------------------------ #
# Register an application at
# https://developers.eveonline.com for Authentication
# & API Access and fill out these settings.
# Be sure to set the callback URL
# to https://example.com/sso/callback
# substituting your domain for example.com
# Logging in to auth requires the publicData
# scope (can be overridden through the
# LOGIN_TOKEN_SCOPES setting).
# Other apps may require more (see their docs).
ESI_SSO_CLIENT_ID = "dummy"
ESI_SSO_CLIENT_SECRET = "dummy"
ESI_SSO_CALLBACK_URL = "http://localhost:8000"


# ------------------------------------------------------------------------------------ #
#
#                                E-Mail Settings
#
# ------------------------------------------------------------------------------------ #
# By default, emails are validated before new users can log in.
# It's recommended to use a free service like SparkPost
# or Elastic Email to send email.
# Https://www.sparkpost.com/docs/integrations/django/
# https://elasticemail.com/resources/settings/smtp-api/
# Set the default from email to something like 'noreply@example.com'
# Email validation can be turned off by uncommenting the line below.
# This can break some services.
REGISTRATION_VERIFY_EMAIL = False
EMAIL_HOST = ""
EMAIL_PORT = 587
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = ""

#######################################
# Add any custom settings below here. #
#######################################

# Discord
DISCORD_GUILD_ID = "1234567890"

## AA Forum
if "django_ckeditor_5" in INSTALLED_APPS:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "media/uploads")

    customColorPalette = [
        {"color": "hsl(4, 90%, 58%)", "label": "Red"},
        {"color": "hsl(340, 82%, 52%)", "label": "Pink"},
        {"color": "hsl(291, 64%, 42%)", "label": "Purple"},
        {"color": "hsl(262, 52%, 47%)", "label": "Deep Purple"},
        {"color": "hsl(231, 48%, 48%)", "label": "Indigo"},
        {"color": "hsl(207, 90%, 54%)", "label": "Blue"},
    ]

    # CKEDITOR_5_CUSTOM_CSS = "path_to.css"  # optional
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
                "imageUpload",
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
                "code",
                "subscript",
                "superscript",
                "highlight",
                "|",
                "codeBlock",
                "sourceEditing",
                "insertImage",
                "bulletedList",
                "numberedList",
                "todoList",
                "|",
                "blockQuote",
                "imageUpload",
                "|",
                "fontSize",
                "fontFamily",
                "fontColor",
                "fontBackgroundColor",
                "mediaEmbed",
                "removeFormat",
                "insertTable",
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
