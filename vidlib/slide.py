from manimlib import *
from vidlib.colors import *

C = colorscheme['default']

class Slide(VGroup):
    CONFIG = {
        'style': {
            'h1': {
                'fs': 48,
                'color': C['blue-light'],
                # 'color': C['blue-light-1'],
            },
            'h2': {
                'fs': 36,
                # 'color': C['gray-light-3'],
                'color': C['gray-light-3'],
            },
            'h3': {
                'fs': 24,
                'color': C['gray-light-3'],
            },
            'bg': {
                'color': C['blue-dark'],
            }
        }
    }
    def __init__(self):
        super().__init__()
        self.last_mob = None
        self.add(
            FullScreenRectangle(fill_color=self.style['bg']['color'])
        )

    def h1(self, text):
        return Text(text, font_size=self.style['h1']['fs'],
                    color=self.style['h1']['color'])

    def h2(self, text):
        return Text(text, font_size=self.style['h2']['fs'],
                    color=self.style['h2']['color'])

    def h3(self, text):
        return Text(text, font_size=self.style['h3']['fs'],
                    color=self.style['h3']['color'])

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
            ul = Line(LEFT, RIGHT, color=self.style['h2']['color'])
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
    CONFIG = {
        'transition_time': 0,
        'transition': 'move_to',
    }
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.slides = []
        self.sid = 0

    def add_slide(self, slide=None, side=DOWN):
        if not slide: slide = Slide()
        if len(self.slides) > 0:
            if side is not None:
                slide.next_to(self.slides[-1], side)
        self.slides.append(slide)
        self.add(slide)
        return slide

    def goto(self, sid, run_time=None):
        if not run_time: run_time = self.transition_time
        if sid >= len(self.slides): pass
        animations = []
        if self.transition == 'move_to':
            animations = [self.camera.frame.animate.move_to(
                self.slides[sid].get_center()
            )]
        elif self.transition == 'crossfade':
            animations = [FadeOut(self.slides[self.sid]),FadeIn(self.slides[sid])]
        self.play(*animations, run_time=run_time)

    def on_key_press(self, symbol, modifiers):
        super().on_key_press(symbol, modifiers)
        if symbol in [65363,65364,65366]:  # right, down, pagedown
            if self.sid < len(self.slides) - 1:
                self.goto(self.sid+1)
                self.sid += 1

        if symbol in [65361,65362,65365]:  # left, up, pageup
            if self.sid > 0:
                self.goto(self.sid-1)
                self.sid -= 1
                

    def show_animations(self):
        pass
