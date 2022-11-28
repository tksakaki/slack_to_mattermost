# slack_to_mattermost
Scripts to snyc all message mattermost with slack.  This script is intended for daily execution



## Setup

### Install

``` 
pip install -r requirements.txt
```

### environment variables

* Mattermost関連
  * mattermost_id: Mattermost API id
  * mattermost_token: Mattermost API token
  * mattermost_url: Mattermost URL
  * mattermost_team_id: Mattermost team_id
* Slack関連
  * slack_token: Slack API token．User OAuth Token is better.

#### API setting

#### Slack

* User Token Scopes
  * [channels:history](https://api.slack.com/scopes/channels:history)
  * [channels:read](https://api.slack.com/scopes/channels:read)
  * [files:read](https://api.slack.com/scopes/files:read)
  * [search:read](https://api.slack.com/scopes/search:read)
  * [users.profile:read](https://api.slack.com/scopes/users.profile:read)
  * [users:read](https://api.slack.com/scopes/users:read)

#### Mattermost 

 nothing Special



## How to Use

* setup to run daily_run() on main.py dailly.
  * Linux server: setup cron
  * GCP
    * Cloudfunctions
    * PubSub
    * CloudScheduler
  * AWS
    * Lambda
    * Cloudwatch (for daily run)
