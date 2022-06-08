from asyncio import Lock

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    ArgumentMatch,
    ArgResult,
)
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from library.depend import Switch, FunctionCall
from .util import BuildImage

saya = Saya.current()
channel = Channel.current()

channel.name("BuildImage")
channel.author("nullqwertyuiop")
channel.description("")

lock = Lock()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch(".build_image").help("匹配 .build_image"),
                    ArgumentMatch("--help", action="store_true", optional=True).help(
                        "显示该帮助文本"
                    )
                    @ "get_help",
                    ArgumentMatch("-w", "--width", type=int, optional=True).help(
                        "图片的宽度，必填"
                    )
                    @ "width",
                    ArgumentMatch("-h", "--height", type=int, optional=True).help(
                        "图片的高度，必填"
                    )
                    @ "height",
                    ArgumentMatch("-c", "--color", type=str, optional=True).help(
                        "图片的背景颜色"
                    )
                    @ "color",
                    ArgumentMatch("-m", "--mode", type=str, optional=True).help("图片的模式")
                    @ "mode",
                    ArgumentMatch("-fs", "--font-size", type=int, optional=True).help(
                        "文字的大小"
                    )
                    @ "font_size",
                    ArgumentMatch("-t", "--text", type=str, optional=True).help("插入的文字")
                    @ "text",
                    ArgumentMatch(
                        "-a", "--alpha", action="store_true", optional=True
                    ).help("是否为透明图片")
                    @ "alpha",
                ],
            )
        ],
        decorators=[Switch.check(channel.module), FunctionCall.record(channel.module)],
    )
)
async def build_image(
    app: Ariadne,
    event: MessageEvent,
    get_help: ArgResult,
    width: ArgResult,
    height: ArgResult,
    color: ArgResult,
    mode: ArgResult,
    font_size: ArgResult,
    text: ArgResult,
    alpha: ArgResult,
):
    if get_help.matched:
        return await app.sendMessage(
            event.sender.group if isinstance(event, GroupMessage) else event.sender,
            MessageChain(
                channel.content[0]
                .metaclass.inline_dispatchers[0]
                .get_help(".build_image", "通过指令构造一张图片")
            ),
        )
    if not (width.matched or height.matched):
        return await app.sendMessage(
            event.sender.group if isinstance(event, GroupMessage) else event.sender,
            MessageChain("必填参数未满足，请检查参数是否正确"),
        )
    if mode.result not in (
        "1",
        "CMYK",
        "F",
        "HSV",
        "I",
        "L",
        "LAB",
        "P",
        "RGB",
        "RGBA",
        "RGBX",
        "YCbCr",
    ):
        return await app.sendMessage(
            event.sender.group if isinstance(event, GroupMessage) else event.sender,
            MessageChain(
                "模式错误，支持的模式为：\n"
                "1. CMYK\n2. F\n3. HSV\n"
                "4. I\n5. L\n6. LAB\n"
                "7. P\n8. RGB\n9. RGBA"
                "\n10. RGBX\n11. YCbCr"
            ),
        )
    image = BuildImage(
        w=width.result,
        h=height.result,
        color=color.result,
        image_mode=mode.result or "RGBA",
        font_size=font_size.result or 30,
        is_alpha=alpha.matched,
    )
    if text.matched:
        await image.atext((0, 0), text.result.strip('"').strip("'"))
    await app.sendMessage(
        event.sender.group if isinstance(event, GroupMessage) else event.sender,
        MessageChain([Image(data_bytes=image.pic2bytes())]),
    )