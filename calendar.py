# Kivy imports
import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics.instructions import Callback
from kivy.uix.carousel import Carousel
from kivy.uix.screenmanager import ScreenManager, Screen

# Other imports
from datetime import datetime, date
from random import randint

# Custom imports
from dbms import *
from task_mgmt import *

from random import random


class Calendar(GridLayout):
    def __init__(self, **kwargs):
        super(Calendar, self).__init__(**kwargs)
        # self.size_hint = (3, 2.5)
        self.cols = 1
        self.rows = 2
        # self.bind(size=self.resize_days)

    def get_sects(self, sects=None, *args):
        if sects is not None:
            self.sections = sects

    def week_view(self, conn):
        self.create_header()

        d = date.today()
        d_str = d.strftime('%m-%d-%Y')
        dow = date.today().weekday() + 1 % 7

        cur = conn.cursor()
        cur.execute("SELECT date FROM days WHERE date LIKE \'%" + str(d.year) + "\';")
        all_days = cur.fetchall()

        i = all_days.index((d_str,))
        self.days = all_days[i - dow:i + (7 - dow)]

        self.current_week = Week(days=self.days, cur=cur)
        self.add_widget(self.current_week)

    def month_view(self):
        self.view = 'month'
        g = self.g = GridLayout(cols=7, size_hint_y=None)
        g.bind(minimum_height=g.setter('height'))
        self.clear_widgets()
        self.add_widget(g)
        return g

    def add_day(self, days, n):
        # add all days of the year
        # start at current week and highlight current day
          # scroll_to(widget, padding=10, animate=True)
            # Call after adding widgets, make padding=0 and animation=False
        # n = day number

        d = Day()
        for i in range(20):
            d.grid.add_widget(Label(text=str(n), size_hint_y=None))
        return d

    def resize_days(self, *args):
        # print(self)
        for days in self.week.children:
            days.width = Window.width / 14

    def create_header(self, *args):
        self.calendar_header = GridLayout(rows=1, cols=5, size_hint_y=.075)
        self.add_widget(self.calendar_header)
        self.calendar_header.l_label = Label(size_hint_x=1/3)
        self.calendar_header.add_widget(self.calendar_header.l_label)
        self.calendar_header.l_button = Button(size_hint_x=1/12)
        self.calendar_header.add_widget(self.calendar_header.l_button)
        self.calendar_header.middle = Label(size_hint_x=1/6)
        self.calendar_header.add_widget(self.calendar_header.middle)
        self.calendar_header.r_button = Button(size_hint_x=1/12)
        self.calendar_header.add_widget(self.calendar_header.r_button)
        self.calendar_header.r_label = Label(size_hint_x=1/3)
        self.calendar_header.add_widget(self.calendar_header.r_label)
        self.fill_header()

    def fill_header(self, *args):
        self.calendar_header.l_label.text = 'Placeholder' ##
        self.calendar_header.middle.text = 'Place-\nholder' ##
        self.calendar_header.r_label.text = 'Placeholder' ##


class Week(Screen):
    def __init__(self, days=None, cur=None, sects=None, **kwargs):
        super(Week, self).__init__(**kwargs)
        self.week_grid = GridLayout(cols=7, rows=2)
        self.add_widget(self.week_grid)
        # print(days)
        self.days = []
        for i in range(7):
            d = Day(dom=days[i][0], cur=cur, sects=sects)
            d.date = days[i][0]
            # print(days[i][0])
            self.days.append(d)
            self.week_grid.add_widget(d)

class Day(GridLayout):
    def __init__(self, c=1, dom=None, cur=None, sects=None, **kwargs): # dom = day of month
        super(Day, self).__init__(**kwargs)
        self.dom = dom
        self.rows = 2
        self.cols = 1
        self.label = Label(text=dom[3:5], size_hint_y=.075)
        self.add_widget(self.label)

        self.container = GridLayout(cols=2)

        self.add_widget(self.container)
        self.scroll = ScrollView(do_scroll_x=False, size_hint_y=.905, bar_width=0)
        self.scroll.bind(scroll_y=self.scroll_timeline)
        self.scroll_grid = GridLayout(cols=1, size_hint_y=None, height=2880)
        self.scroll_grid.bind(minimum_height=self.scroll_grid.setter('height'))
        self.scroll.add_widget(self.scroll_grid)
        self.tasks = []
        l = Button(size_hint_y=None, height=self.scroll_grid.height, background_color=(0, 0, 0, 0))
        self.scroll_grid.add_widget(l)

        # timeline
        self.timeline = ScrollView(do_scroll_x=False, size_hint_x=.095)
        self.timeline.do_scroll_y = False
        self.timeline_grid = GridLayout(cols=1, size_hint_y=None, height=2880)
        self.timeline_grid.bind(minimum_height=self.scroll_grid.setter('height'))
        self.scroll_grid.bind(pos=self.do_nothing, size=self.do_nothing)

        self.timeline.add_widget(self.timeline_grid)
        self.container.add_widget(self.timeline)
        self.container.add_widget(self.scroll)
        for i in range(24):
            b = Button(text=str(i % 12 + (12 if i % 12 == 0 else 0)), size_hint_y=None, height=(2880-0)/24, valign='top', halign='center')
            # b.bind(size=self.do_nothing2, pos=self.do_nothing2)
            # b.pos[0] = self.scroll.pos[0]
            # b.bind(pos=self.do_nothing, size=self.do_nothing)
            # b.bind(on_touch_down=self.do_nothing, on_press=self.do_nothing, on_touch_up=self.do_nothing)
            # b.disabled = True
            # b.background_down = '1'
            b.background_color = (random(), random(), random(), 1)
            b.text_size = b.size
            b.bind(size=b.setter('text_size'))
            self.timeline_grid.add_widget(b)

            # for i in range(3):
            #     t = Label(size_hint_y=None, height=1, pos=(b.pos[0] + (8 if i % 2 == 0 else 4), b.pos[1] + b.height * (1 - i/4)), width=b.width - (8 if i % 2 == 0 else 4))
            #     t.bind(pos=self.do_nothing3, size=self.do_nothing3)
            #     b.add_widget(t)

            # l = Label(size_hint_y=None, height=1)
            # l.bind(pos=self.do_nothing2, size=self.do_nothing2)
            # self.timeline_grid.add_widget(l)

    def do_nothing(self, instance, *args):
        # with self.canvas.after:
        #     Color(random(), random(), random(), .75)
        #     Rectangle(pos=instance.pos, size=instance.size)
        with instance.canvas.before:
            for i in range(24*4):
                if i % 4 == 0:
                    Color(random(), random(), random(), .5)
                    instance.rect = Rectangle(size=(self.scroll.width*2/3, 1), pos=(instance.pos[0], i*2880/(24*4)))
                elif i % 4 == 1 or i % 4 == 3:
                    Color(random(), random(), random(), .5)
                    instance.rect = Rectangle(size=(self.scroll.width*1/3, 1), pos=(instance.pos[0], i*2880/(24*4)))
                else:
                    Color(random(), random(), random(), .5)
                    instance.rect = Rectangle(size=(self.scroll.width*1/2, 1), pos=(instance.pos[0], i*2880/(24*4)))
        # instance.unbind(pos=self.do_nothing, size=self.do_nothing)

    def do_nothing2(self, instance, *args):
        with instance.canvas.before:
            Color(random(), random(), random(), .5)
            instance.rect = Rectangle(size=instance.size, pos=instance.pos)
        pass

    def do_nothing3(self, instance, *args):
        # with instance.canvas.before:
        #     Color(1, 1, 1, 1)
        #     instance.rect = Rectangle(size=instance.size, pos=instance.pos)
        pass

    def scroll_timeline(self, *args):
        self.timeline.scroll_y = self.scroll.scroll_y

    def add_tasks2(self, cur=None, dom=None, sects=None, *args):
        cur.execute('select * from tasks where date = ? and cal_compat = 1 order by start_time asc', (dom,))
        tasks = cur.fetchall()
        am = [t for t in tasks if t[8][-2:] == 'am']
        pm = [t for t in tasks if t[8][-2:] == 'pm']
        n = 0
        for i in range(len(am)):
            if am[i][8][:2] == '12':
                temp = am.pop(i)
                am.insert(n, temp)
                n += 1
        n = 0
        for i in range(len(pm)):
            if pm[i][8][:2] == '12':
                temp = pm.pop(i)
                pm.insert(n, temp)
                n += 1

        tasks = am + pm

        for t in tasks:
            pass
            # print('RIIIGHT', t)

        # organize tasks by time (when hour is 12)
        # for t in tasks:
        #     if t.info['start_time']

        vbl_names = ['name', 'note', 'date', 'type', 'deadline', 'reminder', 'exclusive', 'start_time',
                     'end_time', 'every_amt', 'every_unit', 'for_amt', 'for_unit', '_group', 'project',
                     'cal_compat']

        for t in tasks:
            if sects is not None:
                info = dict(zip(vbl_names, t[1:]))
                task = Task(info=info)

                sects['task_management'].task_to_cal(task=task)

    def print(self, touch, *args):
        if self.collide_point(*touch.pos):
            pass
            # print('ehy')

    def resize_day(self, *args):
        self.width = Window.width / 14
        # print('resize_day')
