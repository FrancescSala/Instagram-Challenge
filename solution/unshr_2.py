import sys, collections
from PIL import Image
import numpy as np

# measures how well shreds i and j would fit one next to the other in a reconstructed image
# (shred i on the left and shred j on the right) 
def computeDistance(i,j):
    if i == j: return sys.maxint
    # c1 and c2 are the borders in contact of the two shreds
    c1, c2 = (i + 1) * shredWidth - 1, j * shredWidth
    # the distance is the cumulated difference of the pixels along this sewing
    return sum(abs(pixels[c1]-pixels[c2]))

# estimates the width of the shreds, when it is not given as an input argument
def calculateShredWidth():
    borders, borders2 = [], []
    for i in xrange(1,imageWidth-2): borders += [[i,computeDistance(i,i+1)]]
    borders.sort(key=lambda x: x[1], reverse=True)
    for item in borders: borders2 += [item[0]]
    min = [sys.maxint,sys.maxint, False]
    for i in xrange(3,imageWidth/6+1):
        if imageWidth%i == 0:
            d = 0
            for j in xrange(1,imageWidth/i): d += borders2.index(j*i -1) + 1
            e = d / float((imageWidth/i)*(imageWidth/i + 1)/2)
            d = d/float(imageWidth/i -1)
            if (e * d < min[1]): min =[i, e * d]
    return min[0]

# side is either LEFT or RIGTH
# This function determines which shred fits better next to sherd i, (at its left or at its right, according to parameter)
def bestCandidate(i,side):
    distances = [computeDistance(j,i) if side == LEFT else computeDistance(i,j) for j in range(numShreds)]
    return distances.index(min(distances))

# starting from the leftmost shred, adds the best shreds for the right, until reconstructing the whole image
def reconstructImageFromLeft(sequence):
    if bestNeighboursRight[sequence[-1]] in sequence: return sequence
    else: return reconstructImageFromLeft(sequence + [bestNeighboursRight[sequence[-1]]])

# starting from an arbitrary shred, adds the best candidate, either for the left or for the right.
# This function is used only when it has not been possible to determine which was the leftmost shred in the original (unshredded) image.
def reconstructImage(sequence):
    if len(sequence) == numShreds: return sequence
    i, j = bestNeighboursRight.index(sequence[0]), bestNeighboursRight[sequence[-1]]
    l, r = computeDistance(i, sequence[0]), computeDistance(sequence[-1], j)
    if l <= r : return reconstructImage([i] + sequence)
    else: return reconstructImage(sequence + [j])

# Start of the main algorithm
# Check passed arguments
if len(sys.argv) != 2 and len(sys.argv) != 3: sys.exit("Usage: python unshr.py image_filename   or    python unshr.py image_filename  shred_width")

# Load the shredded image and prepare one of the same size to host the reconstructed image 
img = Image.open(sys.argv[1])
print 'dimension of shredded image: ', img.width, ' x ', img.height, ' x ', len(img.getbands())
newImg = Image.new(img.mode,img.size)

# Some initialisations
[imageWidth, imageHeight], shredWidth, LEFT, RIGHT = img.size, 1, 0, 1
pixels = np.asarray(img.getdata().convert('L').transpose(Image.TRANSPOSE)).reshape(img.width,img.height)

# Get the width of the shreds, from input argument or estimate from the shredded image
shredWidth = int(sys.argv[2]) if len(sys.argv) == 3 else calculateShredWidth()
if len(sys.argv) != 3: print "shred width estimated as ", shredWidth

# Number of shreds
numShreds = imageWidth / shredWidth

# Calculate for every shred which other matches better at its right
# For the rightmost shred in the original (unshredded) image, this always gives an incorrect value.
# I try to exploit if this incorrect value causes a repetition in estNeighboursRight. That would:
# indicate which is the leftmost shred (and a hint of which is the rightmost)
bestNeighboursRight = [bestCandidate(i,RIGHT) for i in range(numShreds)]
[(x, y)] = collections.Counter(bestNeighboursRight).most_common(1)
if y == 2:
    # calculate the leftmost shred in the reconstructed image: it is the value missing in bestNeighboursRight
    leftmostShred = (numShreds * (numShreds -1)) / 2 - sum(bestNeighboursRight) + x
    sortedShreds = reconstructImageFromLeft([leftmostShred])
else:
    # still insist in finding the leftmost shred of the original (unshredded) image,
    # but trying not to do a lot of calculations
    found, i = False, 0
    while i < numShreds and not found:
        found = (bestCandidate(bestNeighboursRight[i],LEFT) != i)
        i = i + 1
    if found:
        leftmostShred = bestNeighboursRight[i-1]
        sortedShreds = reconstructImageFromLeft([leftmostShred])
    else:
        sortedShreds = reconstructImage([0])

#arrived at this point I have a sorted list of shreds, which is my reconstruction of the image
#reconstruct the image in newImg
for i in range(len(sortedShreds)): newImg.paste(img.crop((shredWidth*sortedShreds[i],0,shredWidth*(sortedShreds[i]+1),imageHeight)), (shredWidth * i, 0))

# show a thumbnail of the shredded image
size = 300, 300
img.thumbnail(size)
img.show()

# save the reconstructed image to a file and show a thumbnail of it too
newImg.save('output.png')
print "reconstructed image saved as 'output.png'"
newImg.thumbnail(size)
newImg.show()
