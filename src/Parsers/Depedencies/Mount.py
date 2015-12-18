import os
import tarfile
import stat
import pytsk3
import zipfile

# extracts zip file to given location
def extractZip(zipPath, extractFolder):
    try:
        zipLoc = zipfile.ZipFile(zipPath)
        zipLoc.extractall(extractFolder)
        return True
    except:
        pass

    return False

# Extracts the contents of a tar to a given folder
# Inputs: tarPath, extractFolder
def extractTar(tarPath, extractFolder):
    tar = tarfile.open(tarPath)

    for member in tar:
        member.mode = stat.S_IWRITE # allows us to read and write this data within Python, which we need for SQLite
        try:
            tar.extract(member, extractFolder)
        except IOError as e:
            pass
    tar.close()
    return True

# Extracts the contents of an image file to a given folder
# Inputs: imagePath, extractFolder
def extractImageFile(imagePath, extractFolder):
    img = pytsk3.Img_Info(imagePath)

    try:
        vols = pytsk3.Volume_Info(img) # if we can't find the volumes it isn't an image we can do anything with or an image at all
    except:
        img.close()
        return False

    for vol in list(vols):
        folderPath = os.path.join(extractFolder, vol.desc)
        if not os.path.isdir(folderPath):
            os.makedirs(folderPath)
        try:
            fs = pytsk3.FS_Info(img, vol.start * 512)
        except:
            continue

        extractDir(fs, '', extractFolder)

    img.close()
    return True

# Extracts the contents of a file opened using The Sleuth Kit to a given folder
# Inputs: imagePath, extractFolder
def extractDir(fs, readRoot, extractRoot):
    try:
        d = fs.open_dir(readRoot)
    except:
        return

    for f in d:
        if f.info.name.name == '.' or f.info.name.name == '..':
            continue
        newRead = readRoot + '/' + f.info.name.name
        newExtract = os.path.join(extractRoot, f.info.name.name)
        if f.info.name.type == pytsk3.TSK_FS_NAME_TYPE_DIR:
            if not os.path.isdir(newExtract):
                os.makedirs(newExtract)
            extractDir(fs, newRead, newExtract)
        elif f.info.name.type == pytsk3.TSK_FS_NAME_TYPE_REG:
            try:
                readFile = fs.open_meta(inode = f.info.name.meta_addr)
                offset = 0
                remaining = readFile.info.meta.size
                CHUNK = 10485760 # 10MB
                data = b''
                while remaining > 0:
                    readChunk = CHUNK
                    if readChunk > remaining:
                        readChunk = remaining
                    remaining -= readChunk
                    data += readFile.read_random(offset, readChunk)
                    offset += readChunk
                if len(data) > 0:
                    output = open(newExtract, 'wb')
                    output.write(data)
                    output.close()
            except:
                pass

def tryAllInputs(inputPath, extractedRoot):
    newInput = False
    if zipfile.is_zipfile(inputPath):
        newInput = extractZip(inputPath, extractedRoot)
    elif tarfile.is_tarfile(inputPath):
        newInput = extractTar(inputPath, extractedRoot)
    elif os.path.getsize(inputPath) > 1073741824:
        newInput = extractImageFile(inputPath, extractedRoot)
    else:
        newInput = inputPath

    return newInput
