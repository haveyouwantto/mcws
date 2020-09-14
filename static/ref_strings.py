import sys

loading = '加载中...'

search_error = '搜索内容不能为空'
empty_result = '未找到任何结果'
page_error = '页数无效'
file_not_exists = '文件不存在'
command_error = '语法错误'
pyversion = 'Python ' + sys.version
version = ''
unknown_command = '未知命令。'
invaild_id = 'ID 无效'
exception = '发生了一个错误。详情见服务端控制台。'
fatal_exception = '发生了严重错误'

list_format = '[§c{0}§d] - {1}'
pagenum_format = '第 {0} 页，共 {1} 页'

webui = 'WebUI已启用，http://127.0.0.1:26363'


class module:
    reload = '文件列表已重新加载'
    help = {
        '--info': '显示信息    \u00a7c--info',
        '--help': '提供帮助/命令列表    \u00a7c--help',
        '--reload': '重新加载文件列表    \u00a7c--reload',
        '--list': '列出文件    \u00a7c--list [页码]',
        '--list-by-id':'根据文件id列出页面    \u00a7c--list-by-id [id]',
        '--search': '搜索文件    \u00a7c--search <内容>',
        '--list-config':'显示当前模块的配置信息    \u00a7c--list-config'
    }


class mcws:
    help = {
        '.info': '显示信息    \u00a7c.info',
        '.help': '提供帮助/命令列表    \u00a7c.help',
        '.function': '运行在相应的功能文件中找到的命令    \u00a7c.function <function>',
        '.midi': 'mcws midi 模块    \u00a7c.midi [命令]'
    }
    welcome = '欢迎使用mcws'
    info = '\u00a76mcws by HTWT'


class midiplayer:
    name = 'mcws midi模块'
    description = '在Minecraft中播放mid音乐'
    help = {
        '--play': '播放一个mid文件    \u00a7c--play <ID>',
        '--stop': '停止播放    \u00a7c--stop',
        '--playing': '显示正在播放的文件',
        '--loop': '设置播放模式    \u00a7c--loop <song|all>',
        '--list': '列出mid文件    \u00a7c--list [页码]',
        '--search': '搜索mid文件    \u00a7c--search <内容>',
        '--reload': '重新加载mid文件列表    \u00a7c--reload',
        '--from-url': '从互联网下载音乐进行播放    \u00a7c--from-url <URL>',
        '--keyboard': '设置是否显示键盘    \u00a7c--keyboard <0|1>',
        '--pan-by-pitch': '设置音高是否决定声音位置    \u00a7c--pan-by-pitch <0|1>'
    }
    info = '\u00a76mcws midi模块 \u00a7bby HYWT'
    midicount = "当前有 {0} 首 midi 音乐"
    stopping = "正在停止"
    stopped = '已停止'
    load_song = "正在加载 [\u00a7c{0}\u00a7d] - {1}... ({2})"
    reload = 'mid文件列表已重新加载'
    unknown_command = '未知命令。使用 .midi -h 查看可用命令列表。'
    keyboard_enable = '键盘显示: 开启'
    keyboard_disable = '键盘显示: 关闭'
    by_pitch_enable = '音高决定声音位置: 开启'
    by_pitch_disable = '音高决定声音位置: 关闭'
    playing = '正在播放: [\u00a7c{0}\u00a7d] - {1}'


class worldedit:
    no_coordinate = '未设置坐标'
    coor_1_msg = '第一坐标设置为 ({0}) ({1})'
    coor_2_msg = '第二坐标设置为 ({0}) ({1})'
    fill_message = '已处理{0}个方块'


class import_error:
    midiplayer = '缺少依赖库, midi模块启动失败 (mido)'
    pixel = '缺少依赖库, 像素画模块启动失败 (pillow)'
    avatardownload = '缺少依赖库，将禁用头像下载功能'
    webui = '缺少依赖库，将禁用WebUI'


class pixel:
    name = '像素画生成器'
    image_info = '{0} 尺寸: {1}x{2} 大小: {3}'
    resize_info = '* 自动缩放到 {0}x{1}'
    start = '开始绘制...'
    finish = '绘制完成'
    mode_help = [
        '    \u00a7c--- 像素画的放置模式说明 ---    ',
        '  \u00a7d--mode命令用于选择生成像素画的模式。本生成器支持',
        '8种不同的模式，可以划分为「与地面平行」(都有x和z)',
        '和「与地面垂直」(以y结尾)这两种类型。模式的命名依据是当',
        '图片的x,y坐标递增时，\u00a7cMinecraft坐标的增减情况。\u00a7d',
        '「与地面平行」',
        '  这类型模式生成的像素画是与地面平行的。在生成时，',
        '它将会把玩家所在的方块坐标设置成图片的左上角，并根据',
        '所选择的放置模式来计算位置。',
        '下图中 X 为玩家所站的位置，即图片坐标原点',
        '                  \u00a7cx               \u00a7d',
        '  X------------------------------>',
        '  |                              |',
        '  |                              |',
        '\u00a7cy \u00a7d|                              |',
        '  |                              |',
        '  |                              |',
        '  |                              |',
        '  V-------------------------------',
        '「与地面垂直」',
        '  这类型模式生成的像素画是与地面垂直的。和刚才类似，',
        '但是它将玩家所在的位置设置成图片的\u00a7c左下角。\u00a7d',
        '使用该模式时需要注意Minecraft的建筑高度限制问题。',
        '下图中 X 为玩家所站的位置。',
        '                  \u00a7cx               \u00a7d',
        '  /------------------------------>',
        '  |                              |',
        '  |                              |',
        '\u00a7cy \u00a7d|                              |',
        '  |                              |',
        '  |                              |',
        '  V                              |',
        '  X-------------------------------',
        '',
        '下面列出所有模式名称。'
    ]
    help = {
        '--list': '列出图片文件    \u00a7c--list [页码]',
        '--search': '搜索图片文件    \u00a7c--search <内容>',
        '--reload': '重新加载图片文件列表    \u00a7c--reload',
        '--draw': '将一张图片生成像素画    \u00a7c--draw <ID>',
        '--mode': '选择生成像素画的放置模式    \u00a7c--mode <模式>',
        '--man-mode': '有关放置模式的说明书    \u00a7c--man-mode',
        '--from-url': '从互联网下载图片进行绘制    \u00a7c--from-url <URL>'
    }
    set_mode = '将放置模式设置成 {0}'
    invaild_mode = '模式无效'
    current_mode = '当前模式: {0}'
    download_image = '正在获取 {0}...'
    mime_error = '文件类型无效: {0}'
    web_error = '无法访问 {0}'


class xboxapi:
    login = '''-------------------------------
                    请登录xbox。
            -------------------------------
    '''
