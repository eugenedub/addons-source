#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2019  Matthias Kemmer
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

# ----------------------------------------------------------------------------
#
# GRAMPS modules
#
# ----------------------------------------------------------------------------
from gramps.gui.plug import MenuToolOptions, PluginWindows
from gramps.gen.plug.menu import NumberOption, BooleanOption
from gramps.gui.dialog import OkDialog
from gramps.gen.lib.date import Today
from gramps.gen.db import DbTxn

from gramps.gen.const import GRAMPS_LOCALE as glocale
try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext


# ----------------------------------------------------------------------------
#
# Tool Class
#
# ----------------------------------------------------------------------------
class SetPrivacyWindow(PluginWindows.ToolManagedWindowBatch):
    """Handles the Set Privacy Tool processing."""

    def get_title(self):
        return _("Set Privacy Tool")

    def run(self):
        self.db = self.dbstate.get_database()
        self.cnt = []
        opt = []
        for entry in ["years", "person", "event", "media", "no_date"]:
            opt.append(self.get_opt(entry))
        # Check if the user has ticked at least on category
        if True in opt[1:4]:
            self.lock_function(opt)
        else:
            OkDialog("Information", "Choose at least one category e.g. "
                     "'Persons' to progress", parent=self.window)

    def get_opt(self, name):
        """Get the options value for further processing.

        :param name: Name of the menu option
        :param name: string
        :returns: Value of the option
        :rtype: True, False or integer
        """
        menu = self.options.menu
        opt = menu.get_option_by_name(name)
        return opt.get_value()

    def lock_function(self, opt):
        """Lock objects depending on user selection and timeframe."""
        date = Today() - opt[0]
        lock_no_date = opt[4]
        if opt[1]:
            self.lock_persons(date, lock_no_date)
        if opt[2]:
            self.lock_events(date, lock_no_date)
        if opt[3]:
            self.lock_media(date, lock_no_date)
        txt = ""
        for entry in self.cnt:
            txt += "Set private: %d %s\n" % (entry[1], entry[0])
        for entry in self.cnt:
            txt += "Not private: %d %s\n" % (entry[2], entry[0])
        OkDialog("Set Privacy Tool", txt, parent=self.window)

    def lock_persons(self, date, lock_no_date):
        with DbTxn(_("Set Privacy Tool"), self.db, batch=True) as self.trans:
            self.db.disable_signals()
            person_list = list(self.db.iter_people())
            self.progress.set_pass(_('Set persons private..'),
                                   len(person_list))
            cnt = [0, 0]
            for Person in person_list:
                birth_ref = Person.get_birth_ref()
                if birth_ref:
                    birth = self.db.get_event_from_handle(birth_ref.ref)
                    birth_date = birth.get_date_object()
                    if birth_date.get_year() == 0 and lock_no_date:
                        Person.set_privacy(True)
                        cnt[0] += 1
                    elif birth_date.get_year() == 0 and not lock_no_date:
                        Person.set_privacy(False)
                        cnt[1] += 1
                    elif birth_date.get_year() != 0 and birth_date >= date:
                        Person.set_privacy(True)
                        cnt[0] += 1
                    else:
                        Person.set_privacy(False)
                        cnt[1] += 1
                else:
                    if lock_no_date:
                        Person.set_privacy(True)
                        cnt[0] += 1
                    else:
                        Person.set_privacy(False)
                        cnt[1] += 1
                self.db.commit_person(Person, self.trans)
                self.progress.step()
        self.db.enable_signals()
        self.db.request_rebuild()
        self.cnt.append(("persons", cnt[0], cnt[1]))

    def lock_events(self, date, lock_no_date):
        with DbTxn(_("Set Privacy Tool"), self.db, batch=True) as self.trans:
            self.db.disable_signals()
            event_list = list(self.db.iter_events())
            self.progress.set_pass(_('Set events private..'),
                                   len(event_list))
            cnt = [0, 0]
            for Event in event_list:
                event_date = Event.get_date_object()
                if event_date.get_year() == 0 and lock_no_date:
                    Event.set_privacy(True)
                    cnt[0] += 1
                elif event_date.get_year() == 0 and not lock_no_date:
                    Event.set_privacy(False)
                    cnt[1] += 1
                elif event_date.get_year() != 0 and event_date >= date:
                    Event.set_privacy(True)
                    cnt[0] += 1
                else:
                    Event.set_privacy(False)
                    cnt[1] += 1
                self.db.commit_event(Event, self.trans)
                self.progress.step()
        self.db.enable_signals()
        self.db.request_rebuild()
        self.cnt.append(("events", cnt[0], cnt[1]))

    def lock_media(self, date, lock_no_date):
        with DbTxn(_("Set Privacy Tool"), self.db, batch=True) as self.trans:
            self.db.disable_signals()
            media_list = list(self.db.iter_media())
            self.progress.set_pass(_('Set media private..'),
                                   len(media_list))
            cnt = [0, 0]
            for Media in media_list:
                media_date = Media.get_date_object()
                if media_date.get_year() == 0 and lock_no_date:
                    Media.set_privacy(True)
                    cnt[0] += 1
                elif media_date.get_year() == 0 and not lock_no_date:
                    Media.set_privacy(False)
                    cnt[1] += 1
                elif media_date.get_year() != 0 and media_date >= date:
                    Media.set_privacy(True)
                    cnt[0] += 1
                else:
                    Media.set_privacy(False)
                    cnt[1] += 1
                self.db.commit_media(Media, self.trans)
                self.progress.step()
        self.db.enable_signals()
        self.db.request_rebuild()
        self.cnt.append(("media", cnt[0], cnt[1]))


# ----------------------------------------------------------------------------
#
# Option Class
#
# ----------------------------------------------------------------------------
class SetPrivacyOptions(MenuToolOptions):
    """Handles the Set Privacy Tool menu options."""
    def __init__(self, name, person_id=None, dbstate=None):
        MenuToolOptions.__init__(self, name, person_id, dbstate)

    def add_menu_options(self, menu):
        self.person = BooleanOption(_("Persons"), False)
        menu.add_option(_("Option"), "person", self.person)

        self.event = BooleanOption(_("Events"), False)
        menu.add_option(_("Option"), "event", self.event)

        self.media = BooleanOption(_("Media"), False)
        menu.add_option(_("Option"), "media", self.media)

        self.no_date = BooleanOption(_("Always private if no date."), False)
        self.no_date.set_help(_("If checked, all objects without a date will "
                                "also be set private."))
        menu.add_option(_("Option"), "no_date", self.no_date)

        self.years = NumberOption(_("Years"), 0, 0, 2000)
        self.years.set_help(_("The time range in years from today you want to "
                              "set objects private.\n"
                              "'0 years' = remove privacy from all objects."))
        menu.add_option(_("Option"), "years", self.years)
