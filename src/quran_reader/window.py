import os

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')
from gi.repository import Adw, Gtk, Gdk, GLib, Gio

from .constants import APP_CSS, DATA_DIR, HAS_TEXT_DB, PAGES_DIR, SURAHS, SURAH_BY_NUM
from .db import BASMALA, SURAH_FIRST_PAGE, load_ayahs


class QuranBrowser(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id='io.github.hihebark.QuranReader',
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.lang          = 'ar'
        self.mode          = 'mushaf'
        self.current_page  = 1
        self.current_surah = None
        self._filtered     = list(SURAHS)

    # ------------------------------------------------------------------ lifecycle

    def do_activate(self):
        display = Gdk.Display.get_default()

        provider = Gtk.CssProvider()
        provider.load_from_data(APP_CSS)
        Gtk.StyleContext.add_provider_for_display(
            display, provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        Gtk.IconTheme.get_for_display(display).add_search_path(
            os.path.join(DATA_DIR, "icons")
        )

        self.window = Adw.ApplicationWindow(application=self)
        self.window.set_title("Quran Browser")
        self.window.set_default_size(1020, 760)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        root.append(self._build_header())

        self.paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.paned.set_vexpand(True)
        self.paned.set_position(270)
        self.paned.set_shrink_start_child(False)
        self.paned.set_shrink_end_child(False)
        self.paned.set_start_child(self._build_sidebar())
        self.paned.set_end_child(self._build_content())
        self.paned.set_direction(Gtk.TextDirection.RTL)
        root.append(self.paned)

        key_ctrl = Gtk.EventControllerKey()
        key_ctrl.connect("key-pressed", self._on_key_pressed)
        self.window.add_controller(key_ctrl)

        self.window.set_content(root)
        self.window.present()
        self._go_to_page(1)

    # ------------------------------------------------------------------ header

    def _build_header(self):
        header = Adw.HeaderBar()

        mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        mode_box.add_css_class("linked")
        self.btn_mushaf = Gtk.ToggleButton(label="Mushaf")
        self.btn_text   = Gtk.ToggleButton(label="Text")
        self.btn_text.set_group(self.btn_mushaf)
        self.btn_mushaf.set_active(True)
        if not HAS_TEXT_DB:
            self.btn_text.set_sensitive(False)
            self.btn_text.set_tooltip_text("Run scripts/build_text_db.py first")
        self.btn_mushaf.connect("toggled", self._on_mode_toggled)
        self.btn_text.connect("toggled", self._on_mode_toggled)
        mode_box.append(self.btn_mushaf)
        mode_box.append(self.btn_text)
        header.pack_start(mode_box)

        lang_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        lang_box.add_css_class("linked")
        self.btn_ar = Gtk.ToggleButton(label="AR")
        self.btn_en = Gtk.ToggleButton(label="EN")
        self.btn_en.set_group(self.btn_ar)
        self.btn_ar.set_active(True)
        self.btn_ar.connect("toggled", self._on_lang_toggled)
        self.btn_en.connect("toggled", self._on_lang_toggled)
        lang_box.append(self.btn_ar)
        lang_box.append(self.btn_en)
        header.pack_end(lang_box)

        return header

    # ------------------------------------------------------------------ sidebar

    def _build_sidebar(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        search = Gtk.SearchEntry()
        search.set_placeholder_text("Search surah...")
        search.set_margin_top(10)
        search.set_margin_bottom(6)
        search.set_margin_start(10)
        search.set_margin_end(10)
        search.connect("search-changed", self._on_search_changed)
        box.append(search)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        self.surah_listbox = Gtk.ListBox()
        self.surah_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        scrolled.set_child(self.surah_listbox)
        box.append(scrolled)

        self._populate_surah_list(SURAHS)
        return box

    def _populate_surah_list(self, surahs):
        while child := self.surah_listbox.get_first_child():
            self.surah_listbox.remove(child)
        for num, ar, en, trans, _ in surahs:
            row = Adw.ActionRow()
            if self.lang == 'ar':
                row.set_title(f"{num}. {ar}")
                row.set_subtitle(en)
            else:
                row.set_title(f"{num}. {en}")
                row.set_subtitle(trans)
            row.surah_number = num
            row.set_activatable(True)
            row.connect("activated", self._on_surah_activated)
            self.surah_listbox.append(row)

    # ------------------------------------------------------------------ content stack

    def _build_content(self):
        self.content_stack = Gtk.Stack()
        self.content_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.content_stack.set_vexpand(True)
        self.content_stack.set_hexpand(True)
        self.content_stack.add_named(self._build_mushaf_view(), "mushaf")
        self.content_stack.add_named(self._build_text_view(),   "text")
        return self.content_stack

    # ------------------------------------------------------------------ mushaf view

    def _build_mushaf_view(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.add_css_class("mushaf-page")

        self.page_picture = Gtk.Picture()
        self.page_picture.set_vexpand(True)
        self.page_picture.set_hexpand(True)
        self.page_picture.set_can_shrink(True)
        self.page_picture.set_content_fit(Gtk.ContentFit.CONTAIN)
        box.append(self.page_picture)

        nav = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        nav.set_halign(Gtk.Align.CENTER)
        nav.set_margin_top(8)
        nav.set_margin_bottom(12)

        self.btn_prev = Gtk.Button(label="\u2190")
        self.btn_prev.connect("clicked", lambda _: self._go_to_page(self.current_page - 1))
        nav.append(self.btn_prev)

        self.page_label = Gtk.Label()
        self.page_label.set_width_chars(10)
        nav.append(self.page_label)

        self.btn_next = Gtk.Button(label="\u2192")
        self.btn_next.connect("clicked", lambda _: self._go_to_page(self.current_page + 1))
        nav.append(self.btn_next)

        box.append(nav)
        return box

    def _go_to_page(self, page: int):
        page = max(1, min(604, page))
        self.current_page = page
        path = os.path.join(PAGES_DIR, f"{page:03d}.svg")
        self.page_picture.set_file(
            Gio.File.new_for_path(path) if os.path.exists(path) else None
        )
        self.page_label.set_text(f"{page} / 604")
        self.btn_prev.set_sensitive(page > 1)
        self.btn_next.set_sensitive(page < 604)

    # ------------------------------------------------------------------ text view

    def _build_text_view(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.text_title = Gtk.Label()
        self.text_title.set_markup("<span size='large'>Select a Surah</span>")
        self.text_title.set_margin_top(14)
        self.text_title.set_margin_bottom(14)
        box.append(self.text_title)
        box.append(Gtk.Separator())

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        self.ayah_listbox = Gtk.ListBox()
        self.ayah_listbox.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        self.ayah_listbox.add_css_class("boxed-list")
        self.ayah_listbox.set_margin_start(12)
        self.ayah_listbox.set_margin_end(12)
        self.ayah_listbox.set_margin_top(12)
        self.ayah_listbox.set_margin_bottom(12)
        scrolled.set_child(self.ayah_listbox)
        box.append(scrolled)

        return box

    def _load_text(self, surah_number: int):
        while child := self.ayah_listbox.get_first_child():
            self.ayah_listbox.remove(child)

        s = SURAH_BY_NUM[surah_number]
        if self.lang == 'ar':
            self.text_title.set_markup(
                f"<span size='x-large' font_weight='bold'>{s[1]}</span>"
                f"  <span size='small' foreground='gray'>{s[2]}</span>"
            )
        else:
            self.text_title.set_markup(
                f"<span size='x-large' font_weight='bold'>{s[2]}</span>"
                f"  <span size='small' foreground='gray'>{s[3]}</span>"
            )

        rows = load_ayahs(surah_number)
        if not rows:
            return

        # Basmala is prepended to ayah 1 by the source data for all surahs
        # except Al-Fatihah (1, where it IS ayah 1) and At-Tawbah (9, no Basmala).
        if surah_number not in (1, 9) and rows[0][1].startswith(BASMALA):
            self.ayah_listbox.append(self._build_basmala_row())
            n, ar, en = rows[0]
            rows[0] = (n, ar[len(BASMALA):].lstrip(), en)

        for ayah_num, arabic, english in rows:
            self.ayah_listbox.append(
                self._build_ayah_row(surah_number, ayah_num, arabic, english)
            )

    def _build_basmala_row(self):
        row = Gtk.ListBoxRow()
        row.set_selectable(False)
        label = Gtk.Label()
        label.set_markup(f"<span font='22'>{BASMALA}</span>")
        label.set_halign(Gtk.Align.CENTER)
        label.set_margin_top(20)
        label.set_margin_bottom(20)
        row.set_child(label)
        return row

    def _build_ayah_row(self, surah_num: int, ayah_num: int, arabic: str, english: str):
        row = Gtk.ListBoxRow()
        row.surah_number = surah_num
        row.ayah_number  = ayah_num
        row.arabic_text  = arabic
        row.english_text = english

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        outer.set_margin_start(16)
        outer.set_margin_end(16)
        outer.set_margin_top(16)
        outer.set_margin_bottom(16)

        # Arabic row: badge (verse-end marker) on the left, text right-aligned
        ar_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        badge = Gtk.Label(label=str(ayah_num))
        badge.add_css_class("ayah-badge")
        badge.set_valign(Gtk.Align.CENTER)
        ar_row.append(badge)

        ar_label = Gtk.Label()
        ar_label.set_markup(f"<span font='22'>{GLib.markup_escape_text(arabic)}</span>")
        ar_label.set_wrap(True)
        ar_label.set_wrap_mode(Gtk.WrapMode.WORD)
        ar_label.set_selectable(True)
        ar_label.set_hexpand(True)
        ar_label.set_halign(Gtk.Align.FILL)
        ar_label.set_xalign(1.0)
        ar_label.set_justify(Gtk.Justification.RIGHT)
        ar_row.append(ar_label)

        outer.append(ar_row)

        en_label = Gtk.Label(label=english)
        en_label.set_wrap(True)
        en_label.set_wrap_mode(Gtk.WrapMode.WORD)
        en_label.set_selectable(True)
        en_label.set_xalign(0.0)
        en_label.set_hexpand(True)
        en_label.add_css_class("dim-label")
        en_label.add_css_class("ayah-english")
        outer.append(en_label)

        row.set_child(outer)

        gesture = Gtk.GestureClick(button=3)
        gesture.connect("pressed", self._on_ayah_right_click, row)
        row.add_controller(gesture)

        return row

    def _on_ayah_right_click(self, _gesture, _n, x, y, row):
        self.ayah_listbox.select_row(row)

        menu = Gio.Menu()
        menu.append("Copy Arabic",    "app.copy-arabic")
        menu.append("Copy English",   "app.copy-english")
        menu.append("Copy Reference", "app.copy-reference")

        for name, text in [
            ("copy-arabic",    row.arabic_text),
            ("copy-english",   row.english_text),
            ("copy-reference", f"{row.surah_number}:{row.ayah_number}"),
        ]:
            action = Gio.SimpleAction(name=name)
            action.connect("activate", self._copy_to_clipboard, text)
            self.remove_action(name)
            self.add_action(action)

        popover = Gtk.PopoverMenu(menu_model=menu)
        popover.set_parent(row)
        rect = Gdk.Rectangle()
        rect.x, rect.y, rect.width, rect.height = int(x), int(y), 1, 1
        popover.set_pointing_to(rect)
        popover.popup()

    def _copy_to_clipboard(self, _action, _param, text: str):
        self.window.get_clipboard().set(text)

    # ------------------------------------------------------------------ event handlers

    def _on_surah_activated(self, row):
        self.current_surah = row.surah_number
        if self.mode == 'mushaf':
            self._go_to_page(SURAH_FIRST_PAGE.get(self.current_surah, 1))
        else:
            self._load_text(self.current_surah)

    def _on_search_changed(self, entry):
        text = entry.get_text().lower()
        self._filtered = [s for s in SURAHS if
                          text in s[1] or
                          text in s[2].lower() or
                          text in str(s[0])]
        self._populate_surah_list(self._filtered)

    def _on_mode_toggled(self, _btn):
        new_mode = 'mushaf' if self.btn_mushaf.get_active() else 'text'
        if new_mode == self.mode:
            return
        self.mode = new_mode
        self.content_stack.set_visible_child_name(new_mode)
        if new_mode == 'text' and self.current_surah:
            self._load_text(self.current_surah)

    def _on_lang_toggled(self, _btn):
        new_lang = 'ar' if self.btn_ar.get_active() else 'en'
        if new_lang == self.lang:
            return
        self.lang = new_lang
        self.paned.set_direction(
            Gtk.TextDirection.RTL if new_lang == 'ar' else Gtk.TextDirection.LTR
        )
        self._populate_surah_list(self._filtered)
        if self.mode == 'text' and self.current_surah:
            self._load_text(self.current_surah)

    def _on_key_pressed(self, _ctrl, keyval, _keycode, _state):
        if self.mode != 'mushaf':
            return False
        if keyval in (Gdk.KEY_Right, Gdk.KEY_Page_Down):
            self._go_to_page(self.current_page + 1)
            return True
        if keyval in (Gdk.KEY_Left, Gdk.KEY_Page_Up):
            self._go_to_page(self.current_page - 1)
            return True
        return False
