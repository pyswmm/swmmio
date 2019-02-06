<<<<<<< HEAD
from definitions import *
=======
from swmmio.defs.config import *
>>>>>>> 20c5e0571a9e48d405822dc963669df8811e6d33
import shutil

#THIS STUFF IS INCOMPLETE/ MAYBE BROKEN
def insert_in_file(key, string, newfile, f=BASEMAP_PATH):

    #make a temp copy
    shutil.copyfile(newfile, )

    #start writing that thing
    key = '{}{}{}'.format('{{', key, '}}') #Django style
    with open(f, 'r') as bm:
        with open(newfile, 'wb') as newmap:
            for line in bm:
                if key in line:
                    newline = line.replace(key, string)
                    newmap.write(newline)
                    # newmap.write(geojson.dumps(FeatureCollection(geometries, crs=crs)))
                else:
                    newmap.write(line)

def insert_in_file_2(key, string, newfile):

    #start writing that thing
    key = '{}{}{}'.format('{{', key, '}}') #Django style
<<<<<<< HEAD
    print key
=======
    print(key)
>>>>>>> 20c5e0571a9e48d405822dc963669df8811e6d33
    with open(newfile, 'r') as newmap:
        for line in newmap:
            if key in line:
                newline = line.replace(key, string)
                newmap.write(newline)
                # newmap.write(geojson.dumps(FeatureCollection(geometries, crs=crs)))
            # else:
            #     newmap.write(line)
