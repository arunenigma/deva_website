import csv
from operator import itemgetter
import os
import itertools
import pygraphviz as pgv
from itertools import tee, izip, chain


class GraphSearch(object):
    def __init__(self, dot, cf_map, dot_name):
        self.dag = dot
        self.cf_map = cf_map
        self.stmts = []
        self.matched_ancestors = []
        self.matched_children = []
        self.results = {}
        self.cf = {}
        self.cf_normalized = {}
        self.dot_name = dot_name
        self.edges = []
        self.family = []
        self.file_name = ''
        self.pp = []

    def draw_dags(self):
        for row in self.cf_map:
            self.cf[(row[0], row[1])] = float(row[2])
        max_cf = max(self.cf.values())
        for pair, con_fac in self.cf.iteritems():
            self.cf_normalized[(pair[0], pair[1])] = con_fac / max_cf

        """
        dag = pgv.AGraph(directed=False, strict=True)
        d = dag.from_string(self.dag)
        self.edges = d.edges()
        for edge in self.edges:
            dag.add_node(edge[0], color='red', style='', shape='box',
                         fontname='courier')
            dag.add_node(edge[1], color='red', style='', shape='box',
                         fontname='courier')
            dag.add_edge(edge[0], edge[1], color='blue', style='', fontname='',
                         xlabel=round(self.cf_normalized.get((edge[0], edge[1])), 2))
        name = self.dot_name.replace('.dot', '.pdf')
        dag.write(self.dot_name)
        u = pgv.AGraph(file=self.dot_name)
        u.layout(prog='dot')
        u.draw(name)
        """

    def ancestry(self, q):
        q_kw = q.split(' ')
        dag = pgv.AGraph(directed=False, strict=True)
        d = dag.from_string(self.dag)
        edges = d.edges()
        #print edges
        for edge in edges:
            for kw in q_kw:
                if kw == edge[0]:
                    """
                    print 'Match Found: ', edge[0], edge, list(
                        reversed(self.get_predecessors(d, edge[0]))), d.successors(edge[0])
                    """
                    #print
                    ancestors = list(reversed(self.get_predecessors(d, edge[0])))
                    ancestors.append(edge[0])
                    if not ancestors in self.matched_ancestors:
                        self.matched_ancestors.append(ancestors)

                    children = list(reversed(self.get_successors(d, edge[0])))
                    children.append(edge[0])
                    if not children in self.matched_children:
                        self.matched_children.append(children)

                elif kw == edge[1]:
                    """
                    print 'Match Found: ', edge[1], edge, list(reversed(self.get_predecessors(d, edge[1])))
                    self.get_successors(d, edge[1])
                    """
                    #print
                    ancestors = list(reversed(self.get_predecessors(d, edge[1])))
                    ancestors.append(edge[1])
                    if not ancestors in self.matched_ancestors:
                        self.matched_ancestors.append(ancestors)

                    children = list(reversed(self.get_successors(d, edge[1])))
                    children.append(edge[1])
                    if not children in self.matched_children:
                        self.matched_children.append(children)
                else:
                    pass

    @staticmethod
    def get_predecessors(d, n):
        ancestors = []
        while d.predecessors(n):
            for ancestor in d.predecessors(n):
                ancestors.append(ancestor)
            n = d.predecessors(n)[0]
        return ancestors

    @staticmethod
    def get_successors(d, n):
        children = []
        while d.successors(n):
            for ancestor in d.successors(n):
                children.append(ancestor)
            n = d.successors(n)[0]
        return children

    def get_statements(self):
        for corpus, topics, files in os.walk("./searchengine/corpus"):
            path = '/'.join(corpus.split('/'))
            for txt_file in files:
                if '.txt' in txt_file:
                    if self.dot_name.split('/')[-1].split('.')[-2] == txt_file.split('.')[-2]:
                        self.file_name = txt_file
                        self.stmts = open(path + '/' + txt_file, 'rb').read().split('. ')

    def all_lower_case(self):
        stmts = []
        for stmt in self.stmts:
            stmt = [w.lower() for w in stmt.split(' ')]
            stmts.append(stmt)
        self.stmts = stmts

    def match_stmts(self):
        for stmt in self.stmts:
            self.family = list(itertools.chain(*(self.matched_ancestors + self.matched_children)))

            if self.family:
                match = set(stmt).intersection(set(self.family))
                query_kw = self.family[-1]
                if query_kw in match:
                    self.results[tuple(match)] = ' '.join(stmt)

    @staticmethod
    def pairs(iterable):
        a, b = tee(iterable)
        return izip(a, chain(b, [next(b)]))

    def calculate_cf(self, match):
        if len(match) > 1:
            edges = tuple(itertools.combinations(match, 2))
            conf = 0.0
            num_edges = 0

            for edge in edges:
                if edge in self.cf_normalized.keys():
                    num_edges += 1
                    conf += self.cf_normalized.get(edge)
                elif tuple(reversed(edge)) in self.cf_normalized.keys():
                    num_edges += 1
                    conf += self.cf_normalized.get(tuple(reversed(edge)))
            if num_edges > 0:
                return conf / num_edges
        else:
            pass  # ??

    def collect_results(self):
        for match, stmt in self.results.iteritems():
            related = list((set(self.family)) - set(match))
            con = self.calculate_cf(match)
            if not con:
                con = 0.0
            match = ', '.join(match)
            related = ', '.join(related)
            return [self.file_name, match, related, stmt, str(round(con * 100, 2)) + ' %']


def collect(query, coll_results):
    for root, dirs, docs in os.walk('./searchengine/dot'):
        for doc in docs:
            if '.dot' in doc:
                dag_dot = open('./searchengine/dot/' + doc, 'rb').read()
                cf_file = open('./searchengine/dot/' + doc.replace('.dot', '.csv'), 'rb')
                cf = csv.reader(cf_file)
                search = GraphSearch(dag_dot, cf, './searchengine/dot/' + doc)
                search.draw_dags()
                #
                search.ancestry(query)
                search.get_statements()
                search.all_lower_case()
                search.match_stmts()
                coll_results.append(search.collect_results())
    return coll_results


def pretty_printing(collected):
    collected = [x for x in collected if x is not None]
    return list(reversed(sorted(collected, key=itemgetter(4))))


def main(query):
    coll_results = []
    cr = collect(query, coll_results)
    return pretty_printing(cr)