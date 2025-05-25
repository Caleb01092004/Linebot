from flask import Flask, request, abort, jsonify
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    #richmenu
    MessagingApiBlob,
    RichMenuSize,
    RichMenuRequest,
    RichMenuArea,
    RichMenuBounds,
    #Message sending
    ReplyMessageRequest,
    PushMessageRequest,
    BroadcastRequest,
    MulticastRequest,
    #MessageType
    TextMessage,
    Emoji,
    VideoMessage,
    AudioMessage,
    ImageMessage,
    LocationMessage,
    StickerMessage,
    #Template
    TemplateMessage,
    ConfirmTemplate,
    ButtonsTemplate,
    CarouselTemplate,
    CarouselColumn,
    ImageCarouselTemplate,
    ImageCarouselColumn,
    #QuickReply
    QuickReply,
    QuickReplyItem,
    #Action
    MessageAction,
    URIAction,
    PostbackAction,
    DatetimePickerAction,
    CameraAction,
    CameraRollAction,
    LocationAction
)
from linebot.v3.webhooks import (
    FollowEvent,
    MessageEvent,
    PostbackEvent,
    TextMessageContent
)
import os
import requests
import logging
from functools import wraps
import json
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
configuration = Configuration(access_token=os.getenv("CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))
def sendDataTobackend(user_id):
    try:
        response = requests.post(
            #"https://linebot-wpp0.onrender.com/api/user/add",
            "https://digital-art-backend-nq89.onrender.com/api/user/add",
            json={"user_id": user_id}
        )
        response.raise_for_status()
        return True, "後端已成功記錄你的使用者資訊！"
    except Exception as e:
        return False, f"記錄時發生錯誤：{str(e)}"
@app.route("/liff-data", methods=["POST"])
def liff_data():
    data = request.get_json()
    logger.info(f"收到的 JSON 資料: {data}")
    
    user_id = data.get("userId")
    display_name = data.get("displayName")
    url_params = data.get("urlParams", {})
    universalId = data.get("universalId")
    
    if not user_id:
        logger.warning("沒有 userId，資料格式不正確")
        return jsonify({'status': 'error', 'message': '缺少 userId'}), 400

    logger.info(f"來自 LIFF 的使用者 ID：{user_id}")
    logger.info(f"使用者名稱：{display_name}")
    logger.info(f"URL 參數：{url_params}")
    logger.info(f"URL 參數：{universalId}")
    
    return jsonify({'status': 'success', 'message': '資料接收成功'})
    
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'
def create_rich_menu_1():
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_blob_api = MessagingApiBlob(api_client)
        areas = [
            RichMenuArea(
                bounds=RichMenuBounds(#地圖
                    x=0,
                    y=0,
                    width=1671,
                    height=1686
                ),
                action=URIAction(
                    label='開啟網站',
                    uri='https://www.google.com'
                )
            ),
            RichMenuArea(
                bounds=RichMenuBounds(#主線任務
                    x=1673,
                    y=0,
                    width=827,
                    height=852
                ),
                action=PostbackAction(#主線任務
                    label='打開圖片選單',
                    data = 'open_task_menu1'
                )
            ),
             RichMenuArea(
                bounds=RichMenuBounds(#支線任務
                    x=1699,
                    y=844,
                    width=831,
                    height=668
                ),
                action=PostbackAction(
                    label='打開圖片選單',
                    data='open_task_menu1'
                )
            ),
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=1672,
                    y=1508,
                    width=828,
                    height=178
                ),
                action=MessageAction(
                    label='HLEP',
                    text='HELP'
                )
            )
        ]
        rich_menu_to_create = RichMenuRequest(
            size=RichMenuSize(
                width=2500,
                height=1686,
            ),
            selected=True,
            name="圖文表單1",
            chat_bar_text="選單",
            areas=areas
        )
        rich_menu_id = line_bot_api.create_rich_menu(
            rich_menu_request=rich_menu_to_create
        ).rich_menu_id

        with open('static/menu.jpg', 'rb') as image:
            line_bot_blob_api.set_rich_menu_image(
                rich_menu_id=rich_menu_id,
                body=bytearray(image.read()),
                _headers={'Content-Type': 'image/jpeg'}
            )
        line_bot_api.set_default_rich_menu(rich_menu_id)

@line_handler.add(FollowEvent)#加入好友事件
def handle_follow(event):
    user_id = event.source.user_id
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="執子之手\n方知子醜")]
            )
        )
    try:
        response = requests.post(
            "https://digital-art-backend-nq89.onrender.com/api/user/add",
            json={"user_id": user_id}
        )
        response.raise_for_status()
        backend_reply = "後端已成功記錄你的使用者資訊！"
    except Exception as e:
        backend_reply = f"記錄時發生錯誤：{str(e)}"
@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    if event.source.type != 'user':
        return
    user_id = event.source.user_id
    text = event.message.text
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if text == "我討厭你":
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[StickerMessage(package_id="6136", sticker_id="10551378")] 
                )
            )
        elif text == "ID":
            try:
                response = requests.post(
                    "https://digital-art-backend-nq89.onrender.com/api/user/add",
                    json={"user_id": user_id}
                )
                response.raise_for_status()
                backend_reply = "後端已成功記錄你的使用者資訊！"
            except Exception as e:
                backend_reply = f"記錄時發生錯誤：{str(e)}"
        elif text == "link1":
             line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="我愛你")]
                )
            )
        elif text == "HELP":
            postback_icon = 'https://linebot-wpp0.onrender.com/static/t1.png'
            message_icon = 'https://linebot-wpp0.onrender.com/static/t2.png'
            datetime_icon = 'https://linebot-wpp0.onrender.com/static/t3.png'
            date_icon = 'https://linebot-wpp0.onrender.com/static/t1.png'
            time_icon = 'https://linebot-wpp0.onrender.com/static/t1.png'
            quickReply = QuickReply(
                items=[
                    QuickReplyItem(
                        action=PostbackAction(
                            label="創作理念",
                            data='Core',
                            display_text="不免俗的一大口好事多超強氣泡水挑戰"
                        ),
                        image_url=postback_icon
                    ),
                    QuickReplyItem(
                        action=PostbackAction(
                            label="主線任務",
                            data='MainTask',
                            display_text="主線任務跟煮麵線有關嗎?"
                        ),
                        image_url=message_icon
                    ),
                    QuickReplyItem(
                       action=PostbackAction(
                            label="支線任務",
                            data='SubTask',
                            display_text="蛤!還有支線D:?!"
                        ),
                        image_url=date_icon
                    ),
                    QuickReplyItem(
                        action=PostbackAction(
                            label="地圖",
                            data='Map',
                            display_text="地圖是做甚麼的?告訴我嘛~"
                        ),
                        image_url=time_icon
                    ),
                    QuickReplyItem(
                        action=PostbackAction(
                            label="歡迎內容",
                            data='Welcome',
                            display_text="我加你時你講了啥?再說一次嘛~啾咪<3"
                        ),
                        image_url=postback_icon
                    ),
                    QuickReplyItem(
                       action=PostbackAction(
                            label="聯絡我們",
                            data='Contact',
                            display_text="小哥哥小姐接我好想認識你們呀~<3"
                        ),
                        image_url=datetime_icon
                    ),
                ]
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text='請選擇項目',
                        quick_reply=quickReply
                    )]
                )
            )
        else:
        #reply_message
        #line_bot_api.reply_message
            result = line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="您好~這裡是自動回覆訊息\n點擊選單HELP或在聊天室輸入\"HELP\"了解更多\n對於這次的展覽有任何想法或疑惑都歡迎私訊我們的IG粉專:You_as_a_unit\n點擊下方連結快速加入\nhttps://liff.line.me/2007392080-yXExAKkE\n")]
            )
        )
    #https://digital-art-frontend.onrender.com/muu
    #sendDataTobackend(user_id)
@line_handler.add(PostbackEvent)
def handle_message(event):
    data = event.postback.data
    user_id = event.source.user_id
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if data == 'open_task_menu1':
            image_carousel_template = ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://linebot-wpp0.onrender.com/static/Lotus.jpg',
                        action=URIAction(
                            label='TouchToOpen',
                            #uri='https://digital-art-frontend.onrender.com/lotus'
                            uri = 'https://liff.line.me/2007392080-gEDLrwOD'
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://linebot-wpp0.onrender.com/static/Muu.jpg',
                        action=URIAction(
                            label='TouchToOpen',
                            #uri='https://digital-art-frontend.onrender.com/muu'
                            uri = 'https://liff.line.me/2007392080-L1Kjqd9K'
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://linebot-wpp0.onrender.com/static/ReStyle.jpg',
                        action=URIAction(
                            label='TouchToOpen',
                            #uri='https://digital-art-frontend.onrender.com/gender'
                            uri = 'https://liff.line.me/2007392080-BQjk8XQj'
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://linebot-wpp0.onrender.com/static/Phone.jpg',
                        action=URIAction(
                            label='TouchToOpen',
                            uri = 'https://liff.line.me/2007392080-ybnwboRn'
                        )
                    ),
                ]
            )
            image_carousel_message = TemplateMessage(
                alt_text='圖片輪播範本',
                template=image_carousel_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[image_carousel_message]
                )
            )
        elif data == 'Core':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text='這個作品以「像素藝術與互動體驗」方向構思，希望透過本作品讓觀眾參與到展品之中，而不單單只是觀看。以像素藝術為風格，創造出一個類似《Minecraft》這樣的像素風格遊戲世界。希望能用這樣的作品，激起同學們對於創新與科技的興趣和同學們對像素藝術的共鳴，並讓他們感受到沉浸式的互動體驗。')]
                )
            )
        elif data == 'MainTask':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='快去做，別磨叽>:0!')]
                )
            )
        elif data == 'SubTask':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='非常任性的創作者設計的支線任務，可能會讓你感到困惑或是迷失方向，但這正是創作者想要表達的意圖。支線任務不僅僅是為了完成某個目標，而是讓你在探索過程中發現更多的可能性和樂趣。希望你能享受這段旅程，並找到屬於自己的答案。總之，加一點好多胡椒鹽。')]
                )
            )
        elif data == 'Map':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text='這不只是任務地圖，而是一場探索，也是一場迷路。有時候，我們不是為了找到什麼，而是為了看見那些從沒注意過的角落—— 一張你沒拍過的照片、一本沒人借過的書，甚至是一頭你從沒見過的牛。')]
                )
            )
        elif data == 'Welcome':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='敬請期待')]
                )
            )
        elif data == 'Contact':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='這是聯絡方式')]
                )
            )
        else:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='無效的選項')]
                )
            )
create_rich_menu_1()  
if __name__ == "__main__":
    app.run()