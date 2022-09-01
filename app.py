"""The whotoboost app.
"""

import pandas
import plotnine
import streamlit
import tweepy

import whotoboost


DEFAULT_N_USERS = 10
MAX_N_USERS = 30


# %% caching function

@streamlit.cache
def fetch_data(username):
    
    return whotoboost.get_followees_follower_counts(username)


# %% user input

streamlit.title('who should you be boosting?')

streamlit.markdown('Find out which of the accounts you follow are the smallest. So you can boost them!')

username = streamlit.text_input(
    'your Twitter username',
    help='Your Twitter handle is the one that begins with @',
    placeholder='@exampleuser'
)

username = username.strip().lstrip('@')

if username:
    fetch = True
    output = True
else:
    fetch = False
    output = False

n_users = streamlit.slider(
    'how many of the smallest accounts to show',
    min_value=3,
    max_value=MAX_N_USERS,
    value=DEFAULT_N_USERS
)

if fetch:

    try:
        followees = fetch_data(username)
        if followees.shape[0] == 0:
            streamlit.markdown(f'**\'{username}\' is not following anyone.**')
            output = False
        else:
            output = True
    except tweepy.BadRequest:
        streamlit.markdown(f'**\'{username}\' is not a valid username.**')
        output = False
    except whotoboost.UserNotFoundError:
        streamlit.markdown(f'**\'{username}\' not found.**')
        output = False
    except tweepy.TooManyRequests:
        streamlit.markdown('**Too much traffic! Try again later.**')
        output = False


# %% figure

if output:

    small_followees = followees.nsmallest(n_users, ['followers'])

    small_followees['username'] = pandas.Categorical(
        small_followees['username'],
        categories=small_followees['username'].tolist()
    )

    fig = (
        plotnine.ggplot(small_followees)
        + plotnine.aes(
            x='username',
            y='followers',
            label='followers',
        )
        + plotnine.geom_col()
        + plotnine.geom_text()
        + plotnine.labs(x='')
        + plotnine.ggtitle('followed by @' + username)
        + plotnine.coord_flip()
    )

    streamlit.pyplot(fig.draw())