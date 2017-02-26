import json
from .greedy_scheduler import GreedySchduler
from .node import Node
from .nodetype import NodeType


class AppScheduler(object):
    def launch_jobs(self):
        greedy_sch = GreedySchduler()
        jobs = greedy_sch.init_jobs(self)
        for j in jobs:
            self.jobs.add(j)
        if self._create_zmq_pair() is None:
            return None
        self.save()
        return self.jobs.all()

    # 所属jobが異なるnext_nodesを持つノードを選び出し、
    # そのノードとnext_nodesとの間に ZMQSink / ZMQSourceのペアを挿入
    def _create_zmq_pair(self):
        zmq_sink_type = NodeType.objects.get(name="ZMQSink")
        zmq_source_type = NodeType.objects.get(name="ZMQSource")

        for node in self.nodes.all():
            for n in node.next_nodes.exclude(job=node.job):
                zmq_sink = Node.objects.create(
                    node_type=zmq_sink_type,
                    name=node.name + "_to_" + n.name + "_sink",
                    automatically_added=True)
                try:
                    zmq_source = n.before_nodes.get(
                        node_type=zmq_source_type,
                        automatically_added=True)
                except Node.DoesNotExist:
                    zmq_source = Node.objects.create(
                        node_type=zmq_source_type,
                        name=n.name + '_source',
                        automatically_added=True,
                        listen_port=n.job.allocated_agent.dpp_listen_port)
                    n.job.allocated_agent.update_listen_port()
                except Node.MultipleObjectsReturned:
                    return None
                node.next_nodes.remove(n)
                node.next_nodes.add(zmq_sink)
                zmq_source.next_nodes.add(n)

                node.job.nodes.add(zmq_sink)
                n.job.nodes.add(zmq_source)

                self.nodes.add(zmq_sink)
                self.nodes.add(zmq_source)

                dst_url = {}
                dst_url['url'] = 'tcp://{0}:{1}'.format(
                        str(n.job.allocated_agent.ip_addr),
                        str(zmq_source.listen_port))
                zmq_sink.args = json.dumps(dst_url)
                zmq_sink.save()
                listen_url = {}
                listen_url['url'] = 'tcp://0.0.0.0:{0}'.format(
                        str(zmq_source.listen_port))
                zmq_source.args = json.dumps(listen_url)
                zmq_source.save()
        return self.nodes.all()
