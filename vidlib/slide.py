from manimlib import *
from vidlib.colors import *

C = colorscheme['default']


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
                'color': BLACK
            }
        }
    }
    def __init__(self):
        super().__init__()
        self.last_mob = None
        self.bg = FullScreenRectangle(fill_color=self.style['bg']['color'])
        self.add(self.bg)
        self.stages = []
        self._refs = {}
        # whether to auto advance to the next slide when animations are done
        self.auto_advance = False

    def add_stage(self, *stages, **kwargs):
        """Add a presentation stage. Input could be anything that
        gets passed to self.play() or a callable function which takes
        a slide as argument. kwargs can contain a keyword 'wait' which
        will determine whether user input is before executing the stage.

        """
        self.stages.append((stages, kwargs))

    def add_ref(self, key, mob):
        self._refs[key] = mob

    def get_ref(self, key):
        if key in self._refs:
            return self._refs[key]
        return None

    def h1(self, text):
        return Text(text, font_size=self.style['h1']['fs'],
                    color=self.style['h1']['color'])

    def h2(self, text):
        return Text(text, font_size=self.style['h2']['fs'],
                    color=self.style['h2']['color'])

    def h3(self, text):
        return Text(text, font_size=self.style['h3']['fs'],
                    color=self.style['h3']['color'])

    def add_rel(self, mob, side=DOWN):
        """alias for add_v, with a slighly better to understand name"""
        self.add_v(mob, relative=side)

    def add_v(self, mob, relative=DOWN):
        """add an object relative to the last added project"""
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
    def __init__(self, dev=True, **kwargs):
        if dev:
            print("Entering dev mode")
            InteractiveScene.__init__(self, **kwargs)
        else:
            print("Entering production mode")
            Scene.__init__(self, **kwargs)
        self.slides = []
        self.sid = 0
        self.cursor = None
        self.transition_time = 0
        self.dev = dev
        self.refs = {}

    def setup(self):
        if self.dev: InteractiveScene.setup(self)
        self.cursor = self.present()

    def present(self):
        pass

    def add_slide(self, slide=None, side=DOWN, add_to_scene=True, pagenum=True, skipfirst=True, focus=True):
        if slide is None: slide = Slide()
        if len(self.slides) > 0:
            if side is not None:
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
        if focus: self.goto_slide(slide)
        return slide

    def goto_sid(self, sid, run_time=None, refresh=True):
        if not run_time: run_time = self.transition_time
        if sid >= len(self.slides): pass
        animations = [self.camera.frame.animate.move_to(self.slides[sid].get_center())]
        self.play(*animations, run_time=run_time)
        self.sid = sid
        print("goto:", self.sid)
        self.post_stage_handler()

    def goto_slide(self, slide, run_time=0):
        try:
            self.sid = self.slides.index(slide)
            self.goto_sid(self.sid, run_time=run_time)
        except Exception as e:
            print(e)

    def on_key_press(self, symbol, modifiers):
        super().on_key_press(symbol, modifiers)
        # if symbol in [65363,65364,65366]:  # right, down, pagedown
        if symbol in [65364,65366]:  # down, pagedown
            if self.sid < len(self.slides) - 1:
                self.goto_sid(self.sid+1)

        # if symbol in [65361,65362,65365]:  # left, up, pageup
        if symbol in [65362,65365]:  # up, pageup
            if self.sid > 0:
                self.goto_sid(self.sid-1)

    def next(self):
        """Advance animation"""
        if self.cursor == None: return
        try:
            next(self.cursor)
        except Exception as e:
            print(e)
            pass

    def post_stage_handler(self):
        """copied from scene.post_cell_func"""
        self.refresh_static_mobjects()
        if not self.is_window_closing():
            self.update_frame(dt=0, ignore_skipping=True)
        self.save_state()

    def present(self):
        for sid in range(len(self.slides)):
            slide = self.slides[sid]
            self.goto_slide(slide)
            # if there is animations defined, play them
            if len(slide.stages)>0:
                print(f"sid {sid}: {len(slide.stages)} stages found")
                for stage in slide.stages:
                    driver, kwargs = stage
                    # wait for interaction unless otherwise told
                    if kwargs.get('wait', True): yield
                    if callable(driver[0]):
                        stage[0][0](slide)
                    else:  # otherwise assume it is a list of animations
                        ani, kwargs = stage
                        self.play(*ani, **kwargs)
                    self.post_stage_handler()
            if not slide.auto_advance: yield  # wait for interaction before going to the next slide

    def on_mouse_press(self, point, button, modifiers):
        # don't use SPACE to advance, it causes weird bug in manim
        super().on_mouse_press(point, button, modifiers)
        if not self.dev: self.next()

    def autoplay(self, wait=3):
        self.wait(wait)
        for _ in self.present():
            self.wait(wait)
        self.wait(wait)

    def to_pdf(self, oname="slide.pdf", wait=3):
        """Render to pdf. This needs to run with non-preview mode,
        such as through manimgl slide.py -w"""
        self.update_frame()
        im1 = self.camera.get_image()
        im1 = im1.convert("RGB")
        images = []
        self.wait(wait)
        for _ in self.present():
            self.update_frame()
            img = self.camera.get_image()
            img = img.convert("RGB")
            images.append(img)
            self.wait(wait)
        self.update_frame()
        img = self.camera.get_image()
        img = img.convert("RGB")
        images.append(img)
        self.wait(wait)
        im1.save(oname, save_all=True, append_images=images)


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
