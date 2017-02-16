import json
from .job import Job
from .node import Node
from .nodetype import NodeType


class AppScheduler(object):
    # appからjob群を生成
    def make_jobs(self):
        index = 0
        jobs = []
        already_asigned_agents = []
        nodes = self.nodes.all()
        nodes_list = []
        for n in nodes:
            nodes_list.append(n)
        if not nodes_list:
            return None
        next_nodes = [n for n in nodes_list if n.is_source()]
        job, node, agent = Job.new(
                str(self.id) + "_" + str(index),
                next_nodes,
                already_asigned_agents)
        index += 1
        while True:
            job.add_node(node, next_nodes)
            nodes_list.remove(node)
            if len(nodes_list) == 0:
                self.jobs.add(job)
                job.save()
                jobs.append(job)
                break
            node = job.find_next_node(next_nodes)
            if node is not None:
                pass
            else:
                self.jobs.add(job)
                job.save()
                jobs.append(job)
                already_asigned_agents.append(agent)
                job, node, agent = Job.create_new_job(
                    str(self.id) + "_" + str(index),
                    next_nodes, already_asigned_agents)
                index += 1
                if job is None:
                    print("couldn't create job")
                    return None
        self.create_zmq_pair()
        return jobs

    # job内の末端ノードで、かつ、別job内に位置するnext_nodesを持つノードを
    # 選び出し、そのノードとnext_nodesとの間に ZMQSink / ZMQSourceのペアを挿入
    def create_zmq_pair(self):
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

    def update_nextnodes(self, node):
        for next_node in node.next_nodes.all():
            if next_node not in self.next_nodes and next_node.job is None:
                self.next_nodes.append(next_node)
        if node in self.next_nodes:
            self.next_nodes.remove(node)
