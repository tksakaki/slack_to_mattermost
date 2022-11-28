from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from mattermostdriver import Driver
import re
import time


class Slack_client:
    def __init__(self, token):
        self.client = WebClient(token=token)
        ret_userdata = self.client.users_list()
        self.users = {}
        for u in ret_userdata["members"]:
            self.users[u['id']] = u
        self.regex_user = re.compile("(\<@([^\>]+)\>)")

    def get_channels(self):
        channels = []
        self.dic_channels = {}
        print("get channels")
        loop_flag = True
        next_cursor = None
        while(loop_flag):
            print(f"crawl channels:{next_cursor}")
            try:
                # Call the conversations.list method using the WebClient
                if(next_cursor):
                    json_data = self.client.conversations_list(
                        exclude_archived=True,
                        cursor=next_cursor
                    )
                else:
                    json_data = self.client.conversations_list(
                        exclude_archived=True
                    )

            except SlackApiError as e:
                print("Error fetching conversations: {}".format(e))
                print(f'Message: {e.response["error"]}\n')
                if(e.response["error"] == "ratelimited"):
                    loop_flag = True
                    print("rate limited in get_channels..wait 30 minutes\n")
                    time.sleep(30)
                    continue
                else:
                    print("unknown error! quit\n")
                    quit()

            if("channels" in json_data):
                channels.extend(json_data['channels'])

            loop_flag = False
            if("response_metadata" in json_data):
                if("next_cursor" in json_data["response_metadata"]):
                    if(json_data["response_metadata"]["next_cursor"] != ""):
                        next_cursor = json_data["response_metadata"]["next_cursor"]
                        loop_flag = True

        for ch in channels:
            self.dic_channels[ch["name"]] = ch

        return self.dic_channels

    def search_channel_period(self, channel, date_from, date_to, count=100):
        date_from_ex = date_from.strftime("%Y-%m-%d")
        date_to_ex = date_to.strftime("%Y-%m-%d")
        search_query = f'in:#{channel["name"]} before:{date_to_ex} after:{date_from_ex}'
        print(search_query)
        page_count = 1
        paging_flag = True
        counter = 0
        ret_entry = []
        while(paging_flag):
            res = self.client.search_all(
                query=search_query,
                count=count,
                page=page_count,
                sort="timestamp",
                sort_dir="asc"
            )
            print(res["messages"]["paging"])
            total_count = res["messages"]["paging"]["total"]
            page_count += 1
            ret_entry.extend(res["messages"]["matches"])
            counter += len(res["messages"]["matches"])
            if(total_count <= counter):
                paging_flag = False
        return ret_entry

    def convert_user(self, text):
        match_result = self.regex_user.findall(text)
        for res in match_result:
            text = text.replace(res[0], f'@{self.users[res[1]]["real_name"]} ')
        return text


class Mattermost_client:
    def __init__(self, token_id, token, team_id, url):
        self.client = Driver({
            'url': url,
            'login_id': token_id,
            'token': token,
            'scheme': 'https',
            'port': 443,
            'verify': True
        })
        self.client.login()
        self.team_id = team_id

    def __del__(self):
        self.client.logout()

    def get_channels(self):
        list_mtchannels = self.client.channels.get_public_channels(self.team_id)
        self.dic_channels = {}
        for ch in list_mtchannels:
            self.dic_channels[ch["name"]] = ch
        return self.dic_channels

    def create_channel(self, name):
        ret_value = self.client.channels.create_channel(
            options={
                "team_id": self.team_id,
                "name": name,
                "display_name": name,
                "type": "O"
            }
        )
        return ret_value
