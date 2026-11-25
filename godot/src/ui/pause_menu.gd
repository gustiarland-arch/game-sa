class_name PauseMenu
extends Control
## Pause: continue, save, dialogue history, back to title (port of the GameScreen pause panel and
## DialogueHistoryOverlay).

signal resume
signal save_requested
signal quit_requested
signal book_requested

var _box: VBoxContainer
var _history: PanelContainer
var _history_text: RichTextLabel
var _status: Label


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	visible = false
	var dim := ColorRect.new(); dim.color = Color(UiTheme.BG, 0.72); dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	var center := CenterContainer.new(); center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(center)
	var panel := PanelContainer.new()
	var st := UiTheme.panel(Color(1, 0.975, 0.965, 0.98))
	st.content_margin_left = 34; st.content_margin_right = 34; st.content_margin_top = 26; st.content_margin_bottom = 26
	panel.add_theme_stylebox_override("panel", st)
	center.add_child(panel)
	_box = VBoxContainer.new()
	_box.add_theme_constant_override("separation", 12)
	panel.add_child(_box)
	var head := UiTheme.label("Jeda", 34, UiTheme.INK, "title")
	head.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_box.add_child(head)
	for item in [["Lanjutkan", func(): resume.emit(), true], ["Simpan", func(): save_requested.emit(), false],
			["Memory Book", func(): book_requested.emit(), false], ["Riwayat dialog", _show_history, false], ["Kembali ke judul", func(): quit_requested.emit(), false]]:
		var b := UiTheme.button(item[0], 22, item[2])
		b.custom_minimum_size = Vector2(320, 56)
		b.pressed.connect(item[1])
		_box.add_child(b)
	_status = UiTheme.label("", 16, UiTheme.INK_SOFT, "body")
	_status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_box.add_child(_status)
	# history overlay
	_history = PanelContainer.new()
	var hs := UiTheme.panel(Color(1, 0.975, 0.965, 0.99))
	hs.content_margin_left = 28; hs.content_margin_right = 28; hs.content_margin_top = 22; hs.content_margin_bottom = 22
	_history.add_theme_stylebox_override("panel", hs)
	_history.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_history.offset_left = 60; _history.offset_right = -60; _history.offset_top = 40; _history.offset_bottom = -40
	_history.visible = false
	add_child(_history)
	var hv := VBoxContainer.new()
	hv.add_theme_constant_override("separation", 10)
	_history.add_child(hv)
	hv.add_child(UiTheme.label("Riwayat dialog", 28, UiTheme.INK, "title"))
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	hv.add_child(scroll)
	_history_text = RichTextLabel.new()
	_history_text.bbcode_enabled = true
	_history_text.fit_content = true
	_history_text.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_history_text.add_theme_font_override("normal_font", UiTheme.font("body"))
	_history_text.add_theme_font_override("bold_font", UiTheme.font("bold"))
	_history_text.add_theme_font_size_override("normal_font_size", 20)
	_history_text.add_theme_font_size_override("bold_font_size", 20)
	_history_text.add_theme_color_override("default_color", UiTheme.INK)
	scroll.add_child(_history_text)
	var close := UiTheme.button("Tutup", 20, true)
	close.size_flags_horizontal = Control.SIZE_SHRINK_END
	close.pressed.connect(func(): _history.visible = false)
	hv.add_child(close)


var _lines: Array = []


func open(history: Array) -> void:
	_lines = history
	_status.text = ""
	_history.visible = false
	visible = true
	(_box.get_child(1) as Button).grab_focus.call_deferred()


func set_status(t: String) -> void:
	_status.text = t


func _show_history() -> void:
	var t := ""
	for e in _lines:
		t += "[b]%s[/b]  [color=#9b8ab8](hari %d)[/color]\n%s\n\n" % [str(e.get("speaker", "")).replace("[", "("), int(e.get("day", 1)), str(e.get("text", "")).replace("[", "(")]
	_history_text.text = t if t != "" else "Belum ada dialog."
	_history.visible = true
