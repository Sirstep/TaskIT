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
from kivy.uix.togglebutton import ToggleButton
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
from kivy.factory import Factory
from kivy.uix.recycleview import RecycleView
from kivydnd.dragndropwidget import DragNDropWidget
from kivy.base import Builder

# Other imports
import inspect
from datetime import datetime, date
import time
from random import randint, random
from math import ceil, floor

# Custom Imports
import main
import calendar

Builder.load_string('''
<Scroll_Label>:
    size_hint_y: None
    text_size: self.width, None
    height: self.texture_size[1]
    ''')


class Task_Mgmt(TabbedPanel):
    def __init__(self, conn=None, **kwargs):
        super(Task_Mgmt, self).__init__(**kwargs)
        self.conn = conn
        self.cur = self.conn.cursor()
        self.in_error = False

        self.add_tab = TabbedPanelItem(text='Add/Edit')
        self.add_widget(self.add_tab)
        self.default_tab = self.add_tab

        self.t1_content = GridLayout(rows=2, cols=1)
        self.add_tab.add_widget(self.t1_content)

        self.form = GridLayout(cols=1, rows=7, spacing=3, padding=3)
        self.t1_content.add_widget(self.form)

        # row 1 (Name)
        self.row1 = GridLayout(rows=1, cols=1, size_hint_y=.5)
        self.form.add_widget(self.row1)
        self.name_in = TextInput(multiline=False, hint_text='Name', padding=1, write_tab=False,
                                 on_text_validate=self.save_task, text='')
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
        if len(self.cur.fetchall()) == 0:
            for i in types:
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

        units = ('Minute(s)', 'Hour(s)', 'Day(s)', 'Week(s)', 'Month(s)', 'Year(s)')
        self.every_units = Spinner(text='Unit', values=units)
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

        self.For_units = Spinner(text='Unit', values=units)
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
        if len(self.cur.fetchall()) == 0:
            for i in groups:
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
        if len(self.cur.fetchall()) == 0:
            for i in projects:
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

        # --------------------------------------------------------------------------------------------------------Search

        self.search_tab = TabbedPanelItem(text='Search')
        self.add_widget(self.search_tab)

        self.t2_content = GridLayout(rows=3, cols=1)
        self.search_tab.add_widget(self.t2_content)

        self.search_options = ['Name', 'Type', 'Date', 'Time', 'Group', 'Project', 'Created']
        self.search_options_active = dict(zip(self.search_options, [0 for _ in range(len(self.search_options))]))
        self.t2_header = GridLayout(rows=1, cols=len(self.search_options))
        for option in self.search_options:
            o = Button(text=option)
            search_func = getattr(self, option)
            o.bind(on_press=search_func)

            self.t2_header.add_widget(o)

        self.t2_content.add_widget(self.t2_header)
        self.t2_subheader = GridLayout(rows=1)
        self.t2_content.add_widget(self.t2_subheader)

        self.t2_results_scroll = ScrollView(do_scroll_x=False, size_hint_y=8)
        self.t2_results_grid = GridLayout(cols=1, size_hint=(1, None), spacing=15, padding=(0, 15, 0, 15))
        self.t2_results_grid.bind(minimum_height=self.t2_results_grid.setter('height'))
        self.t2_results_scroll.add_widget(self.t2_results_grid)

        self.t2_content.add_widget(self.t2_results_scroll)

        # ----------------------------------------------------------------------------------------------------------View

        self.view_tab = TabbedPanelItem(text='View')
        self.add_widget(self.view_tab)

        self.t3_content = GridLayout(rows=2, cols=1)
        self.view_tab.add_widget(self.t3_content)

        self.view_scroll = ScrollView(do_scroll_x=False)

        self.view_label = Scroll_Label(halign='left', valign='top', markup=True, font_size=25)
        self.viewed_task = None

        self.view_label.texts = ['[b][color=00FF00]Name:[/color][/b] ',
                                 '[b][color=00FF00]Note:[/color][/b] ',
                                 '[b][color=00FF00]Date:[/color][/b] ',
                                 '[b][color=00FF00]Type:[/color][/b] ',
                                 '[b][color=FF0000]Deadline[/color][/b]',
                                 '[b][color=FF0000]Reminder[/color][/b]',
                                 '[b][color=FF0000]Exclusive[/color][/b]',
                                 '[b][color=00FF00]Start:[/color][/b] ',
                                 '[b][color=00FF00]End:[/color][/b] ',
                                 '', '', '', '',
                                 '[b][color=00FF00]Group:[/color][/b] ',
                                 '[b][color=00FF00]Project:[/color][/b] ',
                                 '[b][color=0000FF]In Calendar[/color][/b]']


        self.view_scroll.add_widget(self.view_label)
        self.t3_content.add_widget(self.view_scroll)

        self.t3_buttons = GridLayout(rows=1, cols=2, size_hint_y=.1)
        self.edit_task_b = Button(text='Edit', background_color=(0, .5, 0, 1))
        self.edit_task_b.bind(on_press=self.edit_task)
        self.delete_task_b = Button(text='Delete', background_color=(.5, 0, 0, 1))
        self.delete_task_b.bind(on_press=self.delete_task)

        self.t3_buttons.add_widget(self.edit_task_b)
        self.t3_buttons.add_widget(self.delete_task_b)
        self.t3_content.add_widget(self.t3_buttons)

        # ---------------------------------------------------------------------------------------------------------Vault

        self.vault_tab = TabbedPanelItem(text='Vault')
        self.add_widget(self.vault_tab)

        self.t4_scroll = ScrollView(do_scroll_x=False)
        self.t4_content = GridLayout(cols=1, size_hint_y=None, spacing=20, padding=(0, 20, 0, 20))
        self.t4_content.bind(minimum_height=self.t4_content.setter('height'))
        self.t4_scroll.add_widget(self.t4_content)
        self.vault_tab.add_widget(self.t4_scroll)

        self.fill_vault()

    def fill_vault(self, *args):
        self.cur.execute('select name, type, date, start_time, end_time, _group, project from tasks where cal_compat = 0')
        for t in self.cur.fetchall():
            l = Scroll_Label(size_hint_y=None, height=50, font_size=20)
            for i in t:
                if i:
                    l.text += str(i) + ', '
            l.text = l.text[:-2]
            self.t4_content.add_widget(l)
        for t in range(100):
            l = Button(text='Placeholder to exhibit scroll...', size_hint_y=None, height=50, font_size=20)
            self.t4_content.add_widget(l)

    def edit_task(self, *args):
        self.switch_to(self.add_tab)

    def delete_task(self, *args):
        if self.viewed_task:
            self.cur.execute('delete from tasks where start_time = ? and end_time = ? and name = ?',
                             (self.viewed_task.info['start_time'],
                              self.viewed_task.info['end_time'],
                              self.viewed_task.info['name']))
            self.conn.commit()
            current_week = [d.dom for d in self.sections['calendar'].current_week.days]

            if self.viewed_task.info['date'] in current_week:
                self.sections['calendar'].current_week.days[current_week.index(self.viewed_task.info['date'])].\
                    scroll_grid.clear_widgets()
                self.sections['calendar'].current_week.days[current_week.index(self.viewed_task.info['date'])]. \
                    scroll_grid.add_widget(Button(size_hint_y=None,
                                                  height=self.sections['calendar'].current_week.
                                                  days[current_week.index(self.viewed_task.info['date'])].\
                                                  scroll_grid.height,
                                                  background_color=(0, 0, 0, 0)))
                self.sections['calendar'].current_week.days[0].add_tasks2(cur=self.cur,
                                                     dom=self.viewed_task.info['date'],
                                                     sects=self.sections,
                                                     overlap=True)
            self.view_label.text = ''

    def view_task(self, instance=None, *args):
        info = list(instance.info.values())
        self.view_label.text = ''
        for i in range(len(self.view_label.texts)):
            if info[i] and info[i] != 'Unit':
                if info[i] == 1:
                    self.view_label.text += self.view_label.texts[i] + '\n\n'
                else:
                    self.view_label.text += self.view_label.texts[i] + info[i] + '\n\n'
        self.view_label.height = self.view_label.texture_size[1]
        self.switch_to(self.view_tab, do_scroll=True)
        self.viewed_task = instance

    def Name(self, *args):
        if self.search_options_active['Name'] == 0:
            s = self.search_options_active
            [s.update({key: 0}) for key in s.keys()]

            self.t2_subheader.clear_widgets()
            self.name_subheader = GridLayout(rows=1, cols=3)
            self.name_search_input = TextInput(multiline=False, size_hint_x=4)
            self.name_search_input.bind(size=self.scale_text)
            self.name_subheader.add_widget(self.name_search_input)

            self.name_search_boxes = GridLayout(rows=2, cols=2, size_hint_x=1.5)
            self.name_search_contain = CheckBox(group='name_search', size_hint_x=.5)
            self.name_search_boxes.add_widget(self.name_search_contain)
            self.name_search_boxes.add_widget(Label(text='Contains'))
            self.name_search_exactly = CheckBox(group='name_search', size_hint_x=.5)
            self.name_search_boxes.add_widget(self.name_search_exactly)
            self.name_search_boxes.add_widget(Label(text='Exactly'))
            self.name_subheader.add_widget(self.name_search_boxes)

            self.name_search_button = Button(text='GO')
            self.name_search_button.bind(size=self.scale_text, on_press=self.name_search)
            self.name_subheader.add_widget(self.name_search_button)
            self.t2_subheader.add_widget(self.name_subheader)
            self.t2_results_grid.clear_widgets()

            self.search_options_active['Name'] = 1
            self.name_search_last = None
        else:
            temp_children = list(self.t2_results_grid.children)
            self.t2_results_grid.clear_widgets()
            for tc in temp_children:
                self.t2_results_grid.add_widget(tc)

    def name_search(self, *args):
        if self.name_search_last == self.name_search_input.text:
            temp_children = list(self.t2_results_grid.children)
            self.t2_results_grid.clear_widgets()
            for tc in temp_children:
                self.t2_results_grid.add_widget(tc)
        elif self.name_search_input.text == '':
            self.cur.execute('SELECT * from tasks')
            self.search_results = self.cur.fetchall()
            self.show_results()
        else:
            self.cur.execute('SELECT * from tasks')
            self.search_results = []
            for t in self.cur.fetchall():
                if self.name_search_input.text in t[1]:
                    self.search_results.append(t)
            self.show_results()
        self.name_search_last = self.name_search_input.text

    def show_results(self, *args):
        self.t2_results_grid.clear_widgets()
        for i in self.search_results:

            res = Button(text=str(i[1:-1]), size_hint_y=None, height=50, font_size=20, halign='left')
            res.bind(size=res.setter('text_size'))
            # res.bind(size=self.scale_text_btn, on_press=self.set_btn)
            self.t2_results_grid.add_widget(res)

    def Type(self, *args):
        if self.search_options_active['Type'] == 0:

            s = self.search_options_active
            [s.update({key: 0}) for key in s.keys()]

            self.t2_subheader.clear_widgets()

            self.type_btn = Button(text='Chosen Types: ')
            self.type_btn.bind(
                width=lambda *x: self.type_btn.setter('text_size')(self.type_btn, (self.type_btn.width, None)),
            )
            self.selected_type_values = []
            self.type_list2 = DropDown(max_height=288)
            types = ['General', 'School', 'Work', 'Home', 'Other']

            for value in types:
                b = ToggleButton(size_hint=(1, None), height='48dp', text=value)
                b.bind(state=self.select_type_value)
                self.type_list2.add_widget(b)

            self.type_btn.bind(on_release=self.type_list2.open)
            self.t2_subheader.add_widget(self.type_btn)

            self.search_options_active['Type'] = 1
        else:
            temp_children = list(self.t2_results_grid.children)
            self.t2_results_grid.clear_widgets()
            for tc in temp_children:
                self.t2_results_grid.add_widget(tc)

    def select_type_value(self, instance=None, value=None, *args):
        if value == 'down':
            if instance.text not in self.selected_type_values:
                self.selected_type_values.append(instance.text)
                self.on_selected_values(instance, instance.text)
        else:
            if instance.text in self.selected_type_values:
                self.selected_type_values.remove(instance.text)
                self.on_selected_values(instance, instance.text)
                self.on_selected_values(instance, instance.text)

    def on_selected_values(self, instance=None, value=None, *args):
        if value:
            self.type_btn.text = 'Chosen Types: ' + ', '.join(self.selected_type_values)
            self.type_search()
        else:
            self.type_btn.text = 'Chosen Types: '

    def type_search(self, *args):
        types = ['General', 'School', 'Work', 'Home', 'Other']

        self.search_results = []
        for type in sorted(self.selected_type_values):
            self.cur.execute('select * from tasks where type = ?', (type,))
            for res in self.cur.fetchall():
                self.search_results.append(res)

        self.t2_results_grid.clear_widgets()
        for res in self.search_results:
            b = Button(text=str(res[1:-1]), size_hint_y=None, height=50, font_size=20, halign='left')
            b.bind(size=b.setter('text_size'))
            self.t2_results_grid.add_widget(b)

    def Date(self, *args):
        if self.search_options_active['Date'] == 0:

            s = self.search_options_active
            [s.update({key: 0}) for key in s.keys()]

            self.t2_subheader.clear_widgets()

            # ---
            self.month_btn = Button(text='Chosen Months: ')
            self.month_btn.bind(
                width=lambda *x: self.month_btn.setter('text_size')(self.month_btn, (self.month_btn.width, None)),
            )
            self.selected_month_values = []
            self.month_list = DropDown(max_height=288)
            self.month_list.name = 'month_list'
            types = ['General', 'School', 'Work', 'Home', 'Other']

            for value in range(1, 13):
                b = ToggleButton(size_hint=(1, None), height='48dp', text=('0' if value < 10 else '') + str(value))
                b.bind(state=self.select_date_value)
                self.month_list.add_widget(b)

            self.month_btn.bind(on_release=self.month_list.open)
            self.t2_subheader.add_widget(self.month_btn)
            # ---

            # ---
            self.day_btn = Button(text='Chosen days: ')
            self.day_btn.bind(
                width=lambda *x: self.day_btn.setter('text_size')(self.day_btn, (self.day_btn.width, None)),
            )
            self.selected_day_values = []
            self.day_list = DropDown(max_height=288)
            self.day_list.name = 'day_list'
            types = ['General', 'School', 'Work', 'Home', 'Other']

            for value in range(1, 32):
                b = ToggleButton(size_hint=(1, None), height='48dp', text=('0' if value < 10 else '') + str(value))
                b.bind(state=self.select_date_value)
                self.day_list.add_widget(b)

            self.day_btn.bind(on_release=self.day_list.open)
            self.t2_subheader.add_widget(self.day_btn)
            # ---

            # ---
            self.year_btn = Button(text='Chosen years: ')
            self.year_btn.bind(
                width=lambda *x: self.year_btn.setter('text_size')(self.year_btn, (self.year_btn.width, None)),
            )
            self.selected_year_values = []
            self.year_list = DropDown(max_height=288)
            self.year_list.name = 'year_list'
            types = ['General', 'School', 'Work', 'Home', 'Other']

            for value in range(date.today().year, date.today().year + 4):
                b = ToggleButton(size_hint=(1, None), height='48dp', text=str(value))
                b.bind(state=self.select_date_value)
                self.year_list.add_widget(b)

            self.year_btn.bind(on_release=self.year_list.open)
            self.t2_subheader.add_widget(self.year_btn)
            # ---

            self.t2_results_grid.clear_widgets()
            for i in range(1, 53):
                month = Button(text=('0' if i < 10 else '') + str(i), size_hint_y=None, height=40)
                month.bind(size=self.scale_text_btn, on_press=self.set_btn)
                self.t2_results_grid.add_widget(month)
            self.search_options_active['Date'] = 1
        else:
            temp_children = list(self.t2_results_grid.children)
            self.t2_results_grid.clear_widgets()
            for tc in temp_children:
                self.t2_results_grid.add_widget(tc)

    def select_date_value(self, instance=None, value=None, *args):
        if value == 'down':
            if instance.parent.parent is self.month_list:
                if instance.text not in self.selected_month_values:
                    self.selected_month_values.append(instance.text)
                    self.on_selected_months(instance, instance.text)
            elif instance.parent.parent is self.day_list:
                if instance.text not in self.selected_day_values:
                    self.selected_day_values.append(instance.text)
                    self.on_selected_days(instance, instance.text)
            else:
                if instance.text not in self.selected_year_values:
                    self.selected_year_values.append(instance.text)
                    self.on_selected_years(instance, instance.text)
        else:
            if instance.parent is self.month_list:
                if instance.text in self.selected_month_values:
                    self.selected_month_values.append(instance.text)
                    self.on_selected_months(instance, instance.text)
            elif instance.parent is self.day_list:
                if instance.text in self.selected_day_values:
                    self.selected_day_values.append(instance.text)
                    self.on_selected_days(instance, instance.text)
            else:
                if instance.text in self.selected_year_values:
                    self.selected_year_values.append(instance.text)
                    self.on_selected_years(instance, instance.text)

    def on_selected_months(self, instance=None, value=None, *args):
        if value:
            self.month_btn.text = 'Chosen Months: ' + ', '.join(self.selected_month_values)
            self.date_search()
        else:
            self.month_btn.text = 'Chosen Months: '

    def on_selected_days(self, instance=None, value=None, *args):
        if value:
            self.day_btn.text = 'Chosen Days: ' + ', '.join(self.selected_day_values)
            self.date_search()
        else:
            self.day_btn.text = 'Chosen Days: '

    def on_selected_years(self, instance=None, value=None, *args):
        if value:
            self.year_btn.text = 'Chosen Years: ' + ', '.join(self.selected_year_values)
            self.date_search()
        else:
            self.year_btn.text = 'Chosen Years: '

    def date_search(self, *args):
        self.search_results = []
        self.t2_results_grid.clear_widgets()
        search_query = ''
        search_query_tuple = tuple()
        self.cur.execute('select * from tasks')
        results = self.cur.fetchall()
        final = final2 = final3 = []

        if self.selected_month_values:
            for month in self.selected_month_values:
                final += [res for res in results if res[3][:2] in month]
            final2 = final3 = final

        if self.selected_day_values:
            final2 = []
            for day in self.selected_day_values:
                final2 += [res for res in results if res[3][3:5] in day]
            final3 = final2

        if self.selected_year_values:
            final3 = []
            for year in self.selected_year_values:
                final3 += [res for res in results if res[3][6:] in year]

        if results:
            for res in final3:
                self.t2_results_grid.add_widget(Button(text=str(res), size_hint_y=None, height=50))

    def Time(self, *args):
        if self.search_options_active['Time'] == 0:

            s = self.search_options_active
            [s.update({key: 0}) for key in s.keys()]

            self.t2_subheader.clear_widgets()

            # ---
            self.hour_btn = Button(text='Chosen Hours: ')
            self.hour_btn.bind(
                width=lambda *x: self.hour_btn.setter('text_size')(self.hour_btn, (self.hour_btn.width, None)),
            )
            self.selected_hour_values = []
            self.hour_list = DropDown(max_height=288)
            self.hour_list.name = 'hour_list'
            types = ['General', 'School', 'Work', 'Home', 'Other']

            for value in range(1, 13):
                b = ToggleButton(size_hint=(1, None), height='48dp', text=('0' if value < 10 else '') + str(value))
                b.bind(state=self.select_time_value)
                self.hour_list.add_widget(b)

            self.hour_btn.bind(on_release=self.hour_list.open)
            self.t2_subheader.add_widget(self.hour_btn)
            # ---

            # ---
            self.minute_btn = Button(text='Chosen Minutes: ')
            self.minute_btn.bind(
                width=lambda *x: self.minute_btn.setter('text_size')(self.minute_btn, (self.minute_btn.width, None)),
            )
            self.selected_minute_values = []
            self.minute_list = DropDown(max_height=288)
            self.minute_list.name = 'minute_list'
            types = ['General', 'School', 'Work', 'Home', 'Other']

            for value in range(1, 32):
                b = ToggleButton(size_hint=(1, None), height='48dp', text=('0' if value < 10 else '') + str(value))
                b.bind(state=self.select_time_value)
                self.minute_list.add_widget(b)

            self.minute_btn.bind(on_release=self.minute_list.open)
            self.t2_subheader.add_widget(self.minute_btn)
            # ---

            # ---
            self.ampm_btn = Button(text='Chosen AM/PM: ')
            self.ampm_btn.bind(
                width=lambda *x: self.ampm_btn.setter('text_size')(self.ampm_btn, (self.ampm_btn.width, None)),
            )
            self.selected_ampm_values = []
            self.ampm_list = DropDown(max_height=288)
            self.ampm_list.name = 'ampm_list'
            types = ['General', 'School', 'Work', 'Home', 'Other']

            for value in ['am', 'pm']:
                b = ToggleButton(size_hint=(1, None), height='48dp', text=value)
                b.bind(state=self.select_time_value)
                self.ampm_list.add_widget(b)

            self.ampm_btn.bind(on_release=self.ampm_list.open)
            self.t2_subheader.add_widget(self.ampm_btn)
            # ---

            self.search_options_active['Time'] = 1
        else:
            temp_children = list(self.t2_results_grid.children)
            self.t2_results_grid.clear_widgets()
            for tc in temp_children:
                self.t2_results_grid.add_widget(tc)

    def select_time_value(self, instance=None, value=None, *args):
        if value == 'down':
            if instance.parent.parent is self.hour_list:
                if instance.text not in self.selected_hour_values:
                    self.selected_hour_values.append(instance.text)
                    self.on_selected_hours(instance, instance.text)
            elif instance.parent.parent is self.minute_list:
                if instance.text not in self.selected_minute_values:
                    self.selected_minute_values.append(instance.text)
                    self.on_selected_mins(instance, instance.text)
            else:
                if instance.text not in self.selected_ampm_values:
                    self.selected_ampm_values.append(instance.text)
                    self.on_selected_ampm(instance, instance.text)
        else:
            if instance.parent is self.hour_list:
                if instance.text in self.selected_month_values:
                    self.selected_hour_values.append(instance.text)
                    self.on_selected_hours(instance, instance.text)
            elif instance.parent is self.minute_list:
                if instance.text in self.selected_minute_values:
                    self.selected_minute_values.append(instance.text)
                    self.on_selected_mins(instance, instance.text)
            else:
                if instance.text in self.selected_ampm_values:
                    self.selected_ampm_values.append(instance.text)
                    self.on_selected_ampm(instance, instance.text)

    def on_selected_hours(self, instance=None, value=None, *args):
        if value:
            self.hour_btn.text = 'Chosen Hours: ' + ', '.join(self.selected_hour_values)
            self.time_search()
        else:
            self.hour_btn.text = 'Chosen Hours: '

    def on_selected_mins(self, instance=None, value=None, *args):
        if value:
            self.minute_btn.text = 'Chosen Minutes: ' + ', '.join(self.selected_minute_values)
            self.time_search()
        else:
            self.minute_btn.text = 'Chosen Minutes: '

    def on_selected_ampm(self, instance=None, value=None, *args):
        if value:
            self.ampm_btn.text = 'Chosen AM/PM: ' + ', '.join(self.selected_ampm_values)
            self.time_search()
        else:
            self.ampm_btn.text = 'Chosen AM/PM: '

    def time_search(self, *args):
        self.search_results = []
        self.t2_results_grid.clear_widgets()
        search_query = ''
        search_query_tuple = tuple()
        self.cur.execute('select * from tasks')
        results = self.cur.fetchall()
        final = final2 = final3 = []

        if self.selected_hour_values:
            for hour in self.selected_hour_values:
                final += [res for res in results if res[8][:2] in hour or res[9][:2] in hour]
            final2 = final3 = final

        if self.selected_minute_values:
            final2 = []
            for minute in self.selected_minute_values:
                final2 += [res for res in results if res[8][3:5] in minute or res[9][3:5] in minute]
            final3 = final2

        if self.selected_ampm_values:
            final3 = []
            for ampm in self.selected_ampm_values:
                final3 += [res for res in results if res[8][6:] in ampm or res[9][6:] in ampm]
        if results:
            for res in final3:
                self.t2_results_grid.add_widget(Button(text=str(res), size_hint_y=None, height=50))

    def Group(self, *args):
        if self.search_options_active['Group'] == 0:

            [self.search_options_active.update({key: 0}) for key in self.search_options_active.keys()]

            self.t2_subheader.clear_widgets()

            self.group_btn2 = Button(text='Chosen Groups: ', font_size=20)
            self.group_btn2.bind(
                width=lambda *x: self.group_btn2.setter('text_size')(self.group_btn2, (self.group_btn2.width, None)),
            )
            self.selected_group_values = []
            self.group_list2 = DropDown(max_height=288)
            self.cur.execute('select * from _groups')
            groups = self.cur.fetchall() 

            for value in groups:
                b = ToggleButton(size_hint=(1, None), height='48dp', text=str(value[1]), font_size=20)
                b.bind(state=self.select_group_value)
                self.group_list2.add_widget(b)

            self.group_btn2.bind(on_release=self.group_list2.open)
            self.t2_subheader.add_widget(self.group_btn2)
            
            self.search_options_active['Group'] = 1
        else:
            temp_children = list(self.t2_results_grid.children)
            self.t2_results_grid.clear_widgets()
            for tc in temp_children:
                self.t2_results_grid.add_widget(tc)

    def select_group_value(self, instance=None, value=None, *args):
        if value == 'down':
            if instance.text not in self.selected_group_values:
                self.selected_group_values.append(instance.text)
                self.on_selected_groups(instance, instance.text)
        else:
            if instance.text in self.selected_group_values:
                self.selected_group_values.remove(instance.text)
                self.on_selected_groups(instance, instance.text)
                self.on_selected_groups(instance, instance.text)

    def on_selected_groups(self, instance=None, value=None, *args):
        if value:
            self.group_btn2.text = 'Chosen Groups: ' + ', '.join(self.selected_group_values)
            self.group_search()
        else:
            self.group_btn2.text = 'Chosen Groups: '

    def group_search(self, *args):
        self.search_results = []
        for group in sorted(self.selected_group_values):
            self.cur.execute('select * from tasks where _group = ?', (group,))
            for res in self.cur.fetchall():
                self.search_results.append(res)

        self.t2_results_grid.clear_widgets()
        for res in self.search_results:
            self.t2_results_grid.add_widget(Button(text=str(res), size_hint_y=None, height=50))

    def Project(self, *args):
        if self.search_options_active['Project'] == 0:

            [self.search_options_active.update({key: 0}) for key in self.search_options_active.keys()]

            self.t2_subheader.clear_widgets()

            self.project_btn2 = Button(text='Chosen Projects: ', font_size=20)
            self.project_btn2.bind(
                width=lambda *x: self.project_btn2.setter('text_size')(self.project_btn2, (self.project_btn2.width, None)),
            )
            self.selected_project_values = []
            self.project_list2 = DropDown(max_height=288)
            self.cur.execute('select * from projects')
            projects = self.cur.fetchall()

            for value in projects:
                b = ToggleButton(size_hint=(1, None), height='48dp', text=str(value[1]), font_size=20)
                b.bind(state=self.select_project_value)
                self.project_list2.add_widget(b)

            self.project_btn2.bind(on_release=self.project_list2.open)
            self.t2_subheader.add_widget(self.project_btn2)

            self.search_options_active['Project'] = 1
        else:
            temp_children = list(self.t2_results_grid.children)
            self.t2_results_grid.clear_widgets()
            for tc in temp_children:
                self.t2_results_grid.add_widget(tc)

    def select_project_value(self, instance=None, value=None, *args):
        if value == 'down':
            if instance.text not in self.selected_project_values:
                self.selected_project_values.append(instance.text)
                self.on_selected_projects(instance, instance.text)
        else:
            if instance.text in self.selected_project_values:
                self.selected_project_values.remove(instance.text)
                self.on_selected_projects(instance, instance.text)
                self.on_selected_projects(instance, instance.text)

    def on_selected_projects(self, instance=None, value=None, *args):
        if value:
            self.project_btn2.text = 'Chosen projects: ' + ', '.join(self.selected_project_values)
            self.project_search()
        else:
            self.project_btn2.text = 'Chosen projects: '

    def project_search(self, *args):
        self.search_results = []
        for project in sorted(self.selected_project_values):
            self.cur.execute('select * from tasks where project = ?', (project,))
            for res in self.cur.fetchall():
                self.search_results.append(res)

        self.t2_results_grid.clear_widgets()
        for res in self.search_results:
            self.t2_results_grid.add_widget(Button(text=str(res), size_hint_y=None, height=50))

    def Created(self, *args):
        if self.search_options_active['Created'] == 0:

            s = self.search_options_active
            [s.update({key: 0}) for key in s.keys()]

            self.t2_subheader.clear_widgets()

            # add subheader options

            self.t2_results_grid.clear_widgets()
            for i in range(1, 53):
                month = Button(text=('0' if i < 10 else '') + str(i), size_hint_y=None, height=40)
                month.bind(size=self.scale_text_btn, on_press=self.set_btn)
                self.t2_results_grid.add_widget(month)
            self.search_options_active['Created'] = 1
        else:
            temp_children = list(self.t2_results_grid.children)
            self.t2_results_grid.clear_widgets()
            for tc in temp_children:
                self.t2_results_grid.add_widget(tc)


    def do_this(self, instance, *args):
        instance.text_size = self.size

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
                    temp = str(self.st)
                    self.st = str(self.et)
                    self.et = temp

                self.set_vbls()
                insert_vbls = 'INSERT INTO tasks VALUES(?, '
                insert_vals = [None,]
                i = 0
                for vbl in self.vbls:
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

                vbl_names = ['name', 'note', 'date', 'type', 'deadline', 'reminder', 'exclusive', 'start_time',
                             'end_time', 'every_amt', 'every_unit', 'for_amt', 'for_unit', '_group', 'project',
                             'cal_compat']

                info = dict(zip(vbl_names, insert_vals[1:]))
                new_task = Task(info=info, tm=self)

                if new_task.info['start_time'] is None:
                    new_task.info['cal_compat'] = 0
                    insert_vals[-1] = 0
                    self.task_to_vault(task=new_task)
                elif self.check_cal_compat(task=new_task):
                    new_task.info['cal_compat'] = 1
                    insert_vals[-1] = 1
                    self.cur.execute(insert_vbls, tuple(insert_vals))
                    self.conn.commit()
                    current_week = [d.dom for d in self.sections['calendar'].current_week.days]
                    if new_task.info['date'] in current_week:
                        x = current_week.index(new_task.info['date'])
                        self.sections['calendar'].current_week.days[x].add_tasks2(cur=self.cur,
                                                                                  dom=new_task.info['date'],
                                                                                  sects=self.sections,
                                                                                  overlap=new_task.info['exclusive'])
                else:
                    new_task.info['cal_compat'] = 0
                    insert_vals[-1] = 0
                    # may change around a little
                    self.task_to_vault(task=new_task)

                if insert_vals[-1] == 0:
                    self.cur.execute(insert_vbls, tuple(insert_vals))
                    self.conn.commit()

    def clear_task(self, *args):
        pass

    def check_cal_compat(self, task=None, *args):
        if task is not None:
            self.cur.execute('''SELECT date, start_time, end_time, exclusive
                                from tasks where date = ? and cal_compat = 1''', (task.info['date'],))
            same_day_tasks = self.cur.fetchall()
            this_start = int(task.info['start_time'][:2] + task.info['start_time'][3:5])
            this_end = int(task.info['end_time'][:2] + task.info['end_time'][3:5])
            for t in same_day_tasks:
                other_start = int(t[1][:2] + t[1][3:5])
                other_end = int(t[2][:2] + t[2][3:5])
                if (other_start <= this_start <= other_end or other_start <= this_end <= other_end)\
                        and (t[3] or task.info['exclusive']):
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
                if int(self.year_in) == int(date.today().year):
                    if int(self.month_in) == int(date.today().month):
                        if int(self.day_in) >= int(date.today().day):
                            self.date = self.month_in + '-' + self.day_in + '-' + self.year_in
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
                if self.end_time.hour_in or self.end_time.minute_in or self.end_time.ampm_chosen:
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
                if self.start_time.hour_in or self.start_time.minute_in or self.start_time.ampm_chosen:
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

        self.vbls = [self.name_in.text, self.note.text, self.date, self.type.text,
                     self.deadline.active, self.reminder.active, self.exclusive.active,
                     self.st, self.et, self.every_amt, self.every_units.text, self.For_amt,
                     self.For_units.text, self.group_btn.text, self.project_btn.text, self.compat]

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
                instance.background_color = (0, 1, 0, 1)
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

    def task_to_vault(self, task=None, *args):
        pass

    def task_to_cal(self, task=None, *args):
        if task is not None:
            for day in self.sections['calendar'].current_week.days:
                print('\n--------------------\nDay\n--------------------''', day.scroll_grid.children)
                d = day.scroll_grid
                if task.info['date'] == day.date:
                    print('''if task.info['date'] == day.date:''')
                    print('Task:\n', task, task.info['start_time'], task.info['end_time'])
                    children = [c for c in reversed(d.children) if isinstance(c, (Task, GridLayout, Button))]
                    d.clear_widgets()
                    i = 0
                    top = task.loc + task.length
                    bottom = task.loc
                    spot = 0
                    y = 0
                    total_y = len([t for t in children if isinstance(t, (Task, GridLayout, Button))])
                    print('total_y', total_y)
                    for c in children:
                        print('______\nChild\n______''')
                        print(type(c), c.height)
                        # try:
                        #     if c.info['start_time'] == task.info['start_time'] \
                        #             and c.info['end_time'] == task.info['end_time'] \
                        #             and c.info['name'] == task.info['name']:
                        #         print('-+-+-Same Task-+-+-')
                        #         continue
                        # except:
                        #     pass
                        print(c, c.height, c.pos)
                        spot += c.height
                        print(top, c.pos[1] + c.height, bottom, c.pos[1])

                        if i == 0:
                            print('if i == 0')
                            l.height = d.height - top
                        else:
                            try:
                                l.height = (children[i - 1].pos[1] if children[i - 1].pos[1] != 0 else
                                            children[i - 1].loc) - top
                            except:
                                l.height = (children[i - 1].pos[1] if children[i - 1].pos[1] != 0 else
                                            d.height - spot + c.height) - top
                        d.add_widget(l)

                        if top <= c.pos[1] + c.height and bottom >= c.pos[1]: # \
                                # or top <= c.pos[1] + c.height and bottom <= c.pos[1] \
                                # or top >= c.pos[1] + c.height and bottom >= c.pos[1]:
                            print('if top <= c.pos[1] + c.height and bottom >= c.pos[1]:')
                            l = Label(size_hint_y=None)
                            # if i == 0:
                            #     print('if i == 0')
                            #     l.height = d.height - top
                            # else:
                            #     try:
                            #         l.height = (children[i - 1].pos[1] if children[i - 1].pos[1] != 0 else
                            #                     children[i - 1].loc) - top
                            #     except:
                            #         l.height = (children[i - 1].pos[1] if children[i - 1].pos[1] != 0 else
                            #                     d.height - spot + c.height) - top
                            # d.add_widget(l)

                            z = 0
                            try:
                                task.parent.remove_widget(task)
                            except:
                                pass
                            # if c.loc > task.loc and not isinstance(c, Button):
                            #     d.add_widget(c)
                            d.add_widget(task)
                            y += 1
                            if isinstance(task, GridLayout):
                                to_add = []
                                for grid in task.children:
                                    z += 1
                                    for child in grid.children:
                                        if isinstance(child, Task):
                                            to_add.append(child)
                            else:
                                to_add = [task]
                                if task.height > task.parent.parent.height > 100:
                                    print('drag is false')
                                    task.set_draggable(False)
                            for j in range(len(to_add)):
                                to_add[j].remove_on_drag = False
                                to_add[j].drop_func = to_add[j].place_task
                                to_add[j].not_drop_ok_do_animation = False
                                to_add[j].drop_ok_do_animation = False
                                to_add[j].drag_start_func = to_add[j].pick_up
                                to_add[j].while_dragging_func = to_add[j].hold
                                to_add[j].droppable_zone_objects = to_add[j].tm.sections['calendar'].current_week.days

                                if to_add[j].height > task.parent.parent.height > 100:
                                    print('drag is false')
                                    to_add[j].set_draggable(False)

                            l = Label(size_hint_y=None)
                            if i == len(children) - 1 or i == len(children):
                                print('if label')
                                print(len(children), i)
                                l.height = bottom
                            else:
                                print('else label', task.loc, children[i + 1].pos[1], children[i + 1].height)
                                print(len(children), i)
                                l.height = task.loc - (children[i + 1].pos[1] + children[i + 1].height)
                            print('___bottom label height___', l.height)
                            try:
                                if task.loc - (children[i + 1].pos[1] + children[i + 1].height) > 0:
                                    d.add_widget(l)
                            except:
                                # if y == total_y != 0:
                                #     l.height = bottom
                                d.add_widget(l)
                        else:
                            d.add_widget(c)
                        i += 1
                        print('did it even get here')
                    n = 0
                    # if len(d.children) > y + 2:
                    #     for h in list(reversed(d.children)):
                    #         if h not in d.children:
                    #             n += 1
                    #             continue
                    #         if isinstance(h, Label):
                    #             d.remove_widget(h)
                    #             for r in range(n + 1,len(d.children)):
                    #                 e = list(reversed(d.children))
                    #                 if isinstance(e[r], Label):
                    #                     h.height += e[r].height
                    #                     d.remove_widget(e[r])
                    #                 else:
                    #                     d.add_widget(h)
                    #                     break
                    #             if h.parent is not d:
                    #                 d.add_widget(h)
                    #         n += 1

    def task_to_cal2(self, tasks=None, *args):
        # print(tasks)
        if tasks:
            for day in self.sections['calendar'].current_week.days:
                if tasks[0].info['date'] == day.date:
                    d = day.scroll_grid
                    d.clear_widgets()
                    i = 0
                    current_loc = d.height
                    for task in tasks:
                        top = task.loc + task.length
                        bottom = task.loc
                        print(top, d.height, i, current_loc)
                        if top != d.height and i == 0 or i != 0 and top != current_loc:
                            print('if top != d.height or (i != 0 and top != d.children[0].loc):')
                            l = Label(size_hint_y=None)
                            if i == 0:
                                l.height = d.height - top
                            else:
                                l.height = d.children[0].loc - top
                            l.loc = top
                            d.add_widget(l)
                            current_loc -= l.height
                        d.add_widget(task)
                        if isinstance(task, Task):
                            cw = task.tm.sections['calendar'].current_week.days
                            task.hover_day = [d for d in cw if d.dom == task.info['date']]
                        current_loc -= task.height
                        i += 1

                        z = 0
                        if isinstance(task, GridLayout):
                            to_add = []
                            for grid in task.children:
                                z += 1
                                for child in grid.children:
                                    if isinstance(child, Task):
                                        to_add.append(child)
                        else:
                            to_add = [task]
                            if task.height > task.parent.parent.height > 100:
                                print('drag is false')
                                task.set_draggable(False)

                        for j in range(len(to_add)):
                            to_add[j].remove_on_drag = False
                            to_add[j].drop_func = to_add[j].place_task
                            to_add[j].not_drop_ok_do_animation = False
                            to_add[j].drop_ok_do_animation = False
                            to_add[j].drag_start_func = to_add[j].pick_up
                            to_add[j].while_dragging_func = to_add[j].hold
                            to_add[j].droppable_zone_objects = to_add[j].tm.sections['calendar'].current_week.days

                            if to_add[j].height > task.parent.parent.height > 100:
                                print('drag is false')
                                to_add[j].set_draggable(False)

                    if d.children[0].loc != 0:
                        l = Label(size_hint_y=None, height=d.children[0].loc)
                        l.loc = 0
                        d.add_widget(l)


class Task(Button, DragNDropWidget):
    def __init__(self, info=None, tm=None, instance=None, **kwargs):
        super(Task, self).__init__(**kwargs)
        self.size_hint_y = None

        if info is not None:
            self.info = info

        self.text = self.info['name'] + '\n' + self.info['start_time']+ '\n' + self.info['end_time']

        if self.info['end_time'] is not None:
            end_h = int(self.info['end_time'][:2])
            end_m = int(self.info['end_time'][3:5])
            start_h = int(self.info['start_time'][:2])
            start_m = int(self.info['start_time'][3:5])

            if tm:
                self.tm = tm
                day = tm.sections['calendar'].current_week.days[1].scroll_grid
                day_height = day.height
            else:
                day_height = 2880

            if self.info['end_time'][-2:] == self.info['start_time'][-2:]:
                self.length = ((end_h * (0 if end_h == 12 else 1) * 120 + end_m * 2 - start_h *
                                (0 if start_h == 12 else 1) * 120 - start_m * 2) / float(day_height)) * day_height
                self.loc = ((day_height if self.info['end_time'][-2:] == 'am' else day_height/2.) - end_h *
                            (0 if end_h == 12 else 1) * 120 - end_m * 2) # here
            else:
                self.length = ((end_h * (0 if end_h == 12 else 1) * 120 + end_m * 2 - start_h *
                                120 - start_m * 2 + day_height / 2) / float(day_height)) * day_height
                self.loc = (day_height / 2 - end_h * (0 if end_h == 12 else 1) * 120 - end_m * 2)

            self.height = self.length
            self.start_label = Label(text=self.info['start_time'])
            self.bind(on_touch_down=self.check_tap)

            if self.info['type'] == 'General':
                self.background_color = (.7, .7, 1, .65)
            elif self.info['type'] == 'School':
                self.background_color = (.7, 1, .7, .65)
            elif self.info['type'] == 'Work':
                self.background_color = (1, .7, .7, .65)
            elif self.info['type'] == 'Home':
                self.background_color = (1, .4, 1, .65)
            elif self.info['type'] == 'Other':
                self.background_color = (.4, 1, 1, .65)


    def check_tap(self, instance, touch, *args):
        if touch.is_double_tap:
            self.tm.view_task(instance=instance)

    def place_task(self, instance, *args):
        # instance.center = (instance.pos[0] + instance.width / 2, instance.pos[1] + instance.height / 2)
        tasks = [t for t in reversed(instance.current_week[instance.hover_day].scroll_grid.children)
                 if isinstance(t, (Task, GridLayout))]
        print('all tasks in day', tasks)
        for i in range(len(tasks)):
            if tasks[i] is not self:
                if isinstance(tasks[i], GridLayout):
                    tasks[i].info = {'exclusive': 0}
                print(time.time() - instance.start_hover < .5)
                print(instance.end - tasks[i].loc - tasks[i].height > .5)
                print(instance.start - tasks[i].pos[1] < .5)
                print(tasks[i].info['exclusive'] == 1)
                print(instance.info['exclusive'] == 1)
                if time.time() - instance.start_hover < .5\
                        or instance.end - tasks[i].loc - tasks[i].height > .5\
                        or instance.start - tasks[i].pos[1] < .5\
                        or tasks[i].info['exclusive'] == 1\
                        or instance.info['exclusive'] == 1:
                    print('overlap = False')
                    instance.overlap = False
                    if instance.end <= tasks[i].pos[1] <= instance.start \
                            or (instance.start + instance.end) / 2 <= tasks[i].pos[1] + tasks[i].height / 2 \
                            and instance.end >= tasks[i].pos[1] and instance.start <= tasks[i].pos[1] + tasks[i].height:
                        try:
                            if instance.end <= tasks[i + 1].pos[1] + tasks[i + 1].height <= instance.start \
                                    and tasks[i - 1] is not self:
                                return
                        except:
                            pass
                        if tasks[i].pos[1] - instance.height < 0:
                            return
                        print('in place task to adjust task place to below', type(tasks[i]))
                        instance.start = tasks[i].pos[1] - 3
                        instance.end = instance.start - instance.height
                        instance.start_time, instance.end_time = self.get_held_task_time(instance)
                    elif instance.end <= tasks[i].pos[1] + tasks[i].height <= instance.start \
                            or (instance.start + instance.end) / 2 > tasks[i].pos[1] + tasks[i].height / 2 \
                            and instance.end >= tasks[i].pos[1] and instance.start <= tasks[i].pos[1] + tasks[i].height:
                        if instance.end <= tasks[i - 1].pos[1] <= instance.start and tasks[i - 1] is not self:
                            return
                        elif tasks[i].pos[1] + tasks[i].height + instance.height > instance.og_parent.height:
                            return
                        print('in place task to adjust task place to above', type(tasks[i]))
                        instance.end = tasks[i].pos[1] + tasks[i].height - 2
                        instance.start = instance.end + instance.height
                        instance.start_time, instance.end_time = self.get_held_task_time(instance)
                else:
                    print('overlap = True')
                    instance.overlap = True
        self.tm.cur.execute('select * from tasks where date = ?', (instance.current_week[instance.hover_day].date,))

        self.tm.cur.execute('''update tasks set start_time = ?,
                                                end_time = ?,
                                                date = ?
                                                where id = ?''',
                            (instance.start_time, instance.end_time,
                             instance.current_week[instance.hover_day].date, instance.dbid))
        self.tm.conn.commit()

        try:
            if instance.overlap:
                pass
        except:
            instance.overlap = False

        instance.current_week[instance.hover_day].add_tasks2(cur=self.tm.cur,
                                                             dom=instance.current_week[instance.hover_day].date,
                                                             sects=self.tm.sections,
                                                             overlap=instance.overlap)

        instance.og_parent.clear_widgets()
        instance.og_parent.add_widget(Button(size_hint_y=None,
                                             height=instance.og_parent.height,
                                             background_color=(0, 0, 0, 0)))

        self.parent = None

        instance.current_week[instance.parent_index].add_tasks2(cur=self.tm.cur,
                                                                dom=instance.current_week[instance.parent_index].date,
                                                                sects=self.tm.sections)

    def dont_pick_up(self, *args, copy=None):
        pass

    def pick_up(self, *args, copy=None):

        copy.start_hover = time.time()
        copy.touch_pos = [-11, -11]
        copy.og_parent = copy.parent
        copy.day_spaces = [(day.pos[0], day.pos[0] + day.width) for day in
                           copy.tm.sections['calendar'].current_week.days]
        copy.day_scrolls = [day.scroll.scroll_y for day in copy.tm.sections['calendar'].current_week.days]
        copy.current_week = self.tm.sections['calendar'].current_week.days
        try:
            copy.parent_index = copy.current_week.index(copy.parent.parent.parent.parent)
        except:
            copy.parent_index = copy.current_week.index(copy.parent.parent.parent.parent.parent.parent)
        copy.offset = Window.children[0].calendar_tools.height + Window.children[0].inbox.height
        copy.duration = int(copy.info['end_time'][:2]) * 60 + int(copy.info['end_time'][3:5]) -\
                        (int(copy.info['start_time'][:2]) * 60 + int(copy.info['start_time'][3:5]))
        if copy.info['start_time'][-2:] != copy.info['end_time'][-2:]:
            copy.duration += copy.og_parent.height / 2

        self.tm.cur.execute('select * from tasks where start_time = ? and date = ?', (self.info['start_time'],
                                                                                      self.info['date']))
        self.dbid = copy.dbid = self.tm.cur.fetchall()[0][0]

        copy.parent = None
        copy.size_hint_x = None
        copy.width = Window.children[-1].sections['calendar'].current_week.days[1].scroll.width
        copy.bind(pos=copy.hold)

        copy.min_x = copy.current_week[0].pos[0]
        copy.max_x = copy.current_week[-1].pos[0] + copy.current_week[-1].width - copy.width
        copy.min_y = Window.children[0].inbox.height + Window.children[0].calendar_tools.height - 2
        copy.max_y = copy.min_y + copy.current_week[0].height - copy.current_week[0].label.height - copy.height - 5

    def kivydnd_copy(self, *args):
        return Task(info=self.info, tm=self.tm)

    def hold(self, instance, touch):

        instance.hover_time(touch=touch)
        # center = instance.pos[0] + 1/2 * instance.width

        try:
            hover_day = instance.day_spaces.index([day for day in instance.day_spaces
                                                   if day[0] <= instance.center[0] <= day[1]][0])
        except:
            hover_day = instance.parent_index

        top = int(ceil(instance.current_week[hover_day].scroll_grid.height *
                       instance.current_week[hover_day].scroll.scroll_y +
                       (1 - instance.current_week[hover_day].scroll.scroll_y) *
                       instance.current_week[hover_day].scroll.height))
        bottom = ceil(top - instance.current_week[hover_day].scroll.height)
        instance.end = ceil(instance.pos[1] - instance.offset + bottom)

        instance.start = floor(instance.end + instance.height)

        instance.start_time, instance.end_time = self.get_held_task_time(instance)
        if not instance.start_time:
            return

        instance.text = instance.start_time + '\n' + instance.end_time
        instance.hover_day = hover_day

    def get_held_task_time(self, instance, *args):
        start_time = str(int(floor((instance.current_week[0].scroll_grid.height - instance.start) / (2880 / 24)))) \
                     + ':' + str(int((118 - int(instance.start % 120)) / 2))
        start_time += ' am' if instance.start > instance.current_week[0].scroll_grid.height / 2 else ' pm'
        if start_time[0] == '0':
            start_time = '12' + start_time[1:]
        if start_time[1] == ':':
            start_time = '0' + start_time
        if start_time[4] == ' ':
            start_time = start_time[:3] + '0' + start_time[3:]
        if start_time[0] == '-':
            return None, None

        end_time = str(int(start_time[:2]) + int(instance.duration // 60)) + ':' + str(int(start_time[3:5]) +
                                                                                  int(instance.duration % 60))
        if end_time[0] == '-':
            end_time = str(int(end_time[:end_time.index(':')]) + 12) + end_time[end_time.index(':'):]
        end_time += ' am' if instance.end > instance.current_week[0].scroll_grid.height / 2 else ' pm'

        if int(start_time[3:5]) + instance.duration % 60 >= 60:
            end_time = str(int(end_time[:end_time.index(':')])) + ':' + str(int(end_time[end_time.index(':') + 1:-3]) -
                                                                            60) + end_time[-3:]

        if end_time[0] == '0':
            end_time = '12' + end_time[1:]
        if end_time[1] == ':':
            end_time = '0' + end_time
        if end_time[4] == ' ':
            end_time = end_time[:3] + '0' + end_time[3:]
        if end_time[3:5] == '60':
            end_time = end_time[:3] + '00' + end_time[5:]

        if int(start_time[:2]) > 12:
            start_time = ('0' if int(start_time[:2]) - 12 < 10 else '') + str(int(start_time[:2]) - 12) + start_time[2:]
        if int(start_time[:2]) > 24:
            start_time = ('0' if int(start_time[:2]) - 24 < 10 else '') + str(int(start_time[:2]) - 24) + start_time[2:]
        if int(end_time[:2]) > 12:
            end_time = ('0' if int(end_time[:2]) - 12 < 10 else '') + str(int(end_time[:2]) - 12) + end_time[2:]
        if int(end_time[:2]) > 24:
            end_time = ('0' if int(end_time[:2]) - 24 < 10 else '') + str(int(end_time[:2]) - 24) + end_time[2:]

        return start_time, end_time

    def hover_time(self, touch=None):
        if abs(self.pos[0] - self.touch_pos[0]) > 10 or abs(self.pos[1] - self.touch_pos[1]) > 10:
            self.start_hover = time.time()
            self.touch_pos = list(touch)

class Scroll_Label(Label):
    def __init__(self, **kwargs):
        super(Scroll_Label, self).__init__(**kwargs)