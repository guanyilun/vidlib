from manimlib import *
from vidlib.colors import *

C = colorscheme['default']

# class Slide(VGroup):
class Slide(Group):
    CONFIG = {
        'style': {
            'h1': {
                'fs': 48,
                # 'color': C['blue-light-1'],
                'color': C['green-light-2'],
            },
            'h2': {
                'fs': 36,
                'color': C['gray-light-3'],
                # 'color': WHITE
            },
            'h3': {
                'fs': 24,
                'color': C['gray-light-3'],
                # 'color': WHITE,
            },
            'bg': {
                # 'color': C['blue-dark'],
                'color': BLACK # C['blue-dark'],
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

    def title(self, text, underline=False, underline_buff=MED_SMALL_BUFF,
              underline_width=FRAME_WIDTH-2, loc=UL, title_buff=0.5):
        """create a title with an optional underline

        Parameters
        ----------
        text : str
            the title text
        underline : bool, optional
            whether to add an underline, by default False
        buff : float, optional
            the buffer between the title and the underline, by default MED_SMALL_BUFF
        underline_width : float, optional
            the width of the underline, by default FRAME_WIDTH-2

        Returns
        -------
        VGroup
            the title (and underline, if requested)

        """
        title = self.h1(text)
        if underline:
            ul = Line(LEFT, RIGHT, color=self.style['h1']['color'])
            ul.next_to(title, DOWN, buff=underline_buff)
            ul.set_width(underline_width)
            title.add(ul)

        # note that I cannot just do to_edge because that will assume that
        # slides are vertically stacked, which may not be the case. A more
        # general solution would be to reference the slide object itself.
        # 1. get corner of the slide
        title.move_to(self.get_corner(loc) - title_buff*loc, aligned_edge=loc)
        return title

    def bulleted_list(self, *texts, buff=MED_SMALL_BUFF, bullet="⚫"):
        blist = VGroup()
        for t in texts:
            blist.add(self.h3(bullet + " " + t))
        blist.arrange(DOWN, aligned_edge=LEFT, buff=buff)
        return blist


class SlideShow(Scene):
    CONFIG = {
        'transition_time': 0,
        'transition': 'move_to',
    }
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.slides = []
        self.sid = 0

    def add_slide(self, slide=None, side=DOWN, add_to_scene=True, pagenum=True, skipfirst=True):
        # if not slide: slide = Slide()
        if len(self.slides) > 0:
            if side is not None:
                # assuming a stacked layout
                slide.next_to(self.slides[-1], side)
        if add_to_scene: self.add(slide)
        if pagenum:
            if skipfirst and len(self.slides) == 0:
                pass
            else:
                pagenum = slide.h3(f"{len(self.slides)}").scale(0.5)
                pagenum.move_to(slide.get_bottom()+0.5*UP)
                slide.add(pagenum)
        self.slides.append(slide)
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
            # note that this assumes the slide is all at the same location
            animations = [FadeOut(self.slides[self.sid]),FadeIn(self.slides[sid])]
        self.play(*animations, run_time=run_time)

    def goto_slide(self, slide, run_time=None):
        if self.transition == 'move_to':
            animations = [self.camera.frame.animate.move_to(
                slide.get_center()
            )]
            self.play(*animations, run_time=run_time)
            try:
                self.sid = self.slides.index(slide)
            except Exception: pass
        else:
            raise NotImplementedError

    def on_key_press(self, symbol, modifiers):
        super().on_key_press(symbol, modifiers)
        # if symbol in [65363,65364,65366]:  # right, down, pagedown
        if symbol in [65364,65366]:  # down, pagedown
            if self.sid < len(self.slides) - 1:
                self.goto(self.sid+1)
                self.sid += 1

        # if symbol in [65361,65362,65365]:  # left, up, pageup
        if symbol in [65362,65365]:  # up, pageup
            if self.sid > 0:
                self.goto(self.sid-1)
                self.sid -= 1
        
        if symbol == 65363:
            next(self.cursor)

        
                class MultiLevelText(Group):
    def __init__(self, text, level_indicator="\t", indent=0.5, markers="dot", line_spacing=0.2, font_size=24, **kwargs):
        super().__init__()
        # first split text into lines
        lines = text.split("\n")
        # then find the level of each line based on level indicator: note that
        # the algorithm assumes that level_indicator is at the beginning of the line
        # and it is only one character.
        levels = [len(line) - len(line.lstrip(level_indicator)) for line in lines]
        # then remove the level indicator from the lines
        lines = [line.lstrip(level_indicator) for line in lines]
        # add appropriate level markers in each line
        # check whether level markers is a list or a string
        if isinstance(markers, str):
            if   markers == "dot":    marker = "⚫"
            elif markers == "square": marker = "▪"
            elif markers == "dash":   marker = "⚬"
            elif markers == '-':      marker = '-'
            else: raise ValueError("Invalid marker type")
            # add the marker to each line
            lines = [marker + " " + line for line in lines]
        elif isinstance(markers, list):
            if len(markers) != max(levels)+1:
                raise ValueError("Number of markers must match the maximum level")
            lines = [markers[level] + " " + line for level, line in zip(levels, lines)]
        else:
            raise ValueError("Invalid marker type")
        # now create the text objects
        texts = [Text(line, font_size=24, **kwargs) for line in lines]
        self.add(*texts)
        # arrange the text objects
        self.arrange(DOWN, aligned_edge=LEFT, buff=line_spacing)
        # now create the indentations
        indents = [indent*level for level in levels]
        # now create the group
        for text, indent in zip(texts, indents):
            text.shift(indent*RIGHT)
