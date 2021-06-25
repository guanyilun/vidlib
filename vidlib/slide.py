from manimlib import *


class Slide(VGroup):
    CONFIG = {
        'text_config': {
            'color': BLACK
        },
        'fs_h1': 48,
        'fs_h2': 36,
        'fs_h3': 24,
        'fill_color': "#eeeeee",
    }
    def __init__(self):
        super().__init__()
        self.last_mob = None
        self.add(FullScreenRectangle(fill_color=self.fill_color))

    def h1(self, text):
        return Text(text, font_size=self.fs_h1, **self.text_config)

    def h2(self, text):
        return Text(text, font_size=self.fs_h2, **self.text_config)

    def h3(self, text):
        return Text(text, font_size=self.fs_h3, **self.text_config)

    def add_v(self, mob, relative=DOWN):
        if self.last_mob is None:
            self.add(mob)
        else:
            mob.next_to(self.last_mob, relative)
            self.add(mob)
        self.last_mob = mob

    def title(self, text, underline=True, buff=MED_SMALL_BUFF,
              underline_width=FRAME_WIDTH-2):
        title = self.h1(text)
        title.to_edge(UP)
        if underline:
            ul = Line(LEFT, RIGHT, **self.text_config)
            ul.next_to(title, DOWN, buff=buff)
            ul.set_width(underline_width)
            title.add(ul)
        self.title = title
        return title

    def bulleted_list(self, *texts, buff=MED_LARGE_BUFF, bullet="⚫"):
        blist = VGroup()
        for t in texts:
            blist.add(self.h2(bullet + " " + t))
        blist.arrange(DOWN, aligned_edge=2*LEFT, buff=buff)
        blist.next_to(self.title, 2*DOWN, buff=buff)
        return blist.to_edge(LEFT, buff=1)


class SlideShow(Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.slides = []
        self.sid = 0

    def add_slide(self, slide=None):
        if not slide: slide = Slide()
        if len(self.slides) > 0:
            slide.next_to(self.slides[-1], DOWN)
        self.slides.append(slide)
        self.add(slide)
        return slide

    def goto(self, sid):
        if sid >= len(self.slides): pass
        self.play(
            self.camera.frame.animate.move_to(
                self.slides[sid].get_center()
            ), run_time=0.5)

    def on_key_press(self, symbol, modifiers):
        super().on_key_press(symbol, modifiers)
        if symbol in [65363,65364,65366]:  # right, down
            if self.sid < len(self.slides) - 1:
                self.sid += 1
                self.goto(self.sid)
                print(self.sid)
        if symbol in [65361,65362,65365]:  # left, up
            if self.sid > 0:
                self.sid -= 1
                self.goto(self.sid)
                print(self.sid)
