"""
Django settings for onlineTest project.

Generated by 'django-admin startproject' using Django 1.9.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

USER_FILE_DIR = "/home/judge/user_file/"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'CPP'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

SITE_NAME = "程序设计类课程作业平台"
CONTACT_INFO = "薛景老师（QQ群：230689474）"
ADMINS = [('XueJing', 'xuejing@c.njupt.edu.cn', 'xuejing_cn@163.com'),]#第一项为管理员名称>    ，第二项为发件人邮箱，第三项为收系统邮件邮箱
SITE_DOMAIN = "c.njupt.edu.cn"

ALLOWED_HOSTS = ['*']

LOGIN_REDIRECT_URL = '/index/'
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'auth_system',
    'teetest',          #验证码
    'judge',            #题库管理系统
    'work',             #作业管理系统
    'faq',              #智能问答系统
    'mooc',             #慕课资源管理系统
    'process',          #程序相似度计算
    'qqlogin',          #QQ登录模块
    'channels',         #django-channels，使用websocket来实时推送消息
    'code_week',        #程序设计课过程管理系统
    'warning',          #成绩预警模块
    'django_crontab',   #定时发送邮件
    'sign',             #基于地理位置的签到
    'message',          #消息系统
    'wenda',            #异步问答模块
]

CRONJOBS = [
    ('0 20 * * 7', 'warning.m.warning', '>> /home/judge/log/warning.log'),
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware'
]

ROOT_URLCONF = 'onlineTest.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'work.views.global_settings',
            ],
            'libraries': {
                'filters': 'work.templatetags.filters',
            },
        },
    },
]

WSGI_APPLICATION = 'onlineTest.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jol',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '',
        'PORT': '',
    }
}

# OAuth设置
QQ_APP_ID = ''
QQ_KEY = ''
QQ_RECALL_URL = '/qqlogin/oauth/qq/check'

AUTH_USER_MODEL = 'auth_system.MyUser'
# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Shanghai'

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

USE_I18N = True

USE_L10N = True

# email配置#########################################
EMAIL_HOST = 'smtp.163.com'  # SMTP地址
EMAIL_PORT = 25  # SMTP端口
EMAIL_HOST_USER = 'youremail@163.com'  # 我自己的邮箱
EMAIL_HOST_PASSWORD = 'password'  # 我的邮箱密码
EMAIL_SUBJECT_PREFIX = '程序设计类课程作业平台'  # 为邮件Subject-line前缀,默认是'[django]'
EMAIL_USE_TLS = True  # 与SMTP服务器通信时，是否启动TLS链接(安全链接)。默认是false

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# Static files (css, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static"), ]

# 需要与site.cnf 设置的静态文件路径相同
STATIC_ROOT = '/var/www/html/static'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(USER_FILE_DIR,'media')
LOGIN_URL = '/accounts/login/'

# Channel settings
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379')],
        },
        "ROUTING": "code_week.routing.code_week_routing",
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {#格式器
        'verbose': {#详细
            'format': '>>[%(asctime)s][%(name)s:%(lineno)d][%(levelname)s]-%(message)s'
        },
        'simple': {#简单
            'format': '$[%(threadName)s:%(thread)d] [%(levelname)s]- %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
            },
    },
    'handlers': {
        'mail_admins': {
            'level': 'INFO',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        #'default': {
        #    'level':'DEBUG',
        #    'class':'logging.handlers.RotatingFileHandler',
        #    'filename': os.path.join('/home/judge/log/','django_all.log'), #日志所在路径
        #    'maxBytes': 1024*1024*50, # 5 MB
        #    'backupCount': 5,
        #    'formatter':'verbose',
        #},
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file':{
            'level':'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('/home/judge/log/','django.log'),
            'maxBytes': 1024*1024*50, # 50 MB
            'backupCount': 100, # 保留日志的数量，0代表不自动删除
            'formatter':'verbose',
            'encoding':'UTF-8',
        },
        'detail':{
            'level':'INFO',
            'class':'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join('/home/judge/log/','detail.log'),
            'when': 'MIDNIGHT',
            'interval': 1,
            'backupCount': 180,
            'formatter':'verbose',
            'encoding':'UTF-8',
        },
        'request':{
            'level':'INFO',
            'class':'logging.FileHandler',
            'filename': os.path.join('/home/judge/log/','request.log'),
            'formatter':'verbose',
            'encoding':'UTF-8',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file','detail'],
            'level': 'INFO',
            'propagate': False
        },
        'django.request':{
            'handlers':['request'],
            'level':'WARNING',
            'propagate': False,
        },
    }
}
