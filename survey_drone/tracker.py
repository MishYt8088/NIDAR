class YellowTracker:
    def __init__(self, stable_frames=10):
        self.stable_frames = stable_frames
        self.count = 0
        self.locked = False

    def update(self, detected):
        if detected:
            self.count += 1
        else:
            self.count = 0
            self.locked = False

        if self.count >= self.stable_frames:
            self.locked = True

        return self.locked
