# -*- coding: utf-8 -*-
"""Extract Simplified Chinese messages from Qt's own qt_zh_CN.ts, for merging
into Qqsp.zh_CN.qm (Qqsp never loads qt_*.qm, so its standard dialogs would
otherwise stay English)."""
import os
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
TS = os.path.join(HERE, os.pardir, 'src', 'qt_zh_CN.ts')

# contexts worth carrying over for a QSP player
CONTEXTS = [
    'QFileDialog', 'QFileSystemModel', 'QDialogButtonBox', 'QPlatformTheme',
    'QMessageBox', 'QFontDialog', 'QFontDatabase', 'QColorDialog',
    'QLineEdit', 'QTextControl', 'QAbstractSpinBox', 'QComboBox',
    'QApplication', 'QCoreApplication', 'QGuiApplication', 'QDialog',
    'QMenu', 'QMenuBar', 'QShortcut', 'QErrorMessage', 'QProgressDialog',
    'QToolButton', 'QCheckBox', 'QRadioButton', 'QDockWidget', 'QInputDialog',
    'QUnicodeControlCharacterMenu', 'QScrollBar',
]

# Qt 5.13's zh_CN catalogue has no QPlatformTheme context, yet that is where
# Qt takes the text of every standard dialog button from.
PLATFORM_THEME = [
    ('OK', '确定'),
    ('Save', '保存'),
    ('Save All', '全部保存'),
    ('Open', '打开'),
    ('&Yes', '是(&Y)'),
    ('Yes to &All', '全部都是(&A)'),
    ('&No', '否(&N)'),
    ('N&o to All', '全部否(&O)'),
    ('Abort', '中止'),
    ('Retry', '重试'),
    ('Ignore', '忽略'),
    ('Close', '关闭'),
    ('Cancel', '取消'),
    ('Discard', '放弃'),
    ('Help', '帮助'),
    ('Apply', '应用'),
    ('Reset', '重置'),
    ('Restore Defaults', '恢复默认值'),
]

# small wording fixes for the (old) official translations
FIXUP = {
    '撤消(&U)': '撤销(&U)',
    '恢复(&R)': '重做(&R)',
    '选择全部': '全选',
    '查看：': '查找范围：',
    '文件名称(&N)：': '文件名(&N)：',
    '我的计算机': '我的电脑',
    '抛弃': '放弃',
    '放弃(&A)': '中止(&A)',
    '你确认你想删除“%1“？': '确定要删除“%1”吗？',
    '“%1“是写保护的。\n你还是想删除它么？': '“%1”是写保护的。\n仍要删除吗？',
    '%1已经存在。\n你想要替换它么？': '%1 已存在。\n要替换它吗？',
    '文件%1\n没有找到。\n请核实已给定正确文件名。': '找不到文件 %1。\n请检查文件名是否正确。',
    '目录%1\n没有找到。\n请核实已给定正确目录名。': '找不到目录 %1。\n请检查目录名是否正确。',
    '最近的地方': '最近访问的位置',
    '未知的': '未知',
    '显示隐藏文件(&H)': '显示隐藏文件(&H)',
}


def load_messages():
    """Return list of (context, source, comment, translation)."""
    root = ET.parse(TS).getroot()
    out = []
    for ctx in root.findall('context'):
        name = ctx.findtext('name')
        if name not in CONTEXTS:
            continue
        for m in ctx.findall('message'):
            tnode = m.find('translation')
            if tnode is None or tnode.find('numerusform') is not None:
                continue
            tr = (tnode.text or '').strip()
            if not tr or tnode.get('type') == 'unfinished':
                continue
            tr = FIXUP.get(tr, tr)
            src = m.findtext('source') or ''
            cmt = m.findtext('comment') or ''
            out.append((name, src, cmt, tr))
    for src, tr in PLATFORM_THEME:
        out.append(('QPlatformTheme', src, '', tr))
    return out


if __name__ == '__main__':
    msgs = load_messages()
    print('extracted %d messages from %d contexts' % (len(msgs), len(CONTEXTS)))
    for m in msgs[:10]:
        print('  ', m)
