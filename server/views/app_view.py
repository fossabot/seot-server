import json
import os
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from server.forms import AppForm
from server.models.app import App
from server.serializer import NodeSerializer
import yaml
UPLOAD_DIR = os.path.dirname(os.path.abspath(__file__)) + '/static/files'


class AppView:
    @staticmethod
    @transaction.atomic
    @login_required
    def get(request):
        app_list = []
        for app in App.objects.filter(user=request.user):
            app_list.append(app)
        return render(request, 'server/toppage.html', {'app_list': app_list})

    @staticmethod
    @transaction.atomic
    @login_required
    def upload(request):
        if request.method == 'POST':
            form = AppForm(request.POST, request.FILES)
            if form.is_valid():
                app = form.save()
                app.user = request.user
                app.save()
                app_to_nodes(app)
                return HttpResponseRedirect(reverse('toppage'))
        else:
            form = AppForm(initial={'user': request.user.username})
        return render(request, 'server/form.html', {'form': form})


# appオブジェクトを受取りnodeオブジェクト群を生成
def app_to_nodes(app):
    define_file = app.define_file
    define_file.open(mode='rb')
    nodes_data = yaml.load(define_file)
    define_file.close()
    return nodes_data_to_obj(app, nodes_data)


# nodeオブジェクトデータのリストからnodeオブジェクト生成
def nodes_data_to_obj(app, nodes_data):
    exist_nodes = []
    while True:
        node_gen = [n for n in nodes_data if 'to' not in n or
                    list_contains_list([n.name for n in exist_nodes], n['to'])]
        for node_data in node_gen:
            node = serialize_node(node_data)
            if node is not None:
                app.nodes.add(node)
                exist_nodes.append(node)
                if 'to' in node_data:
                    [node.next_nodes.add(n)
                     for n in exist_nodes if n.name in node_data['to']]
            nodes_data.remove(node_data)
        if len(nodes_data) == 0:
            return exist_nodes
        elif len(exist_nodes) == 0:
            return None


# python辞書型データからserializerを通してnodeオブジェクト保存
def serialize_node(node_data):
    # シリアライザに突っ込む前に、
    # argsがあればjson文字列に変換してargs_strフィールドに格納
    # もっとスマートな方法探す
    if 'args' in node_data:
        node_data['args_str'] = json.dumps(node_data['args'])
    serializer = NodeSerializer(data=node_data)
    if serializer.is_valid():
        return serializer.save()
    else:
        print(serializer.errors)
        return None


# parent_list内にchild_listの要素がすべて含まれているか
def list_contains_list(parent_list, child_list):
    return [n for n in parent_list if n in child_list] == child_list
