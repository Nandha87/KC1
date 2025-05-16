import smbus
import time
import threading

# I2C address of CAP1203 (default)
CAP1203_ADDR = 0x28

# Register addresses
MAIN_CONTROL_REG = 0x00
SENSOR_INPUT_STATUS = 0x03
INTERRUPT_CLEAR = 0x00

class TouchSensor:
    def __init__(self):
        # Initialize I2C (Raspberry Pi uses bus 1)
        self.bus = smbus.SMBus(1)
        self.touch_callback = None
        self.is_running = False
        self.monitor_thread = None

    def read_touch_status(self):
        try:
            # Read the sensor input status register
            touch_status = self.bus.read_byte_data(CAP1203_ADDR, SENSOR_INPUT_STATUS)
            return touch_status
        except Exception as e:
            print("Error reading CAP1203:", e)
            return None

    def clear_interrupt(self):
        self.bus.write_byte_data(CAP1203_ADDR, INTERRUPT_CLEAR, 0x00)

    def set_touch_callback(self, callback):
        """Set the callback function to be called when touch is detected"""
        self.touch_callback = callback

    def start_monitoring(self):
        """Start monitoring touch events in a separate thread"""
        if not self.is_running:
            self.is_running = True
            self.monitor_thread = threading.Thread(target=self._monitor_touch)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop monitoring touch events"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join()

    def _monitor_touch(self):
        """Monitor touch events in a loop"""
        while self.is_running:
            status = self.read_touch_status()
            if status and self.touch_callback:
                if status & 0x01:
                    self.touch_callback("CS1")
                if status & 0x02:
                    self.touch_callback("CS2")
                if status & 0x04:
                    self.touch_callback("CS3")
            self.clear_interrupt()
            time.sleep(0.1)

# For testing the sensor directly
if __name__ == "__main__":
    def touch_handler(sensor):
        print(f"Touch detected on {sensor}")
    
    sensor = TouchSensor()
    sensor.set_touch_callback(touch_handler)
    sensor.start_monitoring()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sensor.stop_monitoring()
        print("Monitoring stopped")