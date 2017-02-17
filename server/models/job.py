import uuid
from django.db import models
from .agent import Agent
from .job_status import JobStatus


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, default='')
    application = models.ForeignKey(
            'App',
            models.SET_NULL,
            related_name='jobs',
            blank=True,
            null=True)
    allocated_agent = models.ForeignKey(
            'Agent',
            models.SET_NULL,
            related_name='allocated_jobs',
            blank=True,
            null=True)
    status = models.IntegerField(
        choices=JobStatus.choices(),
        default=JobStatus.idle.value,
        verbose_name='Job Status'
    )
    updated_at = models.DateTimeField(auto_now=True)

    def running(self):
        running = True
        for n in self.nodes.all():
            running = running and n.running
        return running

    def __str__(self):
        return '%s' % (self.id)

    # next_nodesのうちjobに割当できる（jobで実行できる）ノードを1つ返す
    # jobへ既にセンサノードが割り当てられている時は、
    # 同じタイプのセンサノードは割り当てない
    def find_executable_node(self, next_nodes):
        executable_nodes = [
                node for node in next_nodes
                if self.allocated_agent.available_node_types.filter(
                    name=node.node_type.name)
                and not self.has_nodetype(node.sensor_name())
                ]
        if executable_nodes:
            node = executable_nodes[0]
            return node
        return None

    # ジョブの中に与えられたノードタイプのノードがあるか
    def has_nodetype(self, nodetype_name):
        if self.nodes is not None and nodetype_name is not None:
            return self.nodes.filter(
                    node_type__name=nodetype_name).exists()
        return False

    # 新しいjobを生成
    # nameを指定し、さらに指定されたnodeを動かせるagentを選択
    @classmethod
    def new(cls, name, node, asigned_agents):
        job = cls.objects.create(name=name)
        agent_list = [a for a in Agent.objects.filter(
            available_node_types__name__exact=node.node_type.name,
            active=True)
            if a not in asigned_agents]
        if agent_list:
            agent = agent_list.pop()
            agent.allocated_jobs.add(job)
            return job, agent
        else:
            job.delete()
            return None, None
