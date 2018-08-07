import time
import re
from operator import itemgetter
from slackclient import SlackClient
import conf
from tweepy import API
from tweepy import OAuthHandler
import json
import schedule

# instantiate Slack client
slack_client = SlackClient(conf.SLACK_BOT_TOKEN)
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "topsy"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

auth = OAuthHandler(conf.CONSUMER_KEY,conf.CONSUMER_SECRET)
auth.set_access_token(conf.ACCESS_TOKEN,conf.ACCESS_SECRET)
api = API(auth)

def call_top(sched='True'):
    top_tweets = api.trends_place(1)
    new_tweets = json.dumps(top_tweets, indent=4, sort_keys=True)
    new_tweets = json.loads(new_tweets)
    tweet_dict = new_tweets[0]

    top = tweet_dict['trends']

    sorted_tweets = sorted(top, key=itemgetter('tweet_volume'), reverse=True)
    tmpList = []

    ctr = 0

    while ctr < 10:
        tmpList.append(sorted_tweets[ctr]['name'])
        ctr += 1

    response = "\n".join(tmpList)


    if sched:
        slack_client.api_call(
        "chat.postMessage",
        channel='assignment1',
        text=response
    )
    else:
         return response



def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = call_top()

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        schedule.every().day.at('12:00').do(call_top)
        while True:
            schedule.run_pending()
            time.sleep(RTM_READ_DELAY)
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
