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
import requests
import json
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
CHANAL_ACCESS_TOKEN = 'C+EEXYfa4rNMmrTRCnPYVZwH2P96JBBjcdLxt7AEcr9P70YfMjv08WkD4CSyNZFeMiBl9PR+Q89Jcjk1ygvAtKBIdcyg8bEXa8qZNENMf2942IEOwtzQOqYC7XPGJxYDbgFxCbP8zioGAcS4MH9jsgdB04t89/1O/w1cDnyilFU='
configuration = Configuration(access_token=CHANAL_ACCESS_TOKEN)
handler = WebhookHandler('368027c375e4ee5435a7156aa38ee2d4')

@app.route("/liff-data", methods=["POST"])
def liff_data():
    try:
        data = request.get_json()
        id_token = data.get("idToken")
        name = data.get("name")

        print(f"收到的 ID Token: {id_token}")
        print(f"使用者名稱: {name}")

        return jsonify({"message": f"資料已收到：{name}"})
    except Exception as e:
        print(f"接收資料失敗: {str(e)}")
        return jsonify({"message": "接收資料失敗"}), 500

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
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
                bounds=RichMenuBounds(
                    x=0,
                    y=0,
                    width=1669,
                    height=1686
                ),
                action=URIAction(
                    label='開啟網站',
                    uri='https://www.google.com'
                )
            ),
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=1672,
                    y=0,
                    width=828,
                    height=836
                ),
                action=PostbackAction(
                    label='打開圖片選單',
                    data='open_task_menu'
                )
            ),
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=1672,
                    y=838,
                    width=828,
                    height=848
                ),
                action=URIAction(
                    label='開啟網站',
                    uri='https://www.google.com'
                )
            )
        ]
        rich_menu_to_create = RichMenuRequest(
            size=RichMenuSize(
                width=2500,
                height=1686,
            ),
            selected=True,
            name="圖文選單1",
            chat_bar_text="查看更多資訊",
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

@handler.add(FollowEvent)#加入好友事件
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
    # try:
    #     response = requests.post(
    #     "https://digital-art-backend-nq89.onrender.com/api/user/add",
    #     json={"user_id": user_id}
    #     )
    #     response.raise_for_status()
    #     backend_reply = "後端已成功記錄你的使用者資訊！"
    # except Exception as e:
    #     backend_reply = f"記錄時發生錯誤：{str(e)}"

@handler.add(MessageEvent, message=TextMessageContent)
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
                    #messages=[TextMessage(text="我愛你")]
                    messages=[StickerMessage(package_id="6136", sticker_id="10551378")] 
                )
            )
        elif text == "提示":#輸出音訊檔案
            url = request.url_root + "static/Mozart1.mp3"
            url = url.replace("http", "https")
            app.logger.info("url=",url)
            duration = 60000 #in milliseconds
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        AudioMessage(original_content_url=url,duration=duration)
                    ]
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
        else:
        #reply_message
        #line_bot_api.reply_message
            result = line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="回你了喔")]
            )
        )
    #https://digital-art-frontend.onrender.com/muu
@handler.add(PostbackEvent)
def handle_message(event):
    data = event.postback.data
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if data == 'open_task_menu':
            url = request.url_root + 'static/'
            url = url.replace("http", "https")
            app.logger.info("url=" + url)
            image_carousel_template = ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url=url+'cat1.jpg',
                        action=PostbackAction(
                            label='任務1',
                            data = 'task1'
                        )
                    ),
                    ImageCarouselColumn(
                        image_url=url+'cat2.jpg',
                        action=PostbackAction(
                            label='任務2',
                            data = 'task2'
                        )
                    ),
                    ImageCarouselColumn(
                        image_url=url+'cat3.jpg',
                        action=PostbackAction(
                            label='任務3',
                            data = 'task3'
                        )
                    ),
                    ImageCarouselColumn(
                        image_url=url+'cat4.jpg',
                        action=PostbackAction(
                            label='任務4',
                            data = 'task4'
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
        elif data == 'task1':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='這是任務1的詳細說明')]
                )
            )
        elif data == 'task2':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='這是任務2的詳細說明')]
                )
            )
        elif data == 'task3':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='這是任務3的詳細說明')]
                )
            )
        elif data == 'task4':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='這是任務4的詳細說明')]
                )
            )
import os
create_rich_menu_1()   
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
    #app.run()