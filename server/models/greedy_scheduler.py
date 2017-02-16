from .abst_scheduler import AbstScheduler
from .job import Job


class GreedySchduler(AbstScheduler):
    def __init__(self):
        self.nodes_list = []
        self.next_nodes = []
        self.already_asigned_agents = []
        self.index = 0
        self.jobs = []

    # appからjob群を生成
    def init_jobs(self, app):
        for n in app.nodes.all():
            self.nodes_list.append(n)
        if not self.nodes_list:
            print('no nodes in app')
            return None
        self.next_nodes = [n for n in self.nodes_list if n.is_source()]
        job = self._open_job(app)
        if job is None:
            print('job is none')
            return None
        while True:
            node = job.find_executable_node(self.next_nodes)
            if node is not None:
                self._update_job(job, node)
                if len(self.nodes_list) == 0 and len(self.next_nodes) == 0:
                    self._close_job(job)
                    break
                elif len(self.nodes_list) == 0 or len(self.next_nodes) == 0:
                    print("nodes_list update error")
                    return None
            else:
                self._close_job(job)
                job = self._open_job()
                if job is None:
                    print("couldn't create job")
                    return None
        return self.jobs

    # next_nodesリスト（次にJobに割り当てるnodeのリスト）を更新
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

    def _open_job(self, app):
        job, agent = Job.new(
                str(app.id) + "_" + str(self.index),
                self.next_nodes[0],
                self.already_asigned_agents)
        self._update_job(job, self.next_nodes[0])
        self.already_asigned_agents.append(agent)
        self.index += 1
        return job

    def _update_job(self, job, node):
        job.nodes.add(node)
        self._update_nodeslist(node)

    def _close_job(self, job):
        self.jobs.append(job)
        job.save()
