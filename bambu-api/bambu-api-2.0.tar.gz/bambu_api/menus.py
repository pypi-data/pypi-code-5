"""
Provides a menu builder used by ``bambu_navigation``.
"""

import bambu_navigation
class APIMenuBuilder(bambu_navigation.MenuBuilder):
	def register_partials(self):
		return (
			{
				'name': 'api',
				'description': 'Adds a link to the API documentation'
			},
		)
	
	def add_to_menu(self, name, items, **kwargs):
		items.append(
			{
				'url': ('api:doc',),
				'title': u'Developers',
				'selection': 'develop'
			}
		)

bambu_navigation.site.register(APIMenuBuilder)