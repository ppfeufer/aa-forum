"""
Setting up our app
"""

import os

from setuptools import find_packages, setup

from aa_forum import __version__

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

package_name = "aa-forum"
package_description = "Simple forum for Alliance Auth"
package_license = "GPLv3"
package_author = "Peter Pfeufer"
package_author_email = "development@ppfeufer.de"
package_git_url = "https://github.com/ppfeufer/aa-forum"
package_issues_url = "https://github.com/ppfeufer/aa-forum/issues"
package_changelog_url = "https://github.com/ppfeufer/aa-forum/blob/master/CHANGELOG.md"
package_install_requirements = [
    "allianceauth>=2.8.2",
    "django-ckeditor",
    "allianceauth-app-utils>=1.8.0",
]
package_classifiers = [
    "Environment :: Web Environment",
    "Framework :: Django",
    "Framework :: Django :: 3.1",
    "Framework :: Django :: 3.2",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
]

# URLs are listed in reverse on Pypi
project_urls = {
    "Issue / Bug Reports": package_issues_url,
    "Changelog": package_changelog_url,
    "Git Repository": package_git_url,
}

setup(
    name=package_name,
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    license=package_license,
    description=package_description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=package_git_url,
    project_urls=project_urls,
    author=package_author,
    author_email=package_author_email,
    classifiers=package_classifiers,
    python_requires="~=3.6",
    install_requires=package_install_requirements,
)
