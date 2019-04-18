'''
1
self.name_in.text

2
self.note.text

3
self.month_in
self.day_in
self.year_in
self.type.text
self.deadline.active
self.reminder.active
self.exclusive.active

#4
self.st_hour
self.st_minute
self.start_time.am.active
self.start_time.pm.active
self.st_concrete.active
self.st_flex.text
self.et_hour
self.et_minute
self.end_time.am.active
self.end_time.pm.active
self.et_concrete.active
self.et_flex.text

5
self.h_duration.text
self.m_duration.text
self.every_in
self.For_in
self.every_units.text
self.For_units.text

6
self.group.text
self.project.text
'''


import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics.instructions import Callback
from kivy.uix.carousel import Carousel
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.roulettescroll import RouletteScrollEffect
from kivy.graphics import Color, Rectangle
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.checkbox import CheckBox
from kivy.uix.switch import Switch
from kivy.uix.spinner import Spinner
from kivy.lang import Builder
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock
from kivy.animation import Animation

# Other imports
import inspect
from datetime import datetime, date

# Custom Imports
import main


class Task_Mgmt(TabbedPanel):
    def __init__(self, conn=None, **kwargs):
        super(Task_Mgmt, self).__init__(**kwargs)
        self.conn = conn
        self.cur = self.conn.cursor()
        self.in_error = False

        # self.do_default_tab = False
        self.add_tab = TabbedPanelItem(text='Add/Edit', on_touch_down=self.add_tab_touch)
        self.add_widget(self.add_tab)
        self.default_tab = self.add_tab

        self.t1_content = GridLayout(rows=2, cols=1)
        self.add_tab.add_widget(self.t1_content)

        self.form = GridLayout(cols=1, rows=7, spacing=3, padding=3)
        self.t1_content.add_widget(self.form)

        # row 1 (Name)
        self.row1 = GridLayout(rows=1, cols=1, size_hint_y=.5)
        self.form.add_widget(self.row1)
        self.name_in = TextInput(multiline=False, hint_text='Name', padding=1, write_tab=False, on_text_validate=self.save_task, text='')
        self.name_in.bind(size=self.scale_text)
        self.row1.add_widget(self.name_in)

        # row 2 (Note/Description)
        self.row2 = GridLayout(rows=1, cols=1, size_hint_y=1)
        self.form.add_widget(self.row2)
        self.note = TextInput(hint_text='Note', padding=1, write_tab=False, on_text_validate=self.save_task, text='')
        self.note.bind(size=self.scale_text)
        self.row2.add_widget(self.note)

        # row 3 (Date, Type)
        self.row3 = GridLayout(cols=2, rows=1, size_hint_y=2)
        self.form.add_widget(self.row3)
        self.r3c1 = GridLayout(cols=1, rows=2, padding=(0, 0, 5, 0))
        self.row3.add_widget(self.r3c1)
        self.r3c1.add_widget(Label(text='Date', size_hint_y=1/5))

        # date scroller container
        self.date_scroll = self.date_scroller()
        self.r3c1.add_widget(self.date_scroll)
        for m in self.month_grid.children:
            if int(m.text) == int(date.today().month):
                month = m
        self.month_scroll.scroll_to(month, padding=2, animate=True)
        for d in self.day_grid.children:
            if int(d.text) == int(date.today().day):
                day = d
        self.day_scroll.scroll_to(day, padding=0, animate=True)

        # type spinner
        self.r3c2 = GridLayout(cols=1, rows=3)
        self.r3c2.add_widget(Label(text='Type', size_hint_y=1/5))
        self.type_space = GridLayout(cols=1, rows=2, spacing=(0, 5), size_hint_y=2/3)
        self.r3c2.add_widget(self.type_space)

        self.type = Button(text='General')
        self.type_list = DropDown(max_height=288)

        types = ['General', 'School', 'Work', 'Home', 'Other', 'Custom']
        for i in types:
            b = Button(text=i, size_hint_y=None, height=48)
            b.bind(on_release=lambda b: self.type_list.select(b.text))
            self.type_list.add_widget(b)
            self.cur.execute("SELECT * FROM _types")
            # print(self.cur.fetchall())
            if len(self.cur.fetchall()) == 0:
                self.cur.execute('INSERT INTO _types VALUES(?, ?)', (None, i))
                self.conn.commit()

        self.type.bind(on_release=self.type_list.open)
        self.type_list.bind(on_select=lambda instance, x: setattr(self.type, 'text', x))
        self.type.bind(text=self.apply_type, size=self.scale_text)
        self.type_space.add_widget(self.type)

        self.custom_type = GridLayout(rows=1, cols=2)
        self.custom_type_input = Label(text='')
        self.type_space.add_widget(self.custom_type)

        self.checkboxes = GridLayout(rows=2, cols=3, size_hint_y=1/3)
        self.checkboxes.add_widget(Label(text='Deadline'))
        self.checkboxes.add_widget(Label(text='Reminder'))
        self.checkboxes.add_widget(Label(text='Exclusive'))
        self.deadline = CheckBox(group='r3')
        self.reminder = CheckBox(group='r3')
        self.exclusive = CheckBox(group='r3')
        self.checkboxes.add_widget(self.deadline)
        self.checkboxes.add_widget(self.reminder)
        self.checkboxes.add_widget(self.exclusive)
        self.r3c2.add_widget(self.checkboxes)

        self.row3.add_widget(self.r3c2)

        # row 4 (Start & End Times)
        self.row4 = GridLayout(cols=2, rows=2, size_hint_y=2, spacing=(5, 0))

        self.r4c1 = GridLayout(rows=2, cols=2, size_hint_x=2)
        self.start_time = GridLayout(cols=3, rows=1, size_hint_x=2)
        self.row4.add_widget(Label(text='Start', size_hint_y=1/5))
        self.row4.add_widget(Label(text='End', size_hint_y=1/5))
        self.start_time = self.time_scroller(self.start_time)
        self.r4c1.add_widget(self.start_time)
        self.row4.add_widget(self.r4c1)

        self.r4c4 = GridLayout(rows=2, cols=2, size_hint_x=2) # s_h_x may change
        self.end_time = GridLayout(cols=3, rows=1, size_hint_x=2)

        self.end_time.scroll = self.time_scroller(self.end_time)
        self.r4c4.add_widget(self.end_time)
        self.row4.add_widget(self.r4c4)
        self.form.add_widget(self.row4)

        # row 5 (Duration & Repeat)
        self.row5 = GridLayout(cols=1, rows=2, size_hint_y=1.25) # changed cols from 2 to 1
        # self.row5.add_widget(Label(text='Duration', size_hint=(1/5, 1/3)))
        self.repeat_labels = GridLayout(cols=2, rows=1, size_hint=(4/5, 1/3))
        self.row5.add_widget(self.repeat_labels)
        self.repeat_labels.add_widget(Label(text='Repeat Every'))
        self.repeat_labels.add_widget(Label(text='Repeat For'))

        self.repeat_area = GridLayout(cols=2, rows=1, spacing=(5, 1))
        self.row5.add_widget(self.repeat_area)

        self.every = GridLayout(cols=1, rows=2)
        self.every_scroll = ScrollView(do_scroll_y=False)
        self.every_grid = GridLayout(rows=1, size_hint=(None, 1))
        self.every_grid.bind(minimum_width=self.every_grid.setter('width'))
        for i in range(1, 13):
            b = Button(text=str(i), size_hint_x=None, width=40)
            b.bind(size=self.scale_text_btn, on_press=self.set_btn)
            self.every_grid.add_widget(b)
        self.every_scroll.add_widget(self.every_grid)
        self.every.add_widget(self.every_scroll)
        self.every_amt = 0
        self.every_grid_chosen = None

        self.every_units = Spinner(text='Unit', values=('Minute(s)', 'Hour(s)', 'Day(s)', 'Week(s)', 'Month(s)', 'Year(s)'))
        self.every_units.bind(size=self.scale_text_btn)
        self.every.add_widget(self.every_units)
        self.repeat_area.add_widget(self.every)

        self.For = GridLayout(cols=1, rows=2)
        self.For_scroll = ScrollView(do_scroll_y=False)
        self.For_grid = GridLayout(rows=1, size_hint=(None, 1))
        self.For_grid.bind(minimum_width=self.For_grid.setter('width'))
        for i in range(1, 13):
            b = Button(text=str(i), size_hint_x=None, width=40)
            b.bind(size=self.scale_text_btn, on_press=self.set_btn)
            self.For_grid.add_widget(b)
        self.For_scroll.add_widget(self.For_grid)
        self.For.add_widget(self.For_scroll)
        self.For_amt = 0
        self.For_grid_chosen = None

        self.For_units = Spinner(text='Unit', values=('Minute(s)', 'Hour(s)', 'Day(s)', 'Week(s)', 'Month(s)', 'Year(s)'))
        self.For_units.bind(size=self.scale_text_btn)
        self.For.add_widget(self.For_units)
        self.repeat_area.add_widget(self.For)

        self.form.add_widget(self.row5)

        # row 6 (Group & Project)
        self.row6 = GridLayout(cols=2, rows=2, size_hint_y=.75)

        self.row6.add_widget(Label(text='Group', size_hint_y=1/2))
        self.row6.add_widget(Label(text='Project', size_hint_y=1/2))

        self.group_btn = Button(text='')
        self.group_btn.bind(text=self.scale_text)
        self.group_list = DropDown(max_height=288)
        groups = ['ITCS-4152', 'MATH-3181', 'TaskIT', 'Ben, Josie,\nRoger, Ashley']
        for i in groups:
            b = Button(text=i, size_hint_y=None, height=48)
            b.bind(on_release=lambda b: self.group_list.select(b.text))
            self.group_list.add_widget(b)
            self.cur.execute("SELECT * FROM _groups")
            # print(self.cur.fetchall())
            if len(self.cur.fetchall()) == 0:
                self.cur.execute('INSERT INTO _groups VALUES(?, ?, ?, ?)', (None, i, "Group", "Personal"))
                self.conn.commit()

        self.group_btn.bind(on_release=self.group_list.open)
        self.group_list.bind(on_select=lambda inetance, x: setattr(self.group_btn, 'text', x))
        self.row6.add_widget(self.group_btn)

        self.project_btn = Button(text='')
        self.project_btn.bind(text=self.scale_text)
        self.project_list = DropDown(max_height=288)
        projects = ['4152 P1', '3181 Final', 'TaskIT', 'Practice']
        for i in projects:
            b = Button(text=i, size_hint_y=None, height=48)
            b.bind(on_release=lambda b: self.project_list.select(b.text))
            self.project_list.add_widget(b)
            self.cur.execute("SELECT * FROM projects")
            # print(self.cur.fetchall())
            if len(self.cur.fetchall()) == 0:
                self.cur.execute('INSERT INTO projects VALUES(?, ?, ?, ?)', (None, i, "Project", "Personal"))
                self.conn.commit()

        self.project_btn.bind(on_release=self.project_list.open)
        self.project_list.bind(on_select=lambda instance, x: setattr(self.project_btn, 'text', x))
        self.row6.add_widget(self.project_btn)
        
        self.form.add_widget(self.row6)

        # row 7 (Save, Clear)
        self.row7 = GridLayout(cols=2, rows=1, size_hint_y=1/2, spacing=20, padding=(10, 5))

        self.save = Button(text='Save')
        self.save.bind(on_press=self.save_task)
        self.row7.add_widget(self.save)
        self.clear = Button(text='Clear')
        self.clear.bind(on_press=self.clear_task)
        self.row7.add_widget(self.clear)
        self.form.add_widget(self.row7)

        self.compat = True

    def get_sects(self, sects=None, *args):
        if sects is not None:
            self.sections = sects

    def date_scroller(self, *args):
        date_scroll = GridLayout(cols=3, rows=1, size_hint_x=3)

        # month
        self.month_scroll = ScrollView(do_scroll_x=False)
        self.month_grid = GridLayout(cols=1, size_hint=(1, None))
        self.month_grid.bind(minimum_height=self.month_grid.setter('height'))
        self.month_scroll.add_widget(self.month_grid)
        for i in range(1, 13):
            month = Button(text=('0' if i < 10 else '') + str(i), size_hint_y=None, height=40)
            month.bind(size=self.scale_text_btn, on_press=self.set_btn)
            self.month_grid.add_widget(month)
        date_scroll.add_widget(self.month_scroll)
        self.month_in = ''
        self.month_chosen = None

        # day
        self.day_scroll = ScrollView(do_scroll_x=False)
        self.day_grid = GridLayout(cols=1, size_hint=(1, None))
        self.day_grid.bind(minimum_height=self.day_grid.setter('height'))
        self.day_scroll.add_widget(self.day_grid)
        for i in range(1, 31):
            day = Button(text=('0' if i < 10 else '') + str(i), size_hint_y=None, height=40)
            day.bind(size=self.scale_text_btn, on_press=self.set_btn)
            self.day_grid.add_widget(day)
        date_scroll.add_widget(self.day_scroll)
        self.day_in = ''
        self.day_chosen = None

        # year
        self.year_scroll = ScrollView(do_scroll_x=False)
        self.year_grid = GridLayout(cols=1, size_hint=(1, None))
        self.year_grid.bind(minimum_height=self.year_grid.setter('height'))
        self.year_scroll.add_widget(self.year_grid)
        for i in range(1, 5):
            year = Button(text=str(2018 + i), size_hint_y=None, height=40)
            if i == 1:
                year.background_color = (0, 1, 0, 1)
                self.year_chosen = year
            year.bind(size=self.scale_text_btn, on_press=self.set_btn)
            self.year_grid.add_widget(year)
        date_scroll.add_widget(self.year_scroll)
        self.year_in = str(date.today().year)

        return date_scroll

    def time_scroller(self, area, *args):
        area.hour_scroll = ScrollView(do_scroll_x=False)
        area.hour_grid = GridLayout(cols=1, size_hint=(1, None))
        area.hour_grid.bind(minimum_height=area.hour_grid.setter('height'))
        area.hour_scroll.add_widget(area.hour_grid)
        for i in range(1, 13):
            if i < 10:
                s = '0' + str(i)
            else:
                s = str(i)
            hour = Button(text=s, size_hint_y=None, height=40)
            hour.bind(size=self.scale_text_btn, on_press=self.set_btn)
            area.hour_grid.add_widget(hour)
        area.hour_in = ''
        area.hour_chosen = None

        area.minute_scroll = ScrollView(do_scroll_x=False)
        area.minute_grid = GridLayout(cols=1, size_hint=(1, None))
        area.minute_grid.bind(minimum_height=area.minute_grid.setter('height'))
        area.minute_scroll.add_widget(area.minute_grid)
        for i in range(1, 61):
            if i < 10:
                s = '0' + str(i)
            else:
                s = str(i)
            minute = Button(text=s, size_hint_y=None, height=40)
            minute.bind(size=self.scale_text_btn, on_press=self.set_btn)
            area.minute_grid.add_widget(minute)
        area.minute_in = ''
        area.minute_chosen = None

        area.add_widget(area.hour_scroll)
        area.add_widget(area.minute_scroll)

        area.ampm = GridLayout(rows=2, cols=1, size_hint_x=1/2)
        area.am = Button(text='AM')
        area.am.active = False
        area.am.bind(on_press=self.set_btn)
        area.pm = Button(text='PM')
        area.pm.active = False
        area.pm.bind(on_press=self.set_btn)
        area.ampm.add_widget(area.am)
        area.ampm.add_widget(area.pm)
        area.add_widget(area.ampm)
        area.ampm_in = ''
        area.ampm_chosen = None

        self.st = None
        self.et = None

        return area

    def add_tab_touch(self, touch, *args):
        if self.collide_point(*touch.pos):
            # set all dates and times to current
            pass

    def apply_type(self, *args):
        if self.type.text == 'Custom':
            self.custom_type_input = TextInput(hint_text='Custom Type', on_text_validate=self.confirm_type,
                                               write_tab=False, multiline=False, size_hint_x=4)
            self.custom_type_input.bind(size=self.scale_text)
            self.custom_type.add_widget(self.custom_type_input)
            self.custom_type_add = Button(text='+')
            self.custom_type_add.bind(size=self.scale_text, on_press=self.confirm_type)
            self.custom_type.add_widget(self.custom_type_add)
        # add "Add to List" button (maybe make it just "+")
        # - Commit to db, edit list, set text to new value

    def confirm_type(self, *args):
        # if text is not in list, add
        # else, select entry
        pass

    def save_task(self, *args):
        if self.check_compat():
            if self.name_in != '':

                print('before', self.st, self.et)
                if self.st[-2:] == self.et[-2:]:
                    if int(self.st[:2]) > int(self.et[:2]):
                        temp = self.st
                        self.st = self.et
                        self.et = temp
                    elif self.st[:2] == self.et[:2]:
                        if int(self.st[3:5]) > int(self.et[3:5]):
                            temp = self.st
                            self.st = self.et
                            self.et = temp
                elif self.st[-2:] == 'pm' and self.et[-2:] == 'am':
                    print("switch")
                    temp = str(self.st)
                    self.st = str(self.et)
                    self.et = temp
                print('after', self.st, self.et)

                self.set_vbls()
                insert_vbls = 'INSERT INTO tasks VALUES(?, '
                insert_vals = [None,]
                i = 0
                for vbl in self.vbls:
                    # print(i, vbl)
                    i += 1
                    insert_vbls += '?, '
                    if type(vbl) is bool:
                        if vbl:
                            insert_vals.append(1)
                        else:
                            insert_vals.append(0)
                    else:
                        if len(str(vbl)) > 0 or type(vbl) is int:
                            insert_vals.append(vbl)
                        else:
                            insert_vals.append(None)
                insert_vbls = insert_vbls[0:len(insert_vbls) - 2]
                insert_vbls += ')'
                # print(insert_vbls, tuple(insert_vals)) # debug

                vbl_names = ['name', 'note', 'date', 'type', 'deadline', 'reminder', 'exclusive', 'start_time',
                             'end_time', 'every_amt', 'every_unit', 'for_amt', 'for_unit', '_group', 'project',
                             'cal_compat']

                info = dict(zip(vbl_names, insert_vals[1:]))
                new_task = Task(info=info, tm=self)

                if new_task.info['start_time'] is None:
                    # print('start time is None')
                    new_task.info['cal_compat'] = 0
                    insert_vals[-1] = 0
                    self.task_to_vault(task=new_task)
                elif self.check_cal_compat(task=new_task):
                    # print('checking cal compat')
                    new_task.info['cal_compat'] = 1
                    insert_vals[-1] = 1
                    self.task_to_cal(task=new_task)
                else:
                    # print('neither worked or task was incompat')
                    new_task.info['cal_compat'] = 0
                    insert_vals[-1] = 0
                    # may change around a little
                    self.task_to_vault(task=new_task)

                print(info)
                self.cur.execute(insert_vbls, tuple(insert_vals))
                self.conn.commit()

    def clear_task(self, *args):
        pass

    def check_cal_compat(self, task=None, *args):
        if task is not None:
            self.cur.execute('SELECT date, start_time, end_time from tasks where date = ?', (task.info['date'],))
            same_day_tasks = self.cur.fetchall()
            this_start = int(task.info['start_time'][:2] + task.info['start_time'][3:5])
            this_end = int(task.info['end_time'][:2] + task.info['end_time'][3:5])
            for t in same_day_tasks:
                other_start = int(t[1][:2] + t[1][3:5])
                other_end = int(t[2][:2] + t[2][3:5])
                # print('+++++++++++', this_start, this_end, other_start, other_end)
                if this_start <= other_end and this_start >= other_start\
                        or this_end <= other_end and this_end >= other_start:
                    # print('not compat!')
                    return False
            return True

    def check_compat(self, instance=None, *args):
        # add negative durations check
        flag = True

        # name
        if self.name_in.text == '':
            self.show_errors(instance=self.name_in)
            self.name_in.bind(text=self.check_name)
            self.in_error = True
            self.compat = False
            flag = False

        # date
        if self.month_in != '':
            if self.day_in != '':
                # print(self.year_in)
                if int(self.year_in) == int(date.today().year):
                    if int(self.month_in) == int(date.today().month):
                        if int(self.day_in) >= int(date.today().day):
                            self.date = self.month_in + '-' + self.day_in + '-' + self.year_in
                            # print("Date is today or later.")
                            if instance is not None:
                                for cousin in self.day_grid.children:
                                    cousin.background_color = (1, 1, 1, 1)
                                self.day_chosen.background_color = (0, 1, 0, 1)
                                for child in self.month_grid.children:
                                    child.background_color = (1, 1, 1, 1)
                                self.month_chosen.background_color = (0, 1, 0, 1)
                                return True
                        else:
                            for cousin in self.day_grid.children:
                                cousin.background_color = (1, 0, 0, 1)
                            self.day_chosen.background_color = (0, 1, 0, 1)
                            for child in self.month_grid.children:
                                child.background_color = (1, 0, 0, 1)
                            self.month_chosen.background_color = (0, 1, 0, 1)
                                # return True
                            self.in_error = True
                            self.compat = False
                            flag = False
                    elif int(self.month_in) > int(date.today().month):
                        self.date = self.month_in + '-' + self.day_in + '-' + self.year_in
                        # print("Date is today or later.")
                        if instance is not None:
                            for cousin in self.day_grid.children:
                                cousin.background_color = (1, 1, 1, 1)
                            self.day_chosen.background_color = (0, 1, 0, 1)
                            return True
                    else:
                        for child in self.month_grid.children:
                            child.background_color = (1, 0, 0, 1)
                        self.month_chosen.background_color = (0, 1, 0, 1)
                        for cousin in self.day_grid.children:
                            cousin.background_color = (1, 0, 0, 1)
                        self.day_chosen.background_color = (0, 1, 0, 1)
                        self.in_error = True
                        self.compat = False
                        flag = False
                else:
                    self.date = self.month_in + '-' + self.day_in + '-' + self.year_in
                    if instance is not None:
                        for cousin in self.day_grid.children:
                            cousin.background_color = (1, 1, 1, 1)
                        self.day_chosen.background_color = (0, 1, 0, 1)
                        return True
            else:
                self.show_errors(instance=self.day_grid)
                if int(self.month_in) < int(date.today().month):
                    self.show_errors(instance=self.month_grid)
                    self.month_chosen.background_color = (0, 1, 0, 1)
                else:
                    for child in self.month_grid.children:
                        child.background_color = (1, 1, 1, 1)
                    self.month_chosen.background_color = (0, 1, 0, 1)
                    if instance is not None:
                        return True
                self.in_error = True
                self.compat = False
                flag = False
        else:
            if self.day_in != '':
                self.show_errors(instance=self.month_grid)
                self.in_error = True
                self.compat = False
                flag = False
            else:
                self.date = None

        # type
        if self.type.text == 'Custom':
            if self.custom_type_input.text == '':
                self.show_errors(instance=self.custom_type_input)
                self.custom_type_input.bind(text=self.check_type)
                self.in_error = True
                self.compat = False

        # start time
        if self.start_time.hour_in == '':
            if self.start_time.minute_in == '':
                if self.end_time.hour_in != '' or self.end_time.minute_in != '' or self.end_time.ampm_chosen is not None:
                    self.show_errors(instance=self.start_time.hour_grid)
                    self.show_errors(instance=self.start_time.minute_grid)
                    if self.start_time.ampm_chosen is None:
                        self.show_errors(instance=self.start_time.ampm)
                        self.in_error = True
                        self.compat = False
                        flag = False
                    else:
                        if instance is not None and instance.parent is self.start_time.ampm:
                            return True
                else:
                    if self.start_time.ampm_chosen is not None:
                        if instance is not None and instance.parent is self.start_time.ampm:
                            return True
                        self.show_errors(instance=self.start_time.hour_grid)
                        self.show_errors(instance=self.start_time.minute_grid)
                        self.in_error = True
                        self.compat = False
                        flag = False
                    else:
                        self.st = None
            else:
                self.show_errors(instance=self.start_time.hour_grid)
                if instance is not None and instance.parent is self.start_time.minute_grid:
                    return True
                if not self.start_time.am.active and not self.start_time.pm.active:
                    self.show_errors(instance=self.start_time.am)
                    self.show_errors(instance=self.start_time.pm)
                else:
                    if instance is not None and instance.parent is self.start_time.ampm:
                        return True
                self.in_error = True
                self.compat = False
                flag = False
        else:
            if instance is not None and instance.parent is self.start_time.hour_grid:
                return True
            if self.start_time.minute_in != '':
                if instance is not None and instance.parent is self.start_time.minute_grid:
                    return True
                if self.start_time.am.active:
                    self.st = self.start_time.hour_in + ':' + self.start_time.minute_in + ' am'
                    if instance is not None and instance.parent is self.start_time.ampm:
                        return True
                elif self.start_time.pm.active:
                    self.st = self.start_time.hour_in + ':' + self.start_time.minute_in + ' pm'
                    if instance is not None and instance.parent is self.start_time.ampm:
                        return True
                else:
                    self.show_errors(instance=self.start_time.am)
                    self.show_errors(instance=self.start_time.pm)
                    self.in_error = True
                    compat = False
                    flag = False
            else:
                if not self.start_time.am.active and not self.start_time.pm.active:
                    self.show_errors(instance=self.start_time.am)
                    self.show_errors(instance=self.start_time.pm)
                else:
                    if instance is not None and instance.parent is self.start_time.ampm:
                        return True
                self.show_errors(instance=self.start_time.minute_grid)
                self.in_error = True
                self.compat = False
                flag = False

        # end time
        if self.end_time.hour_in == '':
            if self.end_time.minute_in == '':
                if self.start_time.hour_in != '' or self.start_time.minute_in != '' or self.start_time.ampm_chosen is not None:
                    self.show_errors(instance=self.end_time.hour_grid)
                    self.show_errors(instance=self.end_time.minute_grid)
                    if self.end_time.ampm_chosen is None:
                        self.show_errors(instance=self.end_time.ampm)
                        self.in_error = True
                        self.compat = False
                        flag = False
                    else:
                        if instance is not None and instance.parent is self.end_time.ampm:
                            return True
                else:
                    if self.end_time.ampm_chosen is not None:
                        if instance is not None and instance.parent is self.end_time.ampm:
                            return True
                        self.show_errors(instance=self.end_time.hour_grid)
                        self.show_errors(instance=self.end_time.minute_grid)
                        self.in_error = True
                        self.compat = False
                        flag = False
                    else:
                        self.et = None
            else:
                self.show_errors(instance=self.end_time.hour_grid)
                if instance is not None and instance.parent is self.end_time.minute_grid:
                    return True
                if not self.end_time.am.active and not self.end_time.pm.active:
                    self.show_errors(instance=self.end_time.am)
                    self.show_errors(instance=self.end_time.pm)
                else:
                    if instance is not None and instance.parent is self.end_time.ampm:
                        return True
                self.in_error = True
                self.compat = False
                flag = False
        else:
            if instance is not None and instance.parent is self.end_time.hour_grid:
                return True
            if self.end_time.minute_in != '':
                if instance is not None and instance.parent is self.end_time.minute_grid:
                    return True
                if self.end_time.am.active:
                    self.et = self.end_time.hour_in + ':' + self.end_time.minute_in + ' am'
                    if instance is not None and instance.parent is self.end_time.ampm:
                        return True
                elif self.end_time.pm.active:
                    self.et = self.end_time.hour_in + ':' + self.end_time.minute_in + ' pm'
                    if instance is not None and instance.parent is self.end_time.ampm:
                        return True
                else:
                    self.show_errors(instance=self.end_time.am)
                    self.show_errors(instance=self.end_time.pm)
                    self.in_error = True
                    compat = False
                    flag = False
            else:
                if not self.end_time.am.active and not self.end_time.pm.active:
                    self.show_errors(instance=self.end_time.am)
                    self.show_errors(instance=self.end_time.pm)
                else:
                    if instance is not None and instance.parent is self.end_time.ampm:
                        return True
                self.show_errors(instance=self.end_time.minute_grid)
                self.in_error = True
                self.compat = False
                flag = False

        # repeat every
        if self.every_grid_chosen is not None:
            if self.every_units.text == 'Unit':
                self.show_errors(instance=self.every_units)
                self.every_units.bind(text=self.check_every)
            elif instance is self.every_units:
                self.every_units.background_color = (1, 1, 1, 1)
                return True
            if self.For_grid_chosen is None:
                self.show_errors(instance=self.For_grid)
            elif instance is not None and instance.parent is self.every_grid:
                for sib in instance.parent.children:
                    sib.background_color = (1, 1, 1, 1)
                instance.background_color = (0, 1, 0, 1)
                return True
            if self.For_units.text == 'Unit':
                self.show_errors(instance=self.For_units)
                self.For_units.bind(text=self.check_For)
            elif instance is self.For_units:
                self.For_units.background_color = (1, 1, 1, 1)
                return True
            self.in_error = True
            self.compat = False
            flag = False

        # repeat for
        if self.For_grid_chosen is not None:
            if self.For_units.text == 'Unit':
                self.show_errors(instance=self.For_units)
                self.For_units.bind(text=self.check_For)
            elif instance is not None and instance.parent is self.For_units:
                self.For_units.background_color = (1, 1, 1, 1)
                return True
            if self.every_grid_chosen is None:
                self.show_errors(instance=self.every_grid)
            elif instance is not None and instance.parent is self.For_grid:
                for sib in instance.parent.children:
                    sib.background_color = (1, 1, 1, 1)
                instance.background_color = (0, 1, 0, 1)
                return True
            if self.every_units.text == 'Unit':
                self.show_errors(instance=self.every_units)
                self.every_units.bind(text=self.check_every)
            elif instance is not None and instance.parent is self.every_units:
                self.every_units.background_color = (1, 1, 1, 1)
                return True
            self.in_error = True
            self.compat = False
            flag = False
            
        
        if flag:
            self.in_error = False
            self.compat = True

        return flag

    def show_errors(self, instance=None, *args):
        for c in instance.children:
            c.background_color = (1, 0, 0, 1)
        instance.background_color = (1, 0, 0, 1)

    def check_type(self, *args):
        if self.custom_type_input.text != '':
            self.custom_type_input.background_color = (1, 1, 1, 1)
        self.custom_type_input.unbind(text=self.check_type)

    def check_name(self, *args):
        if self.name_in.text != '':
            self.name_in.background_color = (1, 1, 1, 1)
        self.name_in.unbind(text=self.check_name)
        
    def check_every(self, *args):
        if self.every_units.text != 'Units':
            self.every_units.background_color = (1, 1, 1, 1)
        self.every_units.unbind(text=self.check_every)

    def check_For(self, *args):
        if self.For_units.text != 'Units':
            self.For_units.background_color = (1, 1, 1, 1)
        self.For_units.unbind(text=self.check_For)

    def scale_text(self, instance, *args):
        if instance == self.note:
            instance.font_size = instance.height * .265
            return
        elif instance == self.custom_type_input:
            instance.font_size = instance.height * .575
            return
        elif instance == self.name_in:
            instance.font_size = instance.height * .75
            return
        instance.font_size = instance.height * .6

    def scale_text_btn(self, instance, *args):
        instance.font_size = instance.height * .6

    def set_vbls(self, *args):

        self.vbls = [self.name_in.text, self.note.text, self.date, self.type.text, self.deadline.active,
                     self.reminder.active, self.exclusive.active, self.st, self.et, self.every_amt, self.every_units.text,
                     self.For_amt, self.For_units.text, self.group_btn.text, self.project_btn.text, self.compat]

    def set_btn(self, instance, *args):

        if instance.parent is self.month_grid:
            if self.month_chosen is not None:
                self.month_chosen.background_color = (1, 1, 1, 1)
            # deselect
            if instance is self.month_chosen:
                if self.in_error is True:
                    instance.background_color = (1, 0, 0, 1)
                self.month_in = ''
                self.month_chosen = None
                return
            # select new
            else:
                self.month_in = instance.text
                self.month_chosen = instance
                if self.in_error is True:
                    if self.check_compat(instance=self.month_chosen):
                        for sib in instance.parent.children:
                            sib.background_color = (1, 1, 1, 1)
                    else:
                        self.show_errors(instance=self.month_grid)
                        # print('I changed to red.')
                instance.background_color = (0, 1, 0, 1)
                # print('You pressed month: ' + instance.text)
                return

        if instance.parent is self.day_grid:
            if self.day_chosen is not None:
                self.day_chosen.background_color = (1, 1, 1, 1)
            # deselect
            if instance is self.day_chosen:
                if self.in_error is True:
                    instance.background_color = (1, 0, 0, 1)
                self.day_in = ''
                self.day_chosen = None
                return
            # select new
            else:
                self.day_in = instance.text
                self.day_chosen = instance
                if self.in_error:
                    if self.check_compat(instance=self.day_chosen):
                        for sib in instance.parent.children:
                            sib.background_color = (1, 1, 1, 1)
                    else:
                        self.show_errors(instance=self.day_grid)
                instance.background_color = (0, 1, 0, 1)
                # print('You pressed day: ' + instance.text)
                return

        if instance.parent is self.year_grid:
            if self.year_chosen is not None:
                self.year_chosen.background_color = (1, 1, 1, 1)
            if instance is self.year_chosen:
                if self.in_error:
                    instance.background_color = (1, 0, 0, 1)
                    for sib in self.year_grid:
                        sib.background_color = (1, 0, 0, 1)
                else:
                    instance.background_color = (1, 1, 1, 1)
                    self.year_in = str(date.today().year)
                    self.year_grid.children[-1].background_color = (0, 1, 0, 1)
                self.year_chosen = None
            else:
                self.year_in = instance.text
                self.year_chosen = instance
                if self.in_error:
                    if int(self.year_in) > int(date.today().year):
                        for cousin in self.month_grid.children:
                            cousin.background_color = (1, 1, 1, 1)
                        self.month_chosen.background_color = (0, 1, 0, 1)
                        for cousin in self.day_grid.children:
                            cousin.background_color = (1, 1, 1, 1)
                        self.day_chosen.background_color = (0, 1, 0, 1)
                    else:
                        self.check_compat()
                instance.background_color = (0, 1, 0, 1)
                # print('You pressed year: ' + instance.text)

        if instance.parent is self.start_time.hour_grid:
            if self.start_time.hour_chosen is not None:
                if self.in_error:
                    for sib in instance.parent.children:
                        sib.background_color = (1, 0, 0, 1)
                    self.start_time.hour_chosen.background_color = (1, 0, 0, 1)
                else:
                    self.start_time.hour_chosen.background_color = (1, 1, 1, 1)
            if instance is self.start_time.hour_chosen:
                # instance.background_color = (1, 1, 1, 1)
                self.start_time.hour_in = ''
                self.start_time.hour_chosen = None
            else:
                self.start_time.hour_in = instance.text
                self.start_time.hour_chosen = instance
                if self.in_error:
                    if self.check_compat(instance=self.start_time.hour_chosen):
                        for sib in instance.parent.children:
                            sib.background_color = (1, 1, 1, 1)
                    else:
                        self.show_errors(instance=self.start_time.hour_grid)
                instance.background_color = (0, 1, 0, 1)
                # print('You pressed hour: ' + instance.text)

        if instance.parent is self.start_time.minute_grid:
            if self.start_time.minute_chosen is not None:
                if self.in_error:
                    for sib in instance.parent.children:
                        sib.background_color = (1, 0, 0, 1)
                else:
                    self.start_time.minute_chosen.background_color = (1, 1, 1, 1)
            if instance is self.start_time.minute_chosen:
                if self.in_error:
                    self.start_time.minute_chosen.background_color = (1, 0, 0, 1)
                else:
                    instance.background_color = (1, 1, 1, 1)
                self.start_time.minute_in = ''
                self.start_time.minute_chosen = None
            else:
                self.start_time.minute_in = instance.text
                self.start_time.minute_chosen = instance
                if self.in_error:
                    if self.check_compat(instance=self.start_time.minute_chosen):
                        for sib in instance.parent.children:
                            sib.background_color = (1, 1, 1, 1)
                    else:
                        self.show_errors(instance=self.start_time.minute_grid)
                instance.background_color = (0, 1, 0, 1)
                # print('You pressed minute: ' + instance.text)

        if instance.parent is self.start_time.ampm:
            if self.start_time.ampm_chosen is not None:
                if self.in_error:
                    self.start_time.ampm_chosen.background_color = (1, 0, 0, 1)
                else:
                    self.start_time.ampm_chosen.background_color = (1, 1, 1, 1)
            if instance is self.start_time.ampm_chosen:
                if self.in_error:
                    instance.background_color = (1, 0, 0, 1)
                else:
                    instance.background_color = (1, 1, 1, 1)
                self.start_time.ampm_in = ''
                self.start_time.ampm_chosen = None
            else:
                self.start_time.ampm_in = instance.text
                self.start_time.ampm_chosen = instance
                # print("ch-ch-ch" + instance.text)
                if instance.text == 'AM':
                    self.start_time.am.active = True
                    self.start_time.pm.active = False
                else:
                    self.start_time.pm.active = True
                    self.start_time.am.active = False
                if self.in_error:
                    if self.check_compat(instance=self.start_time.ampm_chosen):
                        for sib in instance.parent.children:
                            sib.background_color = (1, 1, 1, 1)
                    else:
                        self.show_errors(instance=self.start_time.ampm)
                instance.background_color = (0, 1, 0, 1)
                # print('You pressed: ' + instance.text)

        if instance.parent is self.end_time.hour_grid:
            if self.end_time.hour_chosen is not None:
                if self.in_error:
                    for sib in instance.parent.children:
                        sib.background_color = (1, 0, 0, 1)
                    self.end_time.hour_chosen.background_color = (1, 0, 0, 1)
                else:
                    self.end_time.hour_chosen.background_color = (1, 1, 1, 1)
            if instance is self.end_time.hour_chosen:
                self.end_time.hour_in = ''
                self.end_time.hour_chosen = None
            else:
                self.end_time.hour_in = instance.text
                self.end_time.hour_chosen = instance
                if self.in_error:
                    if self.check_compat(instance=self.end_time.hour_chosen):
                        for sib in instance.parent.children:
                            sib.background_color = (1, 1, 1, 1)
                    else:
                        self.show_errors(instance=self.end_time.hour_grid)
                instance.background_color = (0, 1, 0, 1)
                # print('You pressed day: ' + instance.text)

        if instance.parent is self.end_time.minute_grid:
            if self.end_time.minute_chosen is not None:
                if self.in_error:
                    for sib in instance.parent.children:
                        sib.background_color = (1, 0, 0, 1)
                    self.end_time.minute_chosen.background_color = (1, 0, 0, 1)
                else:
                    self.end_time.minute_chosen.background_color = (1, 1, 1, 1)
            if instance is self.end_time.minute_chosen:
                self.end_time.minute_in = ''
                self.end_time.minute_chosen = None
            else:
                self.end_time.minute_in = instance.text
                self.end_time.minute_chosen = instance
                if self.in_error:
                    if self.check_compat(instance=self.end_time.minute_chosen):
                        for sib in instance.parent.children:
                            sib.background_color = (1, 1, 1, 1)
                    else:
                        self.show_errors(instance=self.end_time.minute_grid)
                instance.background_color = (0, 1, 0, 1)
                # print('You pressed day: ' + instance.text)

        if instance.parent is self.end_time.ampm:
            if self.end_time.ampm_chosen is not None:
                if self.in_error:
                    self.end_time.ampm_chosen.background_color = (1, 0, 0, 1)
                else:
                    self.end_time.ampm_chosen.background_color = (1, 1, 1, 1)
            if instance is self.end_time.ampm_chosen:
                if self.in_error:
                    instance.background_color = (1, 0, 0, 1)
                else:
                    instance.background_color = (1, 1, 1, 1)
                self.end_time.ampm_in = ''
                self.end_time.ampm_chosen = None
            else:
                self.end_time.ampm_in = instance.text
                self.end_time.ampm_chosen = instance
                # print("ch-ch-ch" + instance.text)
                if instance.text == 'AM':
                    self.end_time.am.active = True
                    self.end_time.pm.active = False
                else:
                    self.end_time.pm.active = True
                    self.end_time.am.active = False
                if self.in_error:
                    if self.check_compat(instance=self.end_time.ampm_chosen):
                        for sib in instance.parent.children:
                            sib.background_color = (1, 1, 1, 1)
                    else:
                        self.show_errors(instance=self.end_time.ampm)
                instance.background_color = (0, 1, 0, 1)
                # print('You pressed: ' + instance.text)

        if instance.parent is self.every_grid:
            if self.every_grid_chosen is not None:
                self.every_grid_chosen.background_color = (1, 1, 1, 1)
            if instance is self.every_grid_chosen:
                self.every_grid_in = ''
                self.every_grid_chosen = None
                if self.in_error:
                    if not self.check_compat(instance=self.every_grid_chosen):
                        self.show_errors(instance=instance.parent)
                else:
                    instance.background_color = (1, 1, 1, 1)
            else:
                self.every_grid_chosen = instance
                self.every_grid_in = instance.text
                if self.in_error:
                    self.check_compat(instance=self.every_grid_chosen)
                    self.check_compat(instance=self.every_units)
                    self.check_compat(instance=self.For_units)
                instance.background_color = (0, 1, 0, 1)
                # print('You pressed day: ' + instance.text)

        if instance.parent is self.For_grid:
            if self.For_grid_chosen is not None:
                self.For_grid_chosen.background_color = (1, 1, 1, 1)
            if instance is self.For_grid_chosen:
                self.For_grid_in = ''
                self.For_grid_chosen = None
                if self.in_error:
                    if not self.check_compat(instance=self.For_grid_chosen):
                        self.show_errors(instance=instance.parent)
                else:
                    instance.background_color = (1, 1, 1, 1)
            else:
                self.For_grid_chosen = instance
                self.For_grid_in = instance.text
                if self.in_error:
                    for sib in instance.parent.children:
                        sib.background_color = (1, 1, 1, 1)
                        instance.background_color = (0, 1, 0, 1)
                    self.check_compat(instance=self.every_units)
                    self.check_compat(instance=self.For_units)
                instance.background_color = (0, 1, 0, 1)
                # print('You pressed day: ' + instance.text)

    def month_to_str(self, *args):
        pass
        self.date = "something"

    def task_to_vault(self, task=None, *args):

        pass

    def task_to_cal(self, task=None, *args):
        print('-_-_-_-', self.st, self.et)
        if task is not None:
            for day in self.sections['calendar'].current_week.days:
                d = day.scroll_grid
                if task.info['date'] == day.date:
                    children = list(reversed(d.children))
                    d.clear_widgets()
                    i = 0
                    top = task.loc + task.length
                    bottom = task.loc
                    for c in children:
                        # print('top: ' + str(top) + ', bottom: ' + str(bottom) + ', c.top: ' + str(c.pos[1] + c.height) + ', c.bottom: ' + str(c.pos[1]))
                        if top <= c.pos[1] + c.height and bottom >= c.pos[1]:
                            l = Label(size_hint_y=None)
                            if i == 0:
                                l.height = d.height - top
                                # print('top', l.height)
                            else:
                                # print(children[i - 1].text, (children[i - 1].pos[1] if children[i - 1].pos[1] != 0 else children[i - 1].loc, top))
                                l.height = (children[i - 1].pos[1] if children[i - 1].pos[1] != 0 else children[i - 1].loc) - top
                                # print('middle-first', l.height)
                            d.add_widget(l)
                            # print(l.height, l.pos[1])

                            d.add_widget(task)
                            # print(task.height, task.pos[1])

                            l = Label(size_hint_y=None)
                            if i == len(children) - 1:
                                l.height = bottom
                                # print("bottom", bottom)
                            else:
                                l.height = task.loc - (children[i + 1].pos[1] + children[i + 1].height)
                                # print("middle", l.height)
                            d.add_widget(l)
                            # print(l.height, l.pos[1])
                        else:
                            d.add_widget(c)
                        i += 1

class Task(Button):
    def __init__(self, info=None, tm=None, **kwargs):
        super(Task, self).__init__(**kwargs)

        self.size_hint_y = None

        if info is not None:
            self.info = info

        self.text = self.info['name'] + '\n' + self.info['start_time']+ '\n' + self.info['end_time']

        if self.info['cal_compat']:
            pass
        if self.info['end_time'] is not None:
            end_h = int(self.info['end_time'][:2])
            end_m = int(self.info['end_time'][3:5])
            start_h = int(self.info['start_time'][:2])
            start_m = int(self.info['start_time'][3:5])
            if tm is not None:
                day_height = tm.sections['calendar'].current_week.days[1].scroll_grid.height
            else:
                day_height = 2880 # here

            if self.info['end_time'][-2:] == self.info['start_time'][-2:]:
                # print('end_h', end_h)
                self.length = ((end_h * (0 if end_h == 12 else 1) * 120 + end_m * 2 - start_h * (0 if start_h == 12 else 1) * 120 - start_m * 2) / float(day_height)) * day_height # here
                self.loc = ((day_height if self.info['end_time'][-2:] == 'am' else day_height/2.) - end_h * (0 if end_h == 12 else 1) * 120 - end_m * 2) # here
            else:
                self.length = ((end_h * (0 if end_h == 12 else 1) * 120 + end_m * 2 - start_h * 120 - start_m * 2 + day_height / 2) / float(day_height)) * day_height # here
                self.loc = (day_height / 2 - end_h * (0 if end_h == 12 else 1) * 120 - end_m * 2) # here
            self.height = self.length

            self.start_label = Label(text=self.info['start_time'])

            print(self.info['date'], '________________________________', self.text, self.height, self.loc)


    def dragndrop(self, *args):
        '''
        When dropping task into place, copy all widgets to a new list, reverse it, and
        find appropriate place for task based on location dropped. Take into account:
        (1) length of task
        (2) dependencies (location, order in sequence, etc.)
        (3) flexibility of surrounding tasks (if space is insufficient)
        (4) etc.?

        Then the layout should take care of the rest.'''
        pass
