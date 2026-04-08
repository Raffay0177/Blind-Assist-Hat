# battery.py
# Mock battery monitoring module until I2C hardware is implemented

def get_battery_level():
    """ 
    Since standard USB powerbanks don't provide a data interface to the Pi,
    this returns a static placeholder value. Once an I2C ADC or UPS hat 
    is installed, this function can be wired to read the real percentage.
    """
    return "85"
