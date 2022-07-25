import sys
import numpy as np
import serial

# ------ PART 1 -----
baud_rate = 19200
timeout_sec = 5
portname ='/dev/cu.usbserial-FT3J30KX'

ser = serial.Serial(portname, baud_rate, timeout=timeout_sec)  # open serial port
print(ser.name)            # check which port was really used

# ------ PART 2 -----

def freq_Hz_to_word(f_Hz):
    SYSCLK_Hz = 429.4967296 * 1e6
    return np.round(2**32 * f_Hz / SYSCLK_Hz).astype(int)
freqs_Hz_to_word = np.vectorize(freq_Hz_to_word)

def output_row(str_row, mode=0, ser=None):
    if mode==0:
        # for debugging / getting the commands right
        print(str_row)
    if mode==1:
        # for actually sending commands
        ser.write((str_row+'\r\n').encode())
        
def make_table_mode_line(rownum, f_word, dt_word, ch=0):
    f_bytes = format(f_word, '08x')
    dt_bytes = format(dt_word, '02x')
    table_entry_num_bytes = format(rownum, '04x')
    phase_bytes = format(0, '04x')                  # manually setting all phase entries to 0; only 14 bits active
    amplitude_bytes = format(2**10-1, '04x')              # manually setting all amplitude entries to max; only 10 bits active
    this_str_entry = ('t' + str(ch) + ' '  + table_entry_num_bytes + ' ' + f_bytes + ',' +
                      phase_bytes + ',' + amplitude_bytes + ',' + dt_bytes)
    return this_str_entry

def write_table_mode_data_to_dds(frequencies, dts_ms, ch=0, ser=None):
    min_dt_ms = 0.1                          # dwell time is in increments of 100μs
    dt_words = np.round(dts_ms / min_dt_ms).astype(int)
    if any(dt_words>255):
        print('Maximum step duration is 25.9 ms\n'+
              'Setting durations above 25.9 ms to 25.9 ms\n'+
              'If longer durations are required, use multiples steps at the same frequency\n')
        dt_words[dt_words>255] = 255
    df_words = freqs_Hz_to_word(frequencies)
    mode = 0 if ser==None else 1
    
    for j, [f_word, dt_word] in enumerate(zip(df_words, dt_words)):
        # For multichannel, each T0:T1 pair must have the same dwell
        # need to program them in parallel?
        this_str_entry = make_table_mode_line(j, f_word, dt_word, ch=ch)
        output_row(this_str_entry, mode=mode, ser=ser)
    # Final line dwell time: 0x00=loop back to start, 0xff=hold present setting.    
    this_str_entry = make_table_mode_line(j+1, f_word, 0, ch=ch)
    output_row(this_str_entry, mode=mode, ser=ser)        


# ----- PART 3 -----
def stop_table_mode_output(ser):
    ser.write(b'M 0\r\n\r\n')
    
def start_table_mode_output(ser):
    #stop_table_mode_output(ser)
    ser.write(b'M t\r\n')

def update_table_mode_output(ser): #funtion to output trigger signal Output #7 on digitizer
    #stop_table_mode_output(ser)
    ser.write(b'I a\r\n')

def main():
    print("FIRING THE LASER")
    dts_ms = np.array([0.5,0.5,0.5,0.5,0.5])   
    fs_Hz_ch0 = np.array([67,71,75,79,83])*1e6  #right, minus y #82.7
    fs_Hz_ch1 = np.array([75,75,75,75,75])*1e6     #down, minus x

    # write to DDS9m
    stop_table_mode_output(ser)
    write_table_mode_data_to_dds(fs_Hz_ch0, dts_ms, ch=0, ser=ser)
    write_table_mode_data_to_dds(fs_Hz_ch1, dts_ms, ch=1, ser=ser)
    update_table_mode_output(ser) #update for the trigger signal
    start_table_mode_output(ser)


def fire_single(pair):
    print("Firing single spot")



if __name__ == "__main__":
    main(sys.argv[1])
