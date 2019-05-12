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
from kivy.graphics import Line, Color, InstructionGroup

# Other imports
from datetime import datetime, date
from random import randint
from random import random, uniform

# Custom imports
from dbms import *
from task_mgmt import *


class Calendar(GridLayout):
    def __init__(self, **kwargs):
        super(Calendar, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 2

    def get_sects(self, sects=None, *args):
        if sects is not None:
            self.sections = sects

    def week_view(self, conn):
        d = date.today()
        d_str = d.strftime('%m-%d-%Y')
        self.dow = date.today().weekday() + 1 % 7
        self.month = date.today().month

        self.cur = conn.cursor()
        self.cur.execute("SELECT date FROM days WHERE date LIKE \'%" + str(d.year) + "\';")
        self.all_days = self.cur.fetchall()
        self.dow_i = self.all_days.index((d_str,))

        self.create_header()

        self.days = self.all_days[self.dow_i - self.dow:self.dow_i + 7 - self.dow]
        self.prev = self.all_days[self.dow_i - self.dow - 7:self.dow_i - self.dow]
        self.next = self.all_days[self.dow_i - self.dow + 7:self.dow_i + 14 - self.dow]

        self.current_week = Week(days=self.days, cur=self.cur)
        self.add_widget(self.current_week)

    def next_week(self, *args):
        if self.current_week is not None:
            self.remove_widget(self.current_week)
        self.prev = self.all_days[self.all_days.index((self.current_week.days[0].date,)): self.all_days.index((self.current_week.days[-1].date,)) + 1]
        self.current_week = Week(days=self.next, cur=self.cur)
        for day in self.current_week.days:
            day.add_tasks2(cur=self.cur, dom=day.dom, sects=self.sections)
        self.next = self.all_days[self.all_days.index((self.current_week.days[-1].date,)) + 1:self.all_days.index((self.current_week.days[-1].date,)) + 8]
        self.add_widget(self.current_week)

    def prev_week(self, *args):
        if self.current_week is not None:
            self.remove_widget(self.current_week)
        self.next = self.all_days[self.all_days.index((self.current_week.days[0].date,)):self.all_days.index((self.current_week.days[-1].date,)) + 1]
        self.current_week = Week(days=self.prev, cur=self.cur)
        for day in self.current_week.days:
            day.add_tasks2(cur=self.cur, dom=day.dom, sects=self.sections)
        self.prev = self.all_days[self.all_days.index((self.current_week.days[0].date,)) - 7: self.all_days.index((self.current_week.days[0].date,))]
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
        for days in self.week.children:
            days.width = Window.width / 14

    def create_header(self, *args):
        self.calendar_header = GridLayout(rows=1, cols=5, size_hint_y=.075)
        self.add_widget(self.calendar_header)
        self.calendar_header.l_button = Button(size_hint_x=1/12, text='<')
        self.calendar_header.add_widget(self.calendar_header.l_button)
        self.calendar_header.l_button.bind(size=self.scale_text, on_press=self.prev_week)
        self.calendar_header.l_label = Label(size_hint_x=1/3)
        self.calendar_header.add_widget(self.calendar_header.l_label)
        self.calendar_header.middle = Label(size_hint_x=1/6)
        self.calendar_header.add_widget(self.calendar_header.middle)
        self.calendar_header.r_label = Label(size_hint_x=1/3)
        self.calendar_header.add_widget(self.calendar_header.r_label)
        self.calendar_header.r_button = Button(size_hint_x=1/12, text='>')
        self.calendar_header.r_button.bind(size=self.scale_text, on_press=self.next_week)
        self.calendar_header.add_widget(self.calendar_header.r_button)
        self.fill_header()

    def fill_header(self, *args):
        d = datetime.now()
        self.calendar_header.l_label.text = '' ##
        self.calendar_header.middle.text = d.strftime("%B") ##
        self.calendar_header.middle.bind(size=self.scale_text)
        self.calendar_header.r_label.text = '' ##

    def scale_text(self, instance, *args):
        instance.font_size = instance.height * .75

    def print_days(self, *args):
        i = 0
        for days in self.current_week.days:
            print(i)
            for child in reversed(days.scroll_grid.children):
                print(child, child.pos[1], child.height, child.pos[1] + child.height)
            i += 1


class Week(Screen):
    def __init__(self, days=None, cur=None, sects=None, **kwargs):
        super(Week, self).__init__(**kwargs)
        self.week_grid = GridLayout(cols=7, rows=2, spacing=(4,0))
        self.add_widget(self.week_grid)
        self.days = []
        for i in range(7):
            d = Day(dom=days[i][0], cur=cur, sects=sects)
            d.date = days[i][0]
            self.days.append(d)
            self.week_grid.add_widget(d)

    def add_div(self, instance, *args):
        with instance.canvas.before:
            instance.c = Color(uniform(.7, 1), uniform(.7, 1), uniform(.7, 1), .75)
            instance.ig.add(instance.c)
            instance.r = Rectangle(size=instance.size, pos=instance.pos)
            instance.ig.add(instance.r)
            instance.canvas.add(instance.ig)


class Day(GridLayout):
    def __init__(self, c=1, dom=None, cur=None, sects=None, **kwargs): # dom = day of month
        super(Day, self).__init__(**kwargs)
        self.cur = cur
        self.dom = dom
        self.rows = 2
        self.cols = 1
        self.label = Label(text=dom[3:5], size_hint_y=.075)
        with self.label.canvas:
            Color(uniform(.2, 1), uniform(.2, 1), uniform(.2, 1), 1/7)
            self.label.rect = Rectangle(size=self.label.size, pos=self.label.pos)
        self.label.bind(size=self.do_nothing3, pos=self.do_nothing3)
        self.label.bind(size=self.scale_text)
        self.add_widget(self.label)

        self.container = GridLayout(cols=2)

        self.add_widget(self.container)
        self.scroll = ScrollView(do_scroll_x=False, size_hint_y=.905, bar_width=0)
        self.scroll.bind(scroll_y=self.scroll_timeline)
        self.scroll_grid = GridLayout(cols=1, size_hint_y=None, height=2880)
        self.scroll_grid.bind(minimum_height=self.scroll_grid.setter('height'))
        self.scroll.add_widget(self.scroll_grid)
        self.tasks = []
        l = Button(size_hint_y=None, height=self.scroll_grid.height, background_color=(0,0,0,0))
        self.scroll_grid.add_widget(l)

        # timeline
        self.timeline = ScrollView(do_scroll_x=False, size_hint_x=.095)
        self.timeline.do_scroll_y = False
        self.timeline_grid = GridLayout(cols=1, size_hint_y=None, height=2880)
        self.timeline_grid.bind(minimum_height=self.scroll_grid.setter('height'))
        self.scroll_grid.rects = []
        self.scroll_grid.bind(pos=self.do_nothing3, size=self.do_nothing)

        self.timeline.add_widget(self.timeline_grid)
        self.container.add_widget(self.timeline)
        self.container.add_widget(self.scroll)

        for i in range(24):
            l = Label(text=str(i % 12 + (12 if i % 12 == 0 else 0)), size_hint_y=None, height=(2880-0)/24, valign='top', halign='center')
            l.text_size = l.size
            with l.canvas.before:
                Color(uniform(0, 1), uniform(0, 1), uniform(0, 1), .15)
                l.rect = Rectangle(size=l.size, pos=l.pos)
            l.bind(size=self.do_nothing3)
            l.bind(size=l.setter('text_size'))
            self.timeline_grid.add_widget(l)

    def scale_text(self, instance, *args):
        instance.font_size = instance.height * .5

    def do_nothing(self, instance, *args):
        with instance.canvas.before:
            if not hasattr(instance, 'rects'):
                instance.rects = []
            if instance.rects == []:
                for i in range(24*4):
                    if i % 4 == 0:
                        Color(random(), random(), random(), .5)
                        instance.rects.append(Rectangle(size=(self.scroll.width*2/3, 1), pos=(instance.pos[0], i*2880/(24*4))))
                    elif i % 4 == 1 or i % 4 == 3:
                        Color(random(), random(), random(), .5)
                        instance.rects.append(Rectangle(size=(self.scroll.width*1/3, 1), pos=(instance.pos[0], i*2880/(24*4))))
                    else:
                        Color(random(), random(), random(), .5)
                        instance.rects.append(Rectangle(size=(self.scroll.width*1/2, 1), pos=(instance.pos[0], i*2880/(24*4))))
            else:
                i = 0
                for r in instance.rects:
                    if i % 4 == 0:
                        r.size = (self.scroll.width*2/3, 1)
                        r.pos = (instance.pos[0], i*2880/(24*4))
                    elif i % 4 == 1 or i % 4 == 3:
                        r.size = (self.scroll.width*1/3, 1)
                        r.pos = (instance.pos[0], i*2880/(24*4))
                    else:
                        r.size = (self.scroll.width*1/2, 1)
                        r.pos = (instance.pos[0], i*2880/(24*4))
                    i += 1

    def do_nothing2(self, instance, *args):
        with instance.canvas.before:
            Color(random(), random(), random(), .5)
            instance.rect = Rectangle(size=instance.size, pos=instance.pos)
        pass

    def do_nothing3(self, instance, *args):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def scroll_timeline(self, *args):
        self.timeline.scroll_y = self.scroll.scroll_y

    def add_tasks2(self, cur=None, dom=None, sects=None, overlap=True, *args):
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
        print('tasks', tasks)

        vbl_names = ['name', 'note', 'date', 'type', 'deadline', 'reminder', 'exclusive', 'start_time',
                     'end_time', 'every_amt', 'every_unit', 'for_amt', 'for_unit', '_group', 'project',
                     'cal_compat']

        added_tasks = [0 for _ in range(len(tasks) + 1)]
        z = -1
        i = 0
        task_list = []
        for t1 in tasks:
            print(added_tasks)
            z += 1
            print('i =', i)
            if added_tasks[tasks.index(t1)]:
                continue
            if sects: # and not added_tasks[i]:
                info = dict(zip(vbl_names, t1[1:]))
                task = Task(info=info, tm=sects['task_management'])
                added_tasks[tasks.index(t1)] = 1
                # i += 1

                outer_grid = GridLayout(rows=1, size_hint_y=None)
                g = GridLayout(cols=1)
                g.add_widget(task)
                outer_grid.add_widget(g)
                outer_grid.loc = task.loc
                inner_grids = [g]
                top = task.loc + task.height
                j = 1
                if not task.info['exclusive']:
                    try:
                        for t2 in tasks[i + 1:]:
                            if added_tasks[tasks.index(t2)]:
                                continue
                            info = dict(zip(vbl_names, t2[1:]))
                            task2 = Task(info=info, tm=sects['task_management'])
                            if not task2.info['exclusive']:

                                # if task 2 overlaps earliest task (task 1)
                                if task2.loc + task2.height > task.loc + .5:
                                    g = GridLayout(cols=1)
                                    inner_grids.append(g)

                                    inner_grids[j].add_widget(Label(size_hint_y=None, height=top - task2.loc - task2.height))

                                    inner_grids[j].add_widget(task2)
                                    added_tasks[tasks.index(t2)] = 1
                                    # i += 1
                                    print('indices (1):', i, j, i + j)

                                    outer_grid.add_widget(inner_grids[j])
                                    j += 1

                                elif len(inner_grids) > 1:
                                    added = False
                                    in_grid = False
                                    if task2.loc + task2.height > outer_grid.loc + .5:
                                        in_grid = True
                                    for grid in inner_grids:
                                        if task2.loc + task2.height <= grid.loc + .5 and in_grid:
                                            grid.add_widget(Label(size_hint_y=None, height=grid.children[0].loc-task2.loc-task2.height))
                                            try:
                                                grid.add_widget(task2)
                                            except:
                                                task2.parent.remove_widget(task2)
                                                grid.add_widget(task2)
                                            added_tasks[tasks.index(t2)] = 1
                                            # i += 1
                                            added = True
                                    if in_grid and not added:
                                        g = GridLayout(cols=1)
                                        inner_grids.append(g)

                                        inner_grids[j].add_widget(Label(size_hint_y=None, height=top - task2.loc - task2.height))

                                        task = Task(info=info, tm=sects['task_management'])
                                        inner_grids[j].add_widget(task2)
                                        added_tasks[tasks.index(t2)] = 1
                                        # i += 1

                                        outer_grid.add_widget(inner_grids[j])
                                        j += 1
                                else:
                                    break

                                for grid in inner_grids:
                                    if not isinstance(grid.children[0], Task):
                                        grid.remove_widget(grid.children[0])
                                    grid.loc = grid.children[0].loc
                                outer_grid.loc = min([top - sum([c.height for c in grid.children]) for grid in inner_grids])
                    except Error:
                        pass


                if len(inner_grids) > 1:
                    outer_grid.info = {'date': task.info['date']}
                    outer_grid.height = outer_grid.length = top - outer_grid.loc
                    task = outer_grid
                else:
                    print('cleared first grid widgets')
                    inner_grids[0].clear_widgets()

                # if isinstance(task, Task):
                #     added_tasks[i] = 1
                #     i += 1

                print('((((((((()))))))))))', task.loc, task.height, task.loc + task.height)

                try:
                    outer_grid.parent.remove_widget(outer_grid)
                except:
                    pass
                # print('calling task_to_cal with', task)
                task_list.append(task)
        sects['task_management'].task_to_cal2(tasks=task_list)

    def resize_day(self, *args):
        self.width = Window.width / 14
