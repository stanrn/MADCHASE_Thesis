from threading import Event

# Keep list with already received measurements for continuous measurements
received_measurements = []
expected_measurements = set()
batch_done = Event()

# Event for stopping the broadcast
stop_event = Event()