import api_client
import os
import pandas as pd
import pandas.tseries.offsets as offsets
import time

# Mattermost Driver Setting


def post_mattermost(mattermost_client, slack_client, target_channel, dic_posts):
    for ts, post in sorted(dic_posts.items(), key=lambda x:x[0]):
        # チャネルへのメッセージ投稿
        print(post)
        post_time = pd.Timestamp.fromtimestamp(post["ts"]).tz_localize("UTC").tz_convert("Asia/Tokyo")
        text = slack_client.convert_user(post['text'])
        message = "\n\nーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー\n"
        message += f'投稿者:{slack_client.users[post["author"]]["real_name"]}\n'
        message += f'投稿時刻:{post_time.strftime("%Y-%m-%d %H:%M:%S")}\n'
        message += f'{text}\n'
        message += "\n\n"
        mattermost_client.client.posts.create_post(options={
            'channel_id': target_channel,
            'message': message
        })


def run_daily(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
        Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    today = pd.to_datetime("today").tz_localize("UTC").tz_convert("Asia/Tokyo")
    date_to = today.normalize()
    date_from = (today - offsets.Day(2)).normalize()
    mattermost = {
      "id": os.environ['mattermost_id'],
      "token": os.environ['mattermost_token'],
      "url": os.environ['mattermost_url'],
      "team_id": os.environ['mattermost_team_id']
      }
    slack_token = os.environ['slack_token']
    print("initialize")
    s_client = api_client.Slack_client(token=slack_token)
    mt_client = api_client.Mattermost_client(
        token=mattermost["token"],
        token_id=mattermost["id"],
        team_id=mattermost["team_id"],
        url=mattermost["url"]
        )
    print("create client done.")
    time.sleep(10)
    slack_channel = s_client.get_channels()
    matter_channel = mt_client.get_channels()
    print("read channels done.")
    time.sleep(10)
    for k, v in s_client.dic_channels.items():
        if(k not in mt_client.dic_channels):
            try:
                print(f"create channel {k} on Mattermost")
                mt_client.create_channel(k)
            except Exception as e:
                print(f"create channel error{str(e.args)}")
    matter_channel = mt_client.get_channels()
    print("sync channels slack <=> mattermost done.")
    for ch, chinfo in s_client.dic_channels.items():
        list_posts = s_client.search_channel_period(
            channel=slack_channel[ch],
            date_from=date_from,
            date_to=date_to,
            count=100
            )
        dic_posts = {}
        for post in list_posts:
            dic_posts[post['ts']] = {
                'text': post['text'],
                'author': post['user'],
                'ts': float(post['ts'])
                }
        post_mattermost(
            mattermost_client=mt_client,
            slack_client=s_client,
            target_channel=matter_channel[ch]["id"],
            dic_posts=dic_posts
            )
        time.sleep(10)
    print("sync message done.")
