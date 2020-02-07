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

list_format = '[§c{0}§d] - {1}'
pagenum_format = '第 {0} 页，共 {1} 页'


class module:
    reload = 'm文件列表已重新加载'

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
    help = {
        'mcws midi模块': '在Minecraft中播放mid音乐',
        '--info': '-i 显示信息    \u00a7c-info',
        '--help': '-h -? 提供帮助/命令列表    \u00a7c-help',
        '--play': '-p 播放一个mid文件    \u00a7c-play <ID>',
        '--stop': '-st 停止播放    \u00a7c-stop',
        '--list': '-ls 列出mid文件    \u00a7c-list [页码]',
        '--search': '-s 搜索mid文件    \u00a7c-search <内容>',
        '--reload': '-re 重新加载mid文件列表    \u00a7c-reload'
    }
    info = '\u00a76mcws midi模块 \u00a7bby HYWT'
    midicount = "当前有 {0} 首 midi 音乐"
    stopping = "正在停止"
    stopped = '已停止'
    load_song = "正在加载 {0}..."
    reload = 'mid文件列表已重新加载'
    unknown_command = '未知命令。使用 .midi -h 查看可用命令列表。'


class worldedit:
    no_coordinate = '未设置坐标'
    coor_1_msg = '第一坐标设置为 ({0}) ({1})'
    coor_2_msg = '第二坐标设置为 ({0}) ({1})'
    fill_message = '已处理{0}个方块'


class import_error:
    midiplayer = '缺少依赖库, midi模块启动失败'
    pixel = '缺少依赖库, 像素画模块启动失败'
    avatardownload = ''


class pixel:
    image_info = '{0} 尺寸: {1}x{2} 大小: {3}'
    resize_info = '* 自动缩放到 {0}x{1}'


class xboxapi:
    login = '''-------------------------------
                    请登录xbox。
            -------------------------------
    '''
