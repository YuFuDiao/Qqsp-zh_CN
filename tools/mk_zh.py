# -*- coding: utf-8 -*-
"""Build Qqsp.zh_CN.qm (Simplified Chinese) for Qqsp 1.9.0.

The message set is taken verbatim from the official Qqsp.ru.qm that ships
inside Qqsp.exe, so every tr() string of the shipped build is covered.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qm as Q

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, os.pardir, 'src', 'Qqsp.ru.qm')

ZH = {
    # ---------------- MainWindow ----------------
    'ToolBar': '工具栏',
    'Error': '错误',
    '&Quest': '任务(&Q)',
    'Open game...': '打开游戏...',
    'Restart game': '重新开始游戏',
    'Exit': '退出',
    '&Game': '游戏(&G)',
    'Open saved game...': '打开存档...',
    'Save game...': '保存游戏...',
    'Quick Load': '快速读取',
    'Quick Save': '快速保存',
    '&Settings': '设置(&S)',
    'Show / Hide': '显示 / 隐藏',
    'Captions': '面板标题',
    'Hotkeys for actions': '显示动作快捷键',
    'Window / Fullscreen mode': '窗口 / 全屏模式',
    'Display HTML code as plain text': '以纯文本显示 HTML 代码',
    'Options...': '选项...',
    '&Help': '帮助(&H)',
    'About...': '关于...',
    'Main desc': '主描述',
    'Objects': '对象',
    'Actions': '动作',
    'Additional desc': '附加描述',
    'Input area': '输入区域',
    'Image': '图像',
    'Info': '信息',
    'Input data': '输入数据',
    'Select game file': '选择游戏文件',
    'QSP games (*.qsp *.gam)': 'QSP 游戏 (*.qsp *.gam)',
    'Select saved game file': '选择存档文件',
    'Saved game files (*.sav)': '存档文件 (*.sav)',
    'Select file to save': '选择要保存的文件',
    ', ': ', ',
    '<h2>Qqsp</h2><p>Copyright &copy; 2017-2019, Sonnix</p>':
        '<h2>Qqsp</h2><p>版权所有 &copy; 2017-2019, Sonnix</p>',
    '<p>Application version: %1<br>QSP library version: %2<br>Qt library version: %3'
    '<br>Application compilation date: %4<br>Library compilation date: %5</p>':
        '<p>程序版本：%1<br>QSP 库版本：%2<br>Qt 库版本：%3'
        '<br>程序编译日期：%4<br>库编译日期：%5</p>',
    'About': '关于',

    # ---------------- OptionsDialog ----------------
    'Options': '选项',
    'Use custom font size': '使用自定义字号',
    'Use custom font': '使用自定义字体',
    'Select': '选择',
    'Custom background color': '自定义背景色',
    'Language': '语言',
    'Custom text color': '自定义文字颜色',
    'Custom link color': '自定义链接颜色',
    'Autostart last game': '启动时自动打开上次的游戏',
    'Separate config per game': '每个游戏使用独立配置',
    'Sound volume': '音量',
    'Disable video': '禁用视频',
    'Force autoplay and loop for video': '强制视频自动播放并循环',
    'HTML5 Extras (experimental)': 'HTML5 扩展（实验性）',
    'Cancel': '取消',
    'Ok': '确定',

    # ---------------- other contexts ----------------
    'OK': '确定',
    'Game file to open.': '要打开的游戏文件。',
}

LANGNAME = '简体中文'
LANGID = 'zh_CN'

# strings that the shipped build translates but that are missing from the
# official .ts/.qm files (verified by scanning Qqsp.exe's literals and its
# QCoreApplication::translate() call sites)
EXTRAS = [
    ('OptionsDialog', 'Use case insensitive paths', '使用不区分大小写的路径'),
]


def main():
    qm = Q.parse(open(SRC, 'rb').read())
    missing = []
    out = Q.QmFile()
    out.language = LANGID
    seen = set()
    for ctx, src, cmt, tr in qm.messages:
        if src in ('__LANGNAME__',):
            new = LANGNAME
        elif src in ('__LANGID__',):
            new = LANGID
        elif src in ZH:
            new = ZH[src]
        else:
            missing.append((ctx, src))
            new = tr
        out.messages.append((ctx, src, cmt, new))
        seen.add((ctx, src, cmt))
    if missing:
        print('WARNING untranslated:', missing)

    for ctx, src, tr in EXTRAS:
        if (ctx, src, '') not in seen:
            out.messages.append((ctx, src, '', tr))
            seen.add((ctx, src, ''))
            print('extra  : [%s] %r -> %r' % (ctx, src, tr))

    # merge Qt's own Simplified Chinese strings (standard dialogs)
    import qt_zh
    added = skipped = 0
    for ctx, src, cmt, tr in qt_zh.load_messages():
        if (ctx, src, cmt) in seen:
            skipped += 1
            continue
        seen.add((ctx, src, cmt))
        out.messages.append((ctx, src, cmt, tr))
        added += 1
    print('merged Qt messages: +%d (skipped %d duplicates)' % (added, skipped))

    data = Q.build(out)
    dst = os.path.join(HERE, os.pardir, 'out', 'Qqsp.zh_CN.qm')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, 'wb').write(data)
    print('wrote %s (%d bytes, %d messages)' % (dst, len(data), len(out.messages)))
    # verify by re-parsing
    chk = Q.parse(open(dst, 'rb').read())
    assert len(chk.messages) == len(out.messages)
    for (c1, s1, _, t1), (c2, s2, _, t2) in zip(out.messages, chk.messages):
        assert (c1, s1, t1) == (c2, s2, t2), (c1, s1, t1, c2, s2, t2)
    print('verify OK')


if __name__ == '__main__':
    main()
