import os
import sys
import webview

def get_html_path():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, 'index.html')

if __name__ == '__main__':
    html_file = get_html_path()
    window = webview.create_window(
        title='OM Picture Manager',
        url=html_file,
        width=1180,
        height=740,
        min_size=(950, 600),
        resizable=True
    )
    webview.start(gui='edgechromium')