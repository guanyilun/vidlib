from manimlib import *


class MyImageMobject(ImageMobject):
    def __init__(self, filename, extent=None, **kwargs):
        """More flexible version of ImageMobject.
        
        Parameter
        ---------
        filename : str
            Path to image file.
        extent : tuple of float
            actual bounds of the image, i.e., (x_min, x_max, y_min, y_max)
        """
        super().__init__(filename, **kwargs)
        # if extent is None: self.extent = self.data['im_coords']
        self.extent = extent

    def crop(self, box, update_points=True):
        """Crop image to box.
        
        Parameter
        ---------
        box : tuple of float
            (x_min, x_max, y_min, y_max)
        """
        # self.extent = box
        self.data['im_coords'] = np.array([
            (box[0], box[2]),
            (box[0], box[3]),
            (box[1], box[2]),
            (box[1], box[3]),
        ])
        # update points
        if update_points:
            self.set_width((box[1] - box[0])*self.get_width(), stretch=True)
            self.set_height((box[3] - box[2])*self.get_height(), stretch=True)
            # update extent
            x_min, x_max, y_min, y_max = box
            (x_min, y_min) = self.im2sky((x_min, y_min))
            (x_max, y_max) = self.im2sky((x_max, y_max))
            self.extent = (x_min, x_max, y_min, y_max)

    def crop_sky(self, skybox, update_points=True):
        """crop image to skybox.
        
        Parameter
        ---------
        skybox : tuple of float
            (x_min, x_max, y_min, y_max)
        """
        (x_min, x_max, y_min, y_max) = skybox
        (x_min, y_min) = self.sky2im((x_min, y_min))
        (x_max, y_max) = self.sky2im((x_max, y_max))
        self.crop([x_min, x_max, y_min, y_max], update_points=update_points)

    def scroll_by(self, displacement):
        """scroll image by a displacement without changing its size.
        
        Parameter
        ---------
        displacement : tuple of float
            (x, y)
        """
        self.data['im_coords'] += np.array(displacement)

    def scroll_to_v(self, target):
        """scroll image to vertically to the target location
        
        Parameter
        ---------
        target : float
            target alpha (0 to 1)
        """
        self.scroll_by([target - self.data['im_coords'][0, 0], 0])

    def scroll_to_sky(self, skypos, width=2, height=None):
        """scroll image to a sky position, default to place the position in the center.
        
        Parameter
        ---------
        skypos : tuple of float in degrees
            (x, y)
        width : float
            width of the box in degrees
        height : float
            height of the box in degrees 
        """
        if height is None: height = width
        im_coords = np.array([
           self.sky2im([skypos[0] - width/2, skypos[1] - height/2]),
           self.sky2im([skypos[0] - width/2, skypos[1] + height/2]),
           self.sky2im([skypos[0] + width/2, skypos[1] - height/2]),
           self.sky2im([skypos[0] + width/2, skypos[1] + height/2]),
        ])
        self.data['im_coords'] = im_coords

    def scroll_sky(self, pos):
        """scroll image without changing its size.
        
        Parameter
        ---------
        pos : tuple of float
            (x, y)
        """
        (x, y) = self.sky2im(pos)
        self.scroll_by((x, y))

    def im2sky(self, coord):
        """convert an image coordinate to physical coordinate. Image coordinate goes from 0 to 1,
        while sky coordinate can be degrees, for example.
        
        Parameter
        ---------
        coord : tuple of float (x, y)
        
        Return
        ------
        tuple of float

        """
        if self.extent is None: return coord
        else:
            return (
                self.extent[0] + coord[0]*(self.extent[1] - self.extent[0]),
                self.extent[2] + coord[1]*(self.extent[3] - self.extent[2]),
            )

    def sky2im(self, coord):
        """convert a physical coordinate to image coordinate.
        
        Parameter
        ---------
        coord : tuple of float (x, y)
        
        Return
        ------
        tuple of float

        """
        if self.extent is None: return coord
        else:
            return (
                (coord[0] - self.extent[0])/(self.extent[1] - self.extent[0]),
                (coord[1] - self.extent[2])/(self.extent[3] - self.extent[2]),
            )
        
    def im2p(self, coord):
        """convert an image coordinate to point"""
        # self.pointsself.get_width()*coord[0]
        bbox = self.get_bounding_box()
        # based on the BL corner, 2D
        return bbox[0] + np.array([self.get_width()*coord[0], self.get_height()*coord[1], 0])

    def sky2p(self, coord):
        """convert a physical coordinate to point"""
        return self.im2p(self.sky2im(coord))

    def p2im(self, point):
        """convert a point to image coordinate"""
        bbox = self.get_bounding_box()
        # based on the BL corner, 2D
        pt = point[:2]
        return np.abs(pt - bbox[0][:2])/np.array([self.get_width(), self.get_height()])

    def p2sky(self, point):
        """convert a point to physical coordinate"""
        return self.im2sky(self.p2im(point))

    def get_width_sky(self):
        """get width in sky coordinate"""
        return np.abs(self.extent[1] - self.extent[0])

    def get_height_sky(self):
        """get height in sky coordinate"""
        return np.abs(self.extent[3] - self.extent[2])

    def scale_to_match_extent(self, other, move=False):
        """scale image such that length in it is compatible with the another image. This
        is done by comparing extent.

        Parameter
        ---------
        other : Image
            another image
        move : bool
            if True, move the image to the matching location of the other image

        """
        if self.extent is None or other.extent is None: return
        my_pix_per_deg = self.get_width() / self.get_width_sky()
        other_pix_per_deg = other.get_width() / other.get_width_sky()
        ratio = other_pix_per_deg / my_pix_per_deg
        self.scale(ratio, about_point=self.get_center())  # note that this assumes aspect ratio is maintained
        if move: self.move_to(other.sky2p(self.p2sky(self.get_center())))

