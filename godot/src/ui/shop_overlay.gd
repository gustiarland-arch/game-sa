class_name ShopOverlay
extends Control
## Shop catalogue (port of ShopOverlay.java). Buying goes through QuestEngine.purchase.

var engine: QuestEngine
var _shop: Dictionary
var _on_close: Callable
var _on_buy: Callable
var _status := ""
var _close_btn: Button
var _buy: Array = []
var _panel := Rect2()


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	visible = false
	mouse_filter = Control.MOUSE_FILTER_STOP
	_close_btn = UiTheme.button("Selesai", 22, true)
	_close_btn.pressed.connect(close)
	add_child(_close_btn)


func open(shop_id: String, done: Callable, after_purchase: Callable) -> void:
	_shop = Data.quests.get("shops", {}).get(shop_id, {})
	_on_close = done; _on_buy = after_purchase
	if _shop.is_empty():
		if done.is_valid():
			done.call()
		return
	for b in _buy:
		b.queue_free()
	_buy = []
	for good in _shop.get("goods", []):
		Data.tex(_icon(good.item))  # load before draw
		var b := UiTheme.button("Beli • %d" % int(good.price), 19)
		b.pressed.connect(func():
			_status = engine.purchase(_shop.get("id", shop_id), good.item)
			if _status.begins_with("Membeli "):
				Audio.sfx("coin", 0.65)
				if _on_buy.is_valid():
					_on_buy.call()
			else:
				Audio.sfx("soft_wrong", 0.3))
		add_child(b)
		_buy.append(b)
	_shop["id"] = shop_id
	_status = "Pilih barang yang ingin dibeli."
	visible = true
	_close_btn.grab_focus.call_deferred()


func _icon(item: String) -> String:
	return str(Data.memory_book.get("items", {}).get(item, {}).get("icon", ""))


func close() -> void:
	if not visible:
		return
	visible = false
	var c := _on_close
	_on_close = Callable()
	if c.is_valid():
		c.call()


func _gap() -> float:
	return minf(104.0, (_panel.size.y - 230.0) / maxf(1, _buy.size()))


func _process(_dt: float) -> void:
	if not visible:
		return
	var w := minf(960, size.x - 40)
	var h := minf(620, size.y - 30)
	_panel = Rect2((size.x - w) / 2, (size.y - h) / 2, w, h)
	_close_btn.position = _panel.position + Vector2(w - 170, 24); _close_btn.size = Vector2(145, 54)
	var goods: Array = _shop.get("goods", [])
	for i in _buy.size():
		var g: Dictionary = goods[i]
		var b: Button = _buy[i]
		var top := 152 + i * _gap()     # Java y-up row at y + h - 171 - i*gap, height 56
		b.position = _panel.position + Vector2(w - 215, top); b.size = Vector2(176, 56)
		var owned := engine.p.has_item(g.item)
		b.disabled = owned or engine.p.coins < int(g.price)
		b.text = "Dimiliki" if owned else ("Kurang koin" if engine.p.coins < int(g.price) else "Beli • %d" % int(g.price))
	queue_redraw()


func _unhandled_key_input(e: InputEvent) -> void:
	if visible and e.pressed and e.keycode == KEY_ESCAPE:
		close()
		get_viewport().set_input_as_handled()


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Color(UiTheme.BG, 0.73))
	var p := _panel
	UiTheme.panel(Color("2f2545"), Color("57476f"), 22, 3, 10).draw(get_canvas_item(), p)
	UiTheme.draw_text(self, str(_shop.get("title", "")), p.position.x + 27, p.position.y + 18, 28, UiTheme.CREAM, "left", 0, "title")
	UiTheme.draw_text(self, "Penjual: %s    •    Saldo: %d koin" % [_shop.get("keeper", ""), engine.p.coins], p.position.x + 30, p.position.y + 84, 20, UiTheme.GOLD)
	var goods: Array = _shop.get("goods", [])
	for i in goods.size():
		var g: Dictionary = goods[i]
		var top := p.position.y + 138 + i * _gap()    # row panel: Java (yy - 10, 84) with yy = y + h - 171 - i*gap
		var row := Rect2(p.position.x + 24, top, p.size.x - 48, 84)
		UiTheme.panel(Color(1, 0.975, 0.965), Color("d9c6e0"), 14, 2, 0).draw(get_canvas_item(), row)
		draw_circle(row.position + Vector2(39, 44), 30, Color("f3e6ef"))
		var t := Data.tex(_icon(g.item))
		if t:
			draw_texture_rect(t, Rect2(row.position.x + 13, row.position.y + 18, 52, 52), false)
		UiTheme.draw_text(self, "%s — %d koin" % [g.name, int(g.price)], row.position.x + 78, row.position.y + 12, 22, UiTheme.INK, "left", p.size.x - 340, "bold")
		UiTheme.draw_text(self, str(g.get("desc", "")), row.position.x + 78, row.position.y + 44, 17, UiTheme.INK_SOFT, "left", p.size.x - 350)
	UiTheme.draw_text(self, _status, p.position.x + 28, p.position.y + p.size.y - 44, 18, UiTheme.GOLD, "left", p.size.x - 50)
