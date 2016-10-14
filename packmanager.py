import os
import math
import re
import datetime as dt
import pyexiv2 as pe
import itempack as ip


def digits(n):
    """Calculate the number of digits of n."""
    if n != 0:
        return int(math.log10(abs(n))) + 1
    else:
        return 1


class CaptionRange:
    def __init__(self, start=0, end=0):
        self.start = start
        self.end = end

    def __repr__(self):
        return "start = {}, end = {}".format(self.start, self.end)


class PackManager:
    """Manage a list of ImagePack objects.

    The PackManager is responsible for ordering its packs and to call their process() functions.
    """

    def __init__(self, rawFolder, jpgFolder='jpg'):
        """Create a PackManager.

        Arguments:
        rawFolder: Folder containing raw and raw xmp files.
        jpgFolder: Folder containing jpg and jpg xmp files. This is relative to rawFolder.
        """

        self._rawExtension = '.CR2'
        self._rawXmpExtension = self._rawExtension + '.xmp'

        self._rawFolder = rawFolder
        self._jpgFolder = jpgFolder

        self._moveablePackList, self._discardablePackList = self._createPackLists()
        self._moveablePackList.sort(key=lambda x: x._sortId())
        self._calcProNumber()

    def _createPackLists(self):
        """Create the list of image packes."""

        # Set of base names of all files in rawFolder
        files = (set([f.split('.')[0] for f in os.listdir(self._rawFolder)
                      if os.path.isfile(os.path.join(self._rawFolder, f))]) |
                 set([f.split('.')[0] for f in os.listdir(os.path.join(self._rawFolder, self._jpgFolder))
                      if os.path.isfile(os.path.join(self._rawFolder, self._jpgFolder, f))]))

        moveablePackList = []
        discardablePackList = []

        # Try to read the raw and the raw xmp file. If the read is successful, append a moveable
        # pack to the pack list, otherwise append a discardable pack.
        for f in files:
            foundCaption = False
            foundTime = False
            try:
                # Read original date from raw file.
                url = os.path.join(self._rawFolder, f+self._rawExtension)
                metadata = pe.ImageMetadata(url)
                metadata.read()
                tag = metadata['Exif.Photo.DateTimeOriginal']
                date = tag.value.strftime('%Y-%m-%dT%H%M%S')

                # Read caption from raw xmp file.
                url = os.path.join(self._rawFolder, f+self._rawXmpExtension)
                metadata = pe.ImageMetadata(url)
                metadata.read()
                tag = metadata['Xmp.acdsee.caption']
                caption = tag.value

                moveablePackList.append(ip.MoveableItemPack(f, caption, date))

            except KeyError:
                if not foundCaption or foundTime:
                    print("Skip pack due to lack of information {}".format(f+self._rawXmpExtension))

            except IOError:
                discardablePackList.append(ip.DiscardableItemPack(f))

        return moveablePackList, discardablePackList

    def _calcProNumber(self):
        captionBorders = []
        captionBorders.append(CaptionRange(start=0))

        # Split packs by date and caption
        packCaption = self._moveablePackList[0].caption
        for packIdx, pack in enumerate(self._moveablePackList[1:]):
            if pack.caption != packCaption:
                captionBorders[-1].end = packIdx + 1
                captionBorders.append(CaptionRange(start=packIdx + 1))
                packCaption = pack.caption
        captionBorders[-1].end = len(self._moveablePackList)

        # Iterate captionBorder and assign pro numbers to packs
        for border in captionBorders:
            d = digits(border.end - border.start)
            proList = [x+1 for x in range(border.end - border.start)]
            for pack, pro in zip(self._moveablePackList[border.start:border.end], proList):
                pack.setProNumber(str(pro).zfill(d))

    def process(self, dry=False):
        if not dry:
            # Create target folders
            os.makedirs(os.path.join(self._rawFolder, 'ready'), exist_ok=True)
            os.makedirs(os.path.join(self._rawFolder, 'delete'), exist_ok=True)

        for pack in (self._moveablePackList +
                     self._discardablePackList):
            pack.setTargetName()
            pack.process(self._rawFolder, self._jpgFolder, dry=dry)



