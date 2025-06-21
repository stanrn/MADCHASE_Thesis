import matplotlib.pyplot as plt
import numpy as np
import json
import os

class DataPlotter:
    value_max = 2 ** 13

    def __init__(self, file_path, folder_path, measurement_number = 1):
        self.file_path = file_path  # JSON file
        self.folder_path = folder_path  # Where to save plots
        self.measurement_number = measurement_number # Used for creating plot with correct name
        
        # Initialize attributes for datameasurement_number
        self.i_local = None
        self.q_local = None
        self.i_remote = None
        self.q_remote = None
        self.hopping_sequence = None
        self.sinr_local = None
        self.sinr_remote = None
        self.fft = None
        self.phase_slope = None
        self.rssi_openspace = None
        self.best = None
        self.highprec = None
        self.link_loss = None
        self.duration = None
        self.rssi_local = None
        self.rssi_remote = None
        self.txpwr_local = None
        self.txpwr_remote = None
        self.quality = None
        
        # Attributes for transfer functions and impulses
        self.remote = None
        self.local = None
        self.transfer2 = None
        self.transfer = None
        self.impulse = None
        self.impulse_x = None
        self.delaySpread = None
        self.delaySpread2 = None

    def read_data(self):
        """Read data from the specified JSON file"""
        try:
            with open(self.file_path, "r") as file:
                data = json.load(file)  # Load the entire JSON data
                print(data)
                record = data  # Access the first (and only) record

                # Extract relevant data into instance variables
                self.i_local = np.array(record["i_local"])
                self.q_local = np.array(record["q_local"])
                self.i_remote = np.array(record["i_remote"])
                self.q_remote = np.array(record["q_remote"])
                self.hopping_sequence = np.array(record["hopping_sequence"])
                self.sinr_local = np.array(record["sinr_local"])
                self.sinr_remote = np.array(record["sinr_remote"])
                self.fft = record["ifft[mm]"]
                self.phase_slope = record["phase_slope[mm]"]
                self.rssi_openspace = record["rssi_openspace[mm]"]
                self.best = record["best[mm]"]
                self.highprec = record["highprec[mm]"]
                self.link_loss = record["link_loss[dB]"]
                self.duration = record["duration[us]"]
                self.rssi_local = record["rssi_local[dB]"]
                self.rssi_remote = record["rssi_remote[dB]"]
                self.txpwr_local = record["txpwr_local[dB]"]
                self.txpwr_remote = record["txpwr_remote[dB]"]
                self.quality = record["quality"]
        except FileNotFoundError:
            print(f"Error: File not found at {self.file_path}.")
        except ValueError as e:
            print(f"Error: Unable to read data from JSON file. {e}")

    def calcTransfer2(self):    # Squared transfer function
        l = self.i_local + np.multiply(1j, self.q_local)
        r = self.i_remote + np.multiply(1j, self.q_remote)
        self.remote = r
        self.local = l
        self.transfer2 = np.multiply(l, r)

    def calcTransfer(self):
        fstart = 4
        fstop = 78

        tr = np.zeros(len(self.transfer2), dtype=complex)
        
        # Do a linear regression to find an optimum slope
        x = np.arange(fstart, fstop, 1)
        ang = np.unwrap(np.angle(self.transfer2))
        A = np.vstack([x, np.ones(len(x))]).T
        xang = np.linalg.lstsq(A, ang[fstart:fstop], rcond=None)[0]
        xall = np.arange(0, 80, 1)
        th_ideal = xang[0] / 2 * xall + xang[1] / 2
        smag = np.sqrt(np.abs(self.transfer2))
        sang = ang / 2

        for i in range(fstart, fstop):
            at = th_ideal[i]
            diff = sang[i] - th_ideal[i]
            if diff > np.pi:
                sang[i] = sang[i] - np.pi
            elif diff < -np.pi:
                sang[i] = sang[i] + np.pi

        self.transfer = np.multiply(smag, np.exp(1j * sang))
        self.sang = sang


    def calcImpulse2(self):
        N = 2048
        yfft = np.fft.ifft(self.transfer2,N)
        yf = yfft[0:((int)(len(yfft)/2))]
        self.impulse2 = yf
        self.impulse2_x = np.arange(0,N/2)/N/2/1e6

    def calcImpulse(self):
        N = 2048
        yfft = np.fft.ifft(self.transfer, N)
        yf = yfft[0:((int)(len(yfft) / 2))]
        self.impulse = yf
        self.impulse_x = np.arange(0, N / 2) / N / 1e6
        
    def calcImpulse2(self):
        N = 2048
        yfft = np.fft.ifft(self.transfer2, N)
        yf = yfft[0:((int))(len(yfft)/2)]
        self.impulse2 = yf
        self.impulse2_x = np.arange(0, N/2)/N/2/1e6

    def calcDelaySpread(self):
        y = self.impulse
        s = np.abs(y**2)
        s = s / np.max(s)

        # Remove the lowest values. They are likely artifacts of IFFT.
        s[s < 0.01] = 0

        pwr = np.sum(s)
        p1 = np.sum(np.multiply(s, self.impulse_x))
        p2 = np.sum(np.multiply(s, self.impulse_x**2))
        rms = np.sqrt(p2/pwr - (p1/pwr)**2)

        self.delaySpread = rms

    def calcDelaySpread2(self):  # Squared delay spread function
        s = np.abs(self.impulse2)**2

        pwr = np.sum(s)
        p1 = np.sum(np.multiply(s, self.impulse2_x))
        p2 = np.sum(np.multiply(s, self.impulse2_x**2))
        rms = np.sqrt(p2/pwr - (p1/pwr)**2)

        self.delaySpread2 = rms

    def plot_delay_spreads(self):
        plt.figure(figsize=(8, 5))

        delay_spreads = [self.delaySpread, self.delaySpread2]
        labels = ['Delay Spread 1', 'Delay Spread 2']
        
        plt.bar(labels, delay_spreads, color=['#556B2F', '#B87333'])
        plt.title("RMS Delay Spreads")
        plt.ylabel("RMS Delay Spread (samples)")
        plt.grid(axis='y')

        delay_spread_plot_path = os.path.join(self.folder_path, f"delay_spreads_meas{self.measurement_number}.svg")
        plt.savefig(delay_spread_plot_path)
        plt.close()

    def plot_signals(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.i_local / self.value_max, linestyle="-", color="#B87333", label="i_local")
        plt.plot(self.q_local / self.value_max, linestyle=":", color="#B87333", label="q_local")
        plt.plot(self.i_remote / self.value_max, linestyle="-", color="#556B2F", label="i_remote")
        plt.plot(self.q_remote / self.value_max, linestyle=":", color="#556B2F", label="q_remote")

        plt.title("Recorded IQ Data Plot")
        plt.xlabel("Sample Index")
        plt.ylabel("Value")
        plt.grid(True)
        plt.legend()
        
        plot_path = os.path.join(self.folder_path, f"iq_data_same_plot_meas{self.measurement_number}.svg")
        plt.savefig(plot_path)
        plt.close()

    def plot_subplots(self):
        fig, axs = plt.subplots(2, 2, figsize=(12, 5), sharex=True)
        axs = axs.flatten()
        fig.suptitle("First 80 Samples of Recorded IQ Data")

        axs[0].plot(self.i_local / self.value_max, linestyle="-", color="#B87333")
        axs[0].set_title("i_local")
        axs[0].set_ylabel("Value")
        axs[0].grid(True)

        axs[1].plot(self.q_local / self.value_max, linestyle=":", color="#B87333")
        axs[1].set_title("q_local")
        axs[1].set_ylabel("Value")
        axs[1].grid(True)

        axs[2].plot(self.i_remote / self.value_max, linestyle="-", color="#556B2F")
        axs[2].set_title("i_remote")
        axs[2].set_ylabel("Value")
        axs[2].grid(True)

        axs[3].plot(self.q_remote / self.value_max, linestyle=":", color="#556B2F")
        axs[3].set_title("q_remote")
        axs[3].set_xlabel("Sample Index")
        axs[3].set_ylabel("Value")
        axs[3].grid(True)

        plt.tight_layout()
        subplot_path = os.path.join(self.folder_path, f"IQ_data_separate_plot_meas{self.measurement_number}.svg")
        plt.savefig(subplot_path)
        plt.close()

    def plot_impulses(self):
        fig, axs = plt.subplots(1, 1, figsize=(8, 4), sharex=True)
        fig.suptitle("Impulse Responses")

        if self.impulse is not None:
            # Plot the magnitude of the impulse response
            y =  np.abs(self.impulse**2)
            y =  y/np.max(y)
            
            axs.plot(self.impulse_x*10**9, y, color="#556B2F", label="Impulse Magnitude")
            
            # Find the index of the maximum value (argmax)
            max_idx = np.argmax(y)
            max_value = y[max_idx]
            max_time = self.impulse_x[max_idx]

            # Mark the argmax on the plot
            axs.scatter(max_time*10**9, max_value, color='red', zorder=5)  # Mark the point
            axs.text(max_time*10**9, max_value, f'  max = {max_time*10**9:.2f}', color='red')  # Annotate the point

            axs.set_title("Impulse Magnitude")
            axs.set_ylabel("Magnitude")
            axs.set_xlabel("Time [ns]")
            axs.grid(True)
            



        plt.tight_layout()
        impulse_plot_path = os.path.join(self.folder_path, f"impulse_responses_meas{self.measurement_number}.svg")
        plt.savefig(impulse_plot_path)
        plt.close()

    def plot_transfer(self):
        fig, axs = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
        fig.suptitle("Transfer Function")

        if self.transfer is not None:
            # Define frequency array
            N = len(self.transfer)
            sample_rate = 1e6  # Adjust this based on your actual sample rate
            frequency = np.fft.fftfreq(N, d=1/sample_rate)

            axs[0].plot(frequency[:N//2]*10**(-6), np.abs(self.transfer)[:N//2], color='#556B2F')
            axs[0].set_title("Transfer Function Magnitude")
            axs[0].set_ylabel("Magnitude")
            axs[0].grid(True)

            axs[1].plot(frequency[:N//2]*10**(-6), np.angle(self.transfer)[:N//2], color='#556B2F')
            axs[1].set_title("Transfer Function Phase")
            axs[1].set_xlabel("Frequency (MHz)")
            axs[1].set_ylabel("Phase (radians)")
            axs[1].grid(True)

        plt.tight_layout()
        transfer_plot_path = os.path.join(self.folder_path, f"transfer_function_meas{self.measurement_number}.svg")
        plt.savefig(transfer_plot_path)
        plt.close()

    def plot_data(self):
        self.read_data()
        if self.i_local is not None:  
            self.calcTransfer2()
            self.calcTransfer()
            self.calcImpulse()
            self.calcImpulse2()
            #self.calcDelaySpread()
            #self.calcDelaySpread2()
            self.plot_signals()
            self.plot_subplots()
            self.plot_impulses()
            self.plot_transfer()
            #self.plot_delay_spreads()

# Example usage:
# plotter = DataPlotter("data_recorded.json", "figures/")
# plotter.plot_data()
