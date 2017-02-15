class NodeLogics(object):
    # nodeが始端ノードであるか判定
    def is_source(self):
        num = self.before_nodes.count()
        if num == 0:
            return True
        return False

    # ノードタイプがセンサ系か否か
    # センサ系ならノード名文字列を、そうでなければNullを返す
    def sensor_name(self):
        if self.node_type is not None:
            if self.node_type.name in [
                    "StubSenseHatSource",
                    "SenseHatSource",
                    "PiCameraSource"]:
                return self.node_type.name
        return None
