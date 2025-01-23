# Attributes of the IRC connection
IRC_TARGET = ['irc://irc.libera.chat/bottest']

# a dictionary of branches push-related events should be enabled for, or empty if all are enabled
GH_PUSH_ENABLED_BRANCHES = []  # for example, ['master', 'testing', 'author/repo:branch']

# a list of push-related events the bot should post notifications for
#GH_PUSH_ENABLED_EVENTS = ['push', 'force-push', 'delete'] # no others supported for now
GH_PUSH_ENABLED_EVENTS = []

# a list of PR-related events the bot should post notifications for
# notice 'merged' is just a special case of 'closed'
GH_PR_ENABLED_EVENTS = ['opened', 'closed', 'reopened'] # could also add 'synchronized', 'labeled', etc.

# a list of workflow-run-related events the bot should post notiifications for
#GH_WFR_ENABLED_EVENTS = ['requested', 'in_progress', 'completed']
GH_WFR_ENABLED_EVENTS = ['completed']

# the github webhook secret
secret = "secret"
