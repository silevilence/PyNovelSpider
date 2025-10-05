from nicegui import app, ui

app.native.window_args["resizable"] = True
app.native.start_args["debug"] = True
app.native.settings["ALLOW_DOWNLOADS"] = True

with ui.row():
    ui.select({1: "Syosetu", 2: "Syosetu R18"}, label="类型：", value=1)
    ui.input(label="URL：").classes("w-full")
    ui.button("获取信息")

columns = [
    {"name": "index", "label": "序号", "field": "index", "sortable": True},
    {"name": "title", "label": "标题", "field": "title", "sortable": True},
    {"name": "state", "label": "下载状态", "field": "state"},
]

with ui.row().classes("w-full"):
    ui.table(
        columns=columns,
        rows=[],
        row_key="index",
        pagination=True,
    ).classes("w-full")

ui.run(native=True, window_size=(1366, 768), fullscreen=False)
