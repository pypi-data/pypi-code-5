from distutils.core import setup
setup(
  name = 'sci-newsletter',
  include_package_data=True,
  packages = ['newsletter'], # this must be the same as the name above
  version = '0.50',
  description = 'The newsletter module for django for sending auto-gen. emails to a contact list',
  author = 'Tuprikov Maxim',
  author_email = 'insality@gmail.com',
  url = 'https://bitbucket.org/Insality/newsletter-prototype/', # use the URL to the github repo
  download_url = 'https://bitbucket.org/Insality/newsletter-prototype/', # I'll explain this in a second
  keywords = ['feed', 'newsletter'], # arbitrary keywords
  classifiers = [],
)
