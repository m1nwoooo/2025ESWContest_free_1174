import sensor, time, struct
from pyb import USB_VCP, LED

usb = USB_VCP()
led_blue = LED(3)
led_red = LED(1)

MIN_TEMP = 20.0
MAX_TEMP = 60.0

def setup_agc():
    sensor.ioctl(sensor.IOCTL_LEPTON_SET_MODE, False)

def setup_radiometry():
    sensor.ioctl(sensor.IOCTL_LEPTON_SET_MODE, True)
    sensor.ioctl(sensor.IOCTL_LEPTON_SET_RANGE, MIN_TEMP, MAX_TEMP)

def get_temperature():
    roi_x, roi_y, roi_size = 69, 49, 21
    img = sensor.snapshot()
    stats = img.get_statistics(roi=(roi_x, roi_y, roi_size, roi_size))
    pixel_avg = stats.mean()
    temp_range = MAX_TEMP - MIN_TEMP
    temperature = ((pixel_avg * temp_range) / 255.0) + MIN_TEMP
    
    if 0.0 <= temperature <= 150.0 and pixel_avg > 0:
        return temperature
    else:
        return -999.0, 0 #에러 발생시

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=3000)

setup_agc()
temp_mode = False

while True:
    try:
        cmd = usb.recv(4, timeout=100)
        if cmd:
            led_blue.on()
            
            if cmd == b"snap":
                if not temp_mode:
                    img = sensor.snapshot().to_jpeg(quality=100)
                else:
                    img = sensor.snapshot()
                    temperature= get_temperature()
                    
                    if temperature > -900:
                        temp_text = f"{temperature:.1f}C"
                        img.draw_string(3, 3, temp_text, color=255, scale=1)
                        img.draw_cross(79, 59, color=255, size=6, thickness=1)
                        pixel_text = f"px:{pixel_count}"
                        img.draw_string(3, 25, pixel_text, color=255, scale=1)
                    else:
                        img.draw_string(3, 3, "TEMP ERR", color=255, scale=2)
                    
                    img = img.to_jpeg(quality=100)
                
                usb.send(struct.pack("<L", img.size()))
                usb.send(img)
                
            elif cmd == b"temp":
                temp_mode = not temp_mode
                
                if temp_mode:
                    led_red.on()
                    setup_radiometry()
                    time.sleep_ms(300)
                    status = b"TEMP_ON!"
                else:
                    led_red.off()
                    setup_agc()
                    time.sleep_ms(150)
                    status = b"TEMP_OFF"
                
                usb.send(struct.pack("<L", len(status)))
                usb.send(status)
            
            led_blue.off()
            
    except Exception as e:
        led_blue.off()
        led_red.off()
        if "Timeout" not in str(e):
            print(f"Error: {e}")
        
        if temp_mode:
            try:
                setup_radiometry()
                time.sleep_ms(100)
            except:
                pass
        else:
            try:
                setup_agc()
                time.sleep_ms(50)
            except:
                pass
