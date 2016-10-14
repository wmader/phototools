import glob
import os


class ItemPack:
    """Base class packing together all files belonging to one image.

    The pack can include any combination of a raw file, a jpg file, and respective xmp files.
    """

    def __init__(self, baseName):
        """Create an item pack.

        Arguments:
        baseName: The current common part of all filenames belonging to the pack. This name is
        usually provided by the camera.
        """
        self._baseName = baseName

    def __repr__(self):
        return self._targetName

    def _sortId(self):
        """Return the key by which this pack is sorted.

        All derived classes must implement this function.
        """
        pass

    def setProNumber(self, number):
        """Set the running number of this pack in the list of all packs.

        As images come from the same shooting session, their respective packs belong together. Their
        order is determined by the PackManager which also provides the pro number. This number is
        the running number included in the target file name.
        """
        self._proNumber = number

    def process(self, rawFolder, jpgFolder, dry=False):
        """Move files to target folder."""
        fileList = (glob.glob(os.path.join(rawFolder, self._baseName + '*')) +
                    glob.glob(os.path.join(rawFolder, jpgFolder, self._baseName + '*')))

        if not dry:
            for f in fileList:
                ext = '.'+f.split('.', 1)[1]
                targetFile = os.path.join(rawFolder, self._targetFolder, self._targetName+ext)
                if not os.path.isfile(targetFile):
                    os.replace(f, targetFile)
                else:
                    msg = 'File already exists\n' + targetFile + '\skipping this file'
                    print(msg)
        else:
            for f in fileList:
                ext = '.'+f.split('.', 1)[1]
                sourceFile = os.path.basename(f).ljust(18)
                targetFile = os.path.join(self._targetFolder, self._targetName+ext)
                print(sourceFile + ' -> ' + targetFile)


class MoveableItemPack(ItemPack):
    """
    In ItemPack with enough information to be moveable.

    Basically, this means, that an xmp file is found from which the target name is read. Only the
    xmp file of the raw file is considered, as a situation in which only the jpg file has an xmp
    is suspicious.
    """

    def __init__(self, baseName, caption, time):
        self.caption = caption
        self.time = time
        self._targetFolder = 'ready'
        super().__init__(baseName)

    def _sortId(self):
        return self.time + self.caption

    def setTargetName(self):
        self._targetName = self.time + " - " + self._proNumber + ' - ' + self.caption


class DiscardableItemPack(ItemPack):
    def __init__(self, baseName):
        self._targetFolder = 'delete'
        super().__init__(baseName)

    def _sortId(self):
        return 'zzz' + self._baseName

    def setTargetName(self):
        self._targetName = self._baseName
