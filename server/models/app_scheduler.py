import json
from .job import Job
from .node import Node
from .nodetype import NodeType


class AppScheduler(object):
    nodes_list = []
    next_nodes = []
    already_asigned_agents = []
    index = 0
    jobs = []

    # appからjob群を生成
    def make_jobs(self):
        for n in self.nodes.all():
            self.nodes_list.append(n)
        if not self.nodes_list:
            return None
        self.next_nodes = [n for n in self.nodes_list if n.is_source()]
        job = self._open_job()
        while True:
            node = job.find_executable_node(self.next_nodes)
            if node is not None:
                self._update_job(job, node)
                if not self.nodes_list and not self.next_nodes:
                    self._close_job(job)
                    break
                elif not self.nodes_list or not self.next_nodes:
                    print("nodes_list update error")
                    return None
            else:
                self._close_job(job)
                job = self._open_job()
                if job is None:
                    print("couldn't create job")
                    return None
        self._create_zmq_pair()
        return self.jobs.all()

    # job内の末端ノードで、かつ、別job内に位置するnext_nodesを持つノードを
    # 選び出し、そのノードとnext_nodesとの間に ZMQSink / ZMQSourceのペアを挿入
    def _create_zmq_pair(self):
        zmq_sink_type = NodeType.objects.get(name="ZMQSink")
        zmq_source_type = NodeType.objects.get(name="ZMQSource")

        for node in self.nodes.all():
            for n in node.next_nodes.exclude(job=node.job):
                zmq_sink = Node.objects.create(
                    node_type=zmq_sink_type,
                    name=node.name + "_to_" + n.name + "_sink")
                zmq_source = Node.objects.create(
                    node_type=zmq_source_type,
                    name=node.name + "_to_" + n.name + "_source")
                node.next_nodes.remove(n)
                node.next_nodes.add(zmq_sink)
                zmq_source.next_nodes.add(n)

                node.job.nodes.add(zmq_sink)
                n.job.nodes.add(zmq_source)

                self.nodes.add(zmq_sink)
                self.nodes.add(zmq_source)

                target_ip_addr = {}
                target_ip_addr['url'] = 'tcp://{0}:{1}'.format(
                        str(n.job.allocated_agent.ip_addr),
                        str(n.job.allocated_agent.dpp_listen_port))
                zmq_sink.args = json.dumps(target_ip_addr)
                zmq_sink.save()

    # appが持つnext_nodesリスト（次にJobに割り当てるnodeのリスト）を更新
    # 直前にJobに割り当てたnodeを引数として受取り、そのnodeからつながるnode群を
    # next_nodesにappend (この際next_nodes内で重複が起きないようにする)
    # その後割当て済みのnodeをnext_nodes, nodes_listから取り除く
    def _update_nodeslist(self, node):
        for next_node in node.next_nodes.all():
            if next_node not in self.next_nodes and next_node.job is None:
                self.next_nodes.append(next_node)
        if node in self.next_nodes:
            self.next_nodes.remove(node)
        if node in self.nodes_list:
            self.nodes_list.remove(node)

    def _open_job(self):
        job, agent = Job.new(
                str(self.id) + "_" + str(self.index),
                self.next_nodes[0],
                self.already_asigned_agents)
        self._update_nodeslist(self.next_nodes[0])
        self.already_asigned_agents.append(agent)
        self.index += 1
        return job

    def _update_job(self, job, node):
        job.nodes.add(node)
        self._update_nodeslist(node)

    def _close_job(self, job):
        self.jobs.add(job)
        job.save()
