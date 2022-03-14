import board
import busio
import adafruit_mlx90640
import numpy
import cv2

i2c = busio.I2C(board.SCL, board.SDA, frequency=800000)

mlx = adafruit_mlx90640.MLX90640(i2c)
print("MLX addr detected on I2C", [hex(i) for i in mlx.serial_number])

# if using higher refresh rates yields a 'too many retries' exception,
# try decreasing this value to work with certain pi/camera combinations
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ

frame = [0] * 768
try:
    while True:
        try:
            mlx.getFrame(frame)
        except ValueError:
            # these happen, no biggie - retry
            continue

        nested_frame = []

        for h in range(24):
            row = []
            for w in range(32):
                frame[h*32 + w] *= 6.3
                row.append(frame[h*32 + w])
            nested_frame.append(row)
        #         t = frame[h*32 + w]
        #         print("%0.1f, " % t, end="")
        #     print()
        # print()

        np_array = numpy.array(nested_frame).astype('uint8')
        grayImage = cv2.resize(cv2.cvtColor(np_array, cv2.COLOR_GRAY2BGR), dsize=(320, 240))
        cv2.imshow("Thermal Camera", grayImage)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
except KeyboardInterrupt:
    pass

# cv2.imwrite('thermalimg.png',grayImage)
cv2.destroyAllWindows()
