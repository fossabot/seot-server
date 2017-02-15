import json
from server.serializer import NodeSerializer
import yaml


# App定義ファイルアップロード時、Appモデルのセットアップの為に用いられる
# メソッド群を定義したファイル
class AppSetupLogics(object):
    # appオブジェクトを受取りnodeオブジェクト群を生成
    def app_to_nodes(self):
        define_file = self.define_file
        define_file.open(mode='rb')
        nodes_data = yaml.load(define_file)
        define_file.close()
        return self.nodes_data_to_obj(nodes_data)

    # nodeオブジェクトデータのリストからnodeオブジェクト生成、
    # 自身に紐付ける
    def nodes_data_to_obj(self, nodes_data):
        exist_nodes = []
        while True:
            node_gen = [n for n in nodes_data if 'to' not in n or
                        self.list_contains_list(
                            [n.name for n in exist_nodes], n['to'])]
            for node_data in node_gen:
                if 'args' in node_data:
                    node_data['args_str'] = json.dumps(node_data['args'])
                serializer = NodeSerializer(data=node_data)
                node = None
                if serializer.is_valid():
                    node = serializer.save()
                else:
                    print(serializer.errors)
                if node is not None:
                    self.nodes.add(node)
                    exist_nodes.append(node)
                    if 'to' in node_data:
                        [node.next_nodes.add(n)
                         for n in exist_nodes if n.name in node_data['to']]
                nodes_data.remove(node_data)
            if len(nodes_data) == 0:
                return exist_nodes
            elif len(exist_nodes) == 0:
                return None

    # parent_list内にchild_listの要素がすべて含まれているか
    @staticmethod
    def list_contains_list(parent_list, child_list):
        return [n for n in parent_list if n in child_list] == child_list
