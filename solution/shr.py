from PIL import Image
from random import shuffle
import sys

if len(sys.argv) != 4: sys.exit("Usage: python shr.py input_image num_shreds output_image")

# load the input image
img = Image.open(sys.argv[1])

# read the desired number of shreds
numShreds = int(sys.argv[2])
if numShreds < 2: sys.exit("Expected number of shreds to be at least 2")
if img.width % numShreds != 0: 
   print "The number of shreds must be a submultiple of the width of the image: ", img.width
   sys.exit()

# prepare the shred of the image
sequence = range(0, numShreds)
shuffle(sequence)
# check the sequence in order to make sure that there are not contiguous shreds in the sequence
# if there are, just swap them
# in other words, make sure all the shreds in the shredded image will be exactly the same width
for i in range(len(sequence)-1):
    # if contiguous shreds, swap them
    if sequence[i] == sequence[i+1] - 1:
        sequence[i] = sequence[i] + 1
        sequence[i+1] = sequence[i+1] - 1

# calculate the width of the shreds
shredWidth = img.width / numShreds

# create the shredded image
shredded = Image.new(img.mode, img.size)
for i, shred_index in enumerate(sequence):
    shred_x1, shred_y1 = shredWidth * shred_index, 0
    shred_x2, shred_y2 = shred_x1 + shredWidth, img.height
    shredded.paste(img.crop((shred_x1, shred_y1, shred_x2, shred_y2)), (shredWidth * i, 0))

# finally, save the shredded image
shredded.save(sys.argv[3])
print "Shredded image saved as: ", sys.argv[3]



