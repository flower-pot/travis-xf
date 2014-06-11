#!/usr/bin/env python

import requests
import sys
import threading

from repository import Repository
from repository_list import RepositoryList
from preferences_window import PreferencesWindow
from build_status import BuildStatus
from gi.repository import AppIndicator3
from gi.repository import GObject, Gtk, GLib

REFRESH_INTERVAL = 3

class Indicator:
    def __init__(self):
        self.indicator = AppIndicator3.Indicator.new("travis-xf",
                                          "ubuntuone-client-idle",
                                          AppIndicator3.IndicatorCategory.APPLICATION_STATUS)

        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.repositories = RepositoryList()
        self.repositories.load()

        BuildStatus.active.set_indicator_icon(self.indicator)
        self.indicator.set_menu(self.build_menu())

        self.refresh_thread = None

        self.editing_preferences = False
        self.setup_refresh_timer()

    def on_preferences_activate(self, widget):
        self.preferences_window = PreferencesWindow(self.repositories, self.return_from_preferences_callback)
        self.editing_preferences = True

    def return_from_preferences_callback(self, new_repositories):
        # set new repositories and reset connected components
        BuildStatus.active.set_indicator_icon(self.indicator)
        self.repositories = new_repositories
        self.indicator.set_menu(self.build_menu())
        self.editing_preferences = False

    def build_menu(self):
        menu = Gtk.Menu()

        self.repositories.create_menu_items(menu)
        self.add_menu_item(menu, "Preferences", self.on_preferences_activate)
        self.add_menu_item(menu, "Quit", self.quit)

        return menu

    def add_menu_item(self, menu, title, activate_handler):
        item = Gtk.MenuItem(title)
        item.connect("activate", activate_handler)
        item.show()
        menu.append(item)

    def setup_refresh_timer(self):
        GLib.timeout_add_seconds(REFRESH_INTERVAL, self.check_all_build_statuses)

    def check_all_build_statuses(self):
        if not self.editing_preferences:
            self.repositories.set_indicator_icon(self.indicator)
        return True

    def quit(self, widget):
        self.repositories.save()
        Gtk.main_quit()
