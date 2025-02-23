import sys
import os
import django
import environ


sys.path.insert(0, os.path.abspath('..'))

env = environ.Env()
env.read_env(os.path.abspath('../.env'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hw_project.settings')

django.setup()
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'HW_14_DJANGO'
copyright = '2025, Krasnozhon_A'
author = 'Krasnozhon_A'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autodoc_default_options = {
    'exclude-members': 'DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, SECRET_KEY, MONGO_URI, MONGO_DB_NAME, MONGO_DOMAIN,'
                       'MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD, EMAIL_HOST, EMAIL_PORT, EMAIL_STARTTLS,'
                       'EMAIL_USE_SSL, EMAIL_USE_TLS, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, DEFAULT_FROM_EMAIL, file_path',
}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'nature'
html_static_path = ['_static']
