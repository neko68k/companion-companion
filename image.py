#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PIL import Image

def load(filename):
    img = Image.open(filename)

    width = img.width
    height = img.height
    
    if(height>4096):
        img.thumbnail((3686, 4096), resample=Image.Resampling.NEAREST)
        width = 3686
        height = 4096

    img_data = img.convert("RGBA").transpose(Image.FLIP_TOP_BOTTOM).tobytes()
    

    

    return(img_data, width, height)