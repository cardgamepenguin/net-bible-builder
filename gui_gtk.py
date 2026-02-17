# ---------------------------------------------------------------------------
# NET Bible (2nd Ed) Builder
# Copyright (C) 2026 The net-bible-builder Authors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# ---------------------------------------------------------------------------

import threading
from pathlib import Path

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib  # type: ignore

from core.builder import build_epub
from core.validate import validate_epub
from core.config import DEFAULT_OUTPUT


class BuilderWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="NET Bible EPUB Builder")
        self.set_default_size(500, 400)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        self.add(vbox)

        # Output path
        h_output = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        vbox.pack_start(h_output, False, False, 0)

        h_output.pack_start(Gtk.Label(label="Output:"), False, False, 0)
        self.output_entry = Gtk.Entry()
        self.output_entry.set_text(DEFAULT_OUTPUT)
        h_output.pack_start(self.output_entry, True, True, 0)

        # Options
        self.skip_cache_check = Gtk.CheckButton(label="Skip cache (force refresh)")
        vbox.pack_start(self.skip_cache_check, False, False, 0)

        self.validate_check = Gtk.CheckButton(label="Validate EPUB after build")
        vbox.pack_start(self.validate_check, False, False, 0)

        # Max workers
        h_workers = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        vbox.pack_start(h_workers, False, False, 0)
        h_workers.pack_start(Gtk.Label(label="Max workers:"), False, False, 0)
        self.workers_adj = Gtk.Adjustment(8, 1, 64, 1, 4, 0)
        self.workers_spin = Gtk.SpinButton(adjustment=self.workers_adj, climb_rate=1, digits=0)
        h_workers.pack_start(self.workers_spin, False, False, 0)

        # Max RPS
        h_rps = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        vbox.pack_start(h_rps, False, False, 0)
        h_rps.pack_start(Gtk.Label(label="Max requests/sec:"), False, False, 0)
        self.rps_adj = Gtk.Adjustment(2.0, 0.1, 10.0, 0.1, 1.0, 0)
        self.rps_spin = Gtk.SpinButton(adjustment=self.rps_adj, climb_rate=0.1, digits=1)
        h_rps.pack_start(self.rps_spin, False, False, 0)

        # Build button
        self.build_button = Gtk.Button(label="Build EPUB")
        self.build_button.connect("clicked", self.on_build_clicked)
        vbox.pack_start(self.build_button, False, False, 10)

        # Progress Bar
        self.progress_label = Gtk.Label(label="")
        vbox.pack_start(self.progress_label, False, False, 0)

        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        vbox.pack_start(self.progress_bar, False, False, 5)

        # Log view
        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_buffer = self.log_view.get_buffer()
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        scrolled.add(self.log_view)
        vbox.pack_start(scrolled, True, True, 0)

    def append_log(self, text: str):
        def _append():
            end_iter = self.log_buffer.get_end_iter()
            self.log_buffer.insert(end_iter, text + "\n")
            return False

        GLib.idle_add(_append)

    def _reset_progress(self):
        self.progress_label.set_text("")
        self.progress_bar.set_fraction(0)
        self.progress_bar.set_text("")

    def _update_progress(self, stage: str, current: int, total: int):
        fraction = current / total if total > 0 else 0
        self.progress_label.set_text(stage)
        self.progress_bar.set_fraction(fraction)
        self.progress_bar.set_text(f"{current} / {total}")
        return False  # for GLib.idle_add

    def on_build_clicked(self, button):
        self.build_button.set_sensitive(False)
        self._reset_progress()
        self.append_log("Starting build...")

        output = self.output_entry.get_text().strip()
        if not output:
            output = DEFAULT_OUTPUT

        skip_cache = self.skip_cache_check.get_active()
        validate = self.validate_check.get_active()
        max_workers = self.workers_spin.get_value_as_int()
        max_rps = self.rps_spin.get_value()

        def progress_handler(stage, current, total):
            GLib.idle_add(self._update_progress, stage, current, total)

        def worker():
            try:
                self.append_log("Building EPUB...")
                build_epub(
                    output_path=output,
                    skip_cache=skip_cache,
                    retries=3,
                    max_workers=max_workers,
                    max_rps=max_rps,
                    resume=True,
                    progress_callback=progress_handler,
                )
                self.append_log(f"Build complete: {output}")

                if validate:
                    self.append_log("Validating EPUB...")
                    ok = validate_epub(output)
                    self.append_log("Validation OK." if ok else "Validation reported issues.")
            except Exception as e:
                self.append_log(f"Error: {e}")
            finally:
                def final_ui_update():
                    self.build_button.set_sensitive(True)
                    return False
                GLib.idle_add(final_ui_update)

        threading.Thread(target=worker, daemon=True).start()


def main():
    win = BuilderWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
