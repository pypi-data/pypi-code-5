ENDPOINT_METHOD_DEFAULTS = {
    '/people/{username}/activities_post': {'object': {'objectType': 'note'}},
    '/people/{username}/conversations/{id}/messages_post': {'object': {'objectType': 'note'}},
    '/contexts/{hash}/activities_post': {'object': {'objectType': 'note'}},
    '/contexts_post': {'objectType': 'context'},
    '/people/{username}/subscriptions_post': {'object': {'objectType': 'context'}}
}
