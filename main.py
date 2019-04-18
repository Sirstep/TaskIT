# Kivy imports
import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.core.window import Window

# Custom class imports
from calendar import *
from dbms import *
from task_mgmt import *

# Other imports
from win32api import GetSystemMetrics


class Root(GridLayout):
    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)


        Window.size = (GetSystemMetrics(0) - 75, GetSystemMetrics(1))
        self.rows = 2
        self.cols = 2

        # database stuff
        conn = create_connection('database/data.db')
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON;")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='days';")
        # print(cur.fetchall())
        days_exists = len(cur.fetchall())
        if conn is not None:
            if days_exists == 0:
                fill_database(conn)
                conn.commit()
            cur.execute("SELECT * FROM days")
            n_days = len(cur.fetchall())
            if n_days == 0:
                print('fill_database')
                # function that asks user to enter year range (and maybe other info, like google calendar, etc.)
                fill_calendar(conn)
                conn.commit()
            cur.execute("SELECT * FROM days")
        else:
            print("Error! Compty cannot create the database connection.")

        cur.execute("select name from sqlite_master where type = 'table';")
        print(cur.fetchall())

        self.tm = Task_Mgmt(conn=conn)
        self.c = Calendar()
        self.sections = {
            'calendar': self.c,
            'task_management': self.tm,
            'inbox': None,
            'stats': None
        }
        for s in self.sections.values():
            if s is not None:
                s.get_sects(sects=self.sections)

        #calendar
        self.calendar_area = GridLayout(rows=3, cols=1, size_hint=(3, 2.5))
        print(self.calendar_area)
        self.add_widget(self.calendar_area)
        self.calendar_area.add_widget(Label(text='Calendar', size_hint_y=None, height=30))

        self.calendar_area.add_widget(self.c)
        self.c.week_view(conn)

        self.calendar_tools = GridLayout(rows=1, cols=12, size_hint_y=None, height=40)
        for i in range(1, 13):
            self.calendar_tools.add_widget(Button(text=str(i)))
        self.calendar_area.add_widget(self.calendar_tools)

        # task management
        self.task_area = GridLayout(rows=2, cols=1)
        self.add_widget(self.task_area)
        self.task_area.add_widget(Label(text='Task Management', size_hint_y=None, height=30))
        self.task_area.add_widget(self.tm)

        # place holders (Inbox/Contacts, Statistics)
        self.inbox = GridLayout(cols=1, rows=2)
        self.inbox.add_widget(Label(text='Inbox & Contacts', size_hint_y=None, height=30))
        self.inbox.minute_scroll = ScrollView(do_scroll_x=False)
        self.inbox.minute_grid = GridLayout(cols=1, size_hint=(1, None))
        self.inbox.minute_grid.bind(minimum_height=self.inbox.minute_grid.setter('height'))
        self.inbox.minute_scroll.add_widget(self.inbox.minute_grid)
        for i in range(1, 61):
            minute = Button(text=str(i), size_hint_y=None, height=40)
            # minute.bind(on_press=self.inbox.print_btn)
            self.inbox.minute_grid.add_widget(minute)
        self.add_widget(self.inbox)
        self.inbox.add_widget(self.inbox.minute_scroll)

        self.stat_area = GridLayout(rows=2, cols=1)
        self.stat_area.add_widget(Label(text='Usage Statistics', size_hint_y=None, height=30))
        self.stat_area.add_widget(GridLayout(rows=1))
        self.add_widget(self.stat_area)

        cur.execute("SELECT * FROM tasks")
        for i in cur.fetchall():
            print(i)

        for day in self.sections['calendar'].current_week.days:
            day.add_tasks2(cur=cur, dom=day.dom, sects=self.sections)


class MyApp(App):
    def build(self):
        return Root()

if __name__ == '__main__':
    create_connection("database/data.db")
    MyApp().run()
