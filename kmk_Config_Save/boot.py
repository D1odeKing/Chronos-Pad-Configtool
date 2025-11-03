import storage
storage.remount("/", readonly=False)
storage.getmount("/").label = "CHRONOSPAD"
storage.remount("/", readonly=True)
