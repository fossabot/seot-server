from .abst_scheduler import AbstScheduler
from .job import Job


class GreedySchduler(AbstScheduler):
    def __init__(self):
        self.define_nodes = []
        self.candidate_nodes = []
        self.asigned_agents = []
        self.index = 0
        self.jobs = []
        self.app_id = ''

    # appからjobリストを生成
    def init_jobs(self, app):
        self.app_id = app.id
        for n in app.nodes.all():
            self.define_nodes.append(n)
        if not self.define_nodes:
            print('no nodes in app')
            return None
        self.candidate_nodes = [n for n in self.define_nodes if n.is_source()]
        job = self._open_job()
        if job is None:
            print('job is none')
            return None
        while True:
            node = job.find_executable_node(self.candidate_nodes)
            if node is not None:
                self._update_job(job, node)
                if len(self.define_nodes) == 0\
                        and len(self.candidate_nodes) == 0:
                    self._close_job(job)
                    break
                elif len(self.define_nodes) == 0\
                        or len(self.candidate_nodes) == 0:
                    print("define_nodes update error")
                    return None
            else:
                self._close_job(job)
                job = self._open_job()
                if job is None:
                    print("couldn't create job")
                    return None
        return self.jobs

    # candidate_nodesリスト（次にJobに割り当てるnodeのリスト）を更新
    # 直前にJobに割り当てたnodeを引数として受取り、そのnodeからつながるnode群を
    # candidate_nodesにappend (この際candidate_nodes内で重複が起きないようにする)
    # その後割当て済みのnodeをcandidate_nodes, nodes_listから取り除く
    def _update_candidates(self, node):
        for next_node in node.next_nodes.all():
            if next_node not in self.candidate_nodes and next_node.job is None:
                self.candidate_nodes.append(next_node)
        if node in self.candidate_nodes:
            self.candidate_nodes.remove(node)
        if node in self.define_nodes:
            self.define_nodes.remove(node)

    def _open_job(self):
        job, agent = Job.new(
                str(self.app_id) + "_" + str(self.index),
                self.candidate_nodes[0],
                self.asigned_agents)
        self._update_job(job, self.candidate_nodes[0])
        self.asigned_agents.append(agent)
        self.index += 1
        return job

    def _update_job(self, job, node):
        job.nodes.add(node)
        self._update_candidates(node)

    def _close_job(self, job):
        self.jobs.append(job)
        job.save()
