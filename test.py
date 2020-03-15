from blinkstick import blinkstick
from time import sleep
colorMap = [{"red":0, "green":40,"blue":0},{"red":0, "green":60,"blue":0},{"red":0, "green":0,"blue":0},{"red":0, "green":0,"blue":0}]

for bstick in blinkstick.find_all():
    bstick.error_reporting = True
    print ("Found device:")
    print ("    Manufacturer:  " + bstick.get_manufacturer())
    print ("    Description:   " + bstick.get_description())
    print ("    Serial:        " + bstick.get_serial())
    print ("    Current Color: " + bstick.get_color(color_format="hex"))
    print ("    Info Block 1:  " + bstick.get_info_block1())
    print ("    Info Block 2:  " + bstick.get_info_block2())
    print ("    Mode: {}".format(bstick.get_mode()))
    #print ("    LED Count: {}".format(bstick.get_led_count()))
    print ("    Button: {}".format(bstick.get_button()))
    bstick.set_mode = 2
    bstick.set_led_count(4)
    #for a in range(0,4):
    #    bstick.set_color(channel=0, index=a, red=0, green=0, blue=255)    
    #bstick.set_color(channel=0, index=0, red=0, green=colorMap[0]["green"], blue=colorMap[0]["blue"])
    
    while True:
        for a in range(0,4):
            for b in range(0,4):
                offset = b-a-1
                if offset <0:
                    offset = 4 + offset
                bstick.set_color(channel=0, index=b, red=0, green=colorMap[offset]["green"], blue=colorMap[offset]["blue"])
            sleep(0.25)

    
   