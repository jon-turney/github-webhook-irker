# import requests
import sys

import config
import irccolors
import irk


def fmt_repo(data):
    repo = '[' + data['repository']['full_name'] + ']'
    return irccolors.colorize(repo, 'royal')


# Use git.io to get a shortened link for commit names, etc. which are too long
# XXX: service no longer available
def short_gh_link(link):
#    conn = requests.post('https://git.io', data={'url':link})
#    return conn.headers['Location']
    return link


MAX_COMMIT_LOG_LEN = 5
MAX_COMMIT_LEN = 70


def fmt_commit(cmt):
    hsh = irccolors.colorize(cmt['id'][:10], 'teal')
    author = irccolors.colorize(cmt['author']['name'], 'bold-green')
    message = cmt['message']
    message = message[:MAX_COMMIT_LEN] \
        + ('..' if len(message) > MAX_COMMIT_LEN else '')

    return '{} {}: {}'.format(hsh, author, message)


def fmt_last_commits(data):
    commits = list(map(fmt_commit, data['commits']))

    # make sure the commit list isn't too long
    if len(commits) <= MAX_COMMIT_LOG_LEN:
        return commits
    else:
        ellipsized_num = len(commits) - MAX_COMMIT_LOG_LEN + 1
        ellipsized = str(ellipsized_num) + ' more'
        last_shown = MAX_COMMIT_LOG_LEN - 1

        last_line = '... and {} commit' \
            .format(irccolors.colorize(ellipsized, 'royal'))
        if ellipsized_num > 1:  # add s to commitS
            last_line += 's'

        return commits[slice(0, last_shown)] + [last_line]


def get_branch_name_from_push_event(data):
    return data['ref'].split('/')[-1]


def handle_force_push(data):
    author = irccolors.colorize(data['pusher']['name'], 'bold')

    before = irccolors.colorize(data['before'][:10], 'bold-red')
    after = irccolors.colorize(data['after'][:10], 'bold-red')

    branch = get_branch_name_from_push_event(data)
    branch = irccolors.colorize(branch, 'bold-blue')

    irk.irk("{} {} force-pushed {} from {} to {} ({}):"
            .format(fmt_repo(data), author, branch, before, after, short_gh_link(data['compare'])))

    commits = fmt_last_commits(data)
    for commit in commits:
        irk.irk(commit)


def handle_forward_push(data):
    author = irccolors.colorize(data['pusher']['name'], 'bold')

    num_commits = len(data['commits'])
    num_commits = str(num_commits) + " commit" + ('s' if num_commits > 1 else '')

    num_commits = irccolors.colorize(num_commits, 'bold-teal')

    branch = get_branch_name_from_push_event(data)
    branch = irccolors.colorize(branch, 'bold-blue')

    irk.irk("{} {} pushed {} to {} ({}):"
            .format(fmt_repo(data), author, num_commits, branch, short_gh_link(data['compare'])))

    commits = fmt_last_commits(data)
    for commit in commits:
        irk.irk(commit)


def handle_delete_branch(data):
    author = irccolors.colorize(data['pusher']['name'], 'bold')
    action = irccolors.colorize('deleted', 'red')

    branch = get_branch_name_from_push_event(data)
    branch = irccolors.colorize(branch, 'bold-blue')

    irk.irk("{} {} {} {}"
            .format(fmt_repo(data), author, action, branch))


def handle_push_event(data):
    if config.GH_PUSH_ENABLED_BRANCHES:
        branch = get_branch_name_from_push_event(data)
        repo = data['repository']['full_name']
        repobranch = repo + ':' + branch
        if not branch in config.GH_PUSH_ENABLED_BRANCHES:
            if not repobranch in config.GH_PUSH_ENABLED_BRANCHES:
                return

    if data['forced'] and 'force-push' in config.GH_PUSH_ENABLED_EVENTS:
        handle_force_push(data)
    elif data['deleted'] and 'delete' in config.GH_PUSH_ENABLED_EVENTS:
        handle_delete_branch(data)
    elif 'push' in config.GH_PUSH_ENABLED_EVENTS:
        handle_forward_push(data)


def fmt_pr_action(action, merged):
    if action == 'opened' or action == 'reopened':
        action = irccolors.colorize(action, 'green')
    elif action == 'closed':
        if merged:
            action = irccolors.colorize('merged', 'purple')
        else:
            action = irccolors.colorize(action, 'red')
    else:
        action = irccolors.colorize(action, 'brown')

    return action


def handle_pull_request(data):
    repo = fmt_repo(data)
    author = irccolors.colorize(data['sender']['login'], 'bold')
    if not data['action'] in config.GH_PR_ENABLED_EVENTS:
        return

    action = fmt_pr_action(data['action'], data['pull_request']['merged'])
    pr_num = irccolors.colorize('#' + str(data['number']), 'bold-blue')
    title = data['pull_request']['title']
    link = short_gh_link(data['pull_request']['html_url'])

    irk.irk('{} {} {} pull request {}: {} ({})'
            .format(repo, author, action, pr_num, title, link))


def handle_issue(data):
    repo = fmt_repo(data)
    user = irccolors.colorize(data['sender']['login'], 'bold')

    action = data['action']
    if not action in ['opened', 'closed']:
        return
    action_color = 'red' if action == 'opened' else 'green'
    action = irccolors.colorize(action, action_color)

    issue_num = irccolors.colorize('#' + str(data['issue']['number']), 'bold-blue')
    title = data['issue']['title']
    link = short_gh_link(data['issue']['html_url'])

    irk.irk('{} {} {} issue {}: {} ({})'
            .format(repo, user, action, issue_num, title, link))


def handle_workflow_run(data):
    repo = fmt_repo(data)
    action = data['action']

    if action not in config.GH_WFR_ENABLED_EVENTS:
        return

    conclusion = data['workflow_run']['conclusion']
    run_number = data['workflow_run']['run_number']
    link = data['workflow_run']['html_url']

    if conclusion is None:
        conclusion = ''

    if conclusion == 'success':
        conclusion = irccolors.colorize(conclusion, 'green')
    else:
        conclusion = irccolors.colorize(conclusion, 'red')

    irk.irk('{} Workflow run {} {}: {}. {}'
            .format(repo, run_number, action, conclusion, link))


def handle_ping_event(data):
    repo = fmt_repo(data)
    irk.irk('{} ping event'.format(repo))


def handle_event(event, data):
    if event == 'ping':
        handle_ping_event(data)
    elif event == 'push':
        handle_push_event(data)
    elif event == 'pull_request':
        handle_pull_request(data)
    elif event == 'issues':
        handle_issue(data)
    elif event == 'workflow_run':
        handle_workflow_run(data)
    else:
        print("Unknown event type: " + event, file=sys.stderr)
