"""Get information about followees and their follower counts.
"""

import os

import dotenv
import pandas
import tweepy


dotenv.load_dotenv()

client = tweepy.Client(os.getenv('BEARER_TOKEN'))


class UserNotFoundError(Exception):
    pass


def get_followees_follower_counts(username):
    """For each of the accounts a user follows, get that account's follower count.

    argument username: str '@' handle

    returns: pandas.DataFrame with columns:
        username: str
        followers: int
    """
    
    user = client.get_user(username=username)

    if user.data is None:
        raise UserNotFoundError(f'user \'{username}\' not found.')

    user_id = user.data.id

    results = {
        'username': [],
        'followers': []
    }

    pagination_token = None
    page_count = 0

    while True:

        follows = client.get_users_following(
            user_id,
            max_results=1000,
            pagination_token=pagination_token,
            user_fields=['public_metrics']
        )

        page_count += 1
        result_count = follows.meta['result_count']

        if result_count == 0:
            break

        pagination_token = follows.meta.get('next_token', None)

        print(f'page {page_count}: {result_count} results')

        for followee in follows.data:
            results['username'].append('@' + followee.username)
            results['followers'].append(followee.public_metrics['followers_count'])

        if pagination_token is None:
            break

    df = pandas.DataFrame(results)
    df.sort_values(['followers'], inplace=True)

    return df