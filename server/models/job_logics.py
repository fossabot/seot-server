from .agent import Agent


class JobLogics(object):
    # next_nodesのうちagentで動かせるノードを1つ返す
    # また、jobへ既にセンサノードが割り当てられている時は、
    # 同じタイプのセンサノードは割り当てない
    # すでにjobが存在していてわりあてるagentも決まっているとき、
    # このメソッドで次に割り当てるnodeを参照する
    def find_next_node(self, next_nodes):
        executable_nodes = [
                node for node in next_nodes
                if self.allocated_agent.available_node_types.filter(
                    name=node.node_type.name)
                and not self.type_of_node_in_job(node.sensor_name())
                ]
        if executable_nodes:
            node = executable_nodes[0]
            next_nodes.remove(node)
            return node
        return None

    # ジョブの中に与えられたノードタイプのノードがあるか？
    def type_of_node_in_job(self, node_type_name):
        if self.nodes is not None and node_type_name is not None:
            return self.nodes.filter(
                    node_type__name=node_type_name).exists()
        return False

    # nodeをjobにadd
    # addした後next_nodesを更新
    def add_node(self, node, next_nodes):
        self.nodes.add(node)
        for next_node in node.next_nodes.all():
            # next_nodes内に重複要素が出ないよう確認、
            # また、next_nodesが既にjobに割り当てられていないか確認してからappend
            if next_node.name not in [n.name for n in next_nodes] and\
                    next_node.job is None:
                next_nodes.append(next_node)
        if node in next_nodes:
            next_nodes.remove(node)

    # 新しいjobをnameを指定して生成
    # job未割り当てなnodeから適当に一つ選択
    # 選択したnodeを動かせるagentを選択
    @classmethod
    def create_new_job(cls, name, next_nodes, asigned_agents):
        job = cls.objects.create(name=name)
        node = next_nodes.pop()
        agent_list = [a for a in Agent.objects.filter(
            available_node_types__name__contains=node.node_type.name)
            if a not in asigned_agents]
        if agent_list:
            agent = agent_list.pop()
            agent.allocated_jobs.add(job)
            return job, node, agent
        else:
            return None, None, None
