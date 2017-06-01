import re
from collections import defaultdict
import pickle
import pprint
from copy import deepcopy


class Flag:
    def __init__(self, code):
        self.code = code


class Reference:
    def __init__(self, code, state, term):
        self.code = code
        self.state = state
        self.term = term


class Stack:
    __counter = 1
    # V slovniku flag_dict su kluce jedinecne identifikatory prechodu z urciteho
    # stavu na iny stav. Hodnota slovnika je list tupli, ktore na nultom mieste
    # obsahuju referenciu na stack, na ktory prechadza prechod a index do
    # listu states samotneho zasobnika
    flag_dict = defaultdict(list)

    def __init__(self):
        # Pozor, nemylit stack a states. Do stacku sa ukladaju stavy
        # a terminaly, s ktorymi sa aktualne pracuje a states su uz hotove
        # terminaly, ktore vznikli.
        # self.output = ""
        self.stack = []
        self.info = ""
        self.code = type(self).__counter
        self.states = []
        type(self).__counter += 1

    def extend(self, contents):
        self.stack.extend(contents)

    def term_output(self, output):
        self.states.append(output)
        if type(output) is Flag:
            type(self).flag_dict[output.code].append((self, len(self.states)-1))
        # self.output += output

    def pop(self):
        return self.stack.pop()

    def print_info(self):
        if self.info:
            print(self.info)

    def print_states(self, print_p=True):
        for s in self.states:
            if type(s) not in [Reference, Flag]:
                print(s, end=' ')
            elif type(s) is Flag:
                print('(' + str(s.code), end=') ')
            else:
                print('{' + str(s.code), end='} ')
        # print()

    def cycled(self):
        flags = [x.code for x in self.states if type(x) is Flag]
        if type(self.states[-1]) is Reference:
            if self.states[-1].code in flags:
                # print('zacyklili sme sa')
                return True
        return False

    def finished(self):
        if type(self.states[-1]) is Reference:
            return False
        # print('Ukoncili sme')
        return True

    def deepcopy(self):
        # Potrebujeme zachovat referencie zo slovnika
        # flagov aj na tento novy stack
        new_stack = deepcopy(self)
        for i, f in enumerate(self.states):
            if type(f) is Flag:
                type(self).flag_dict[f.code].append((new_stack, i))
        return new_stack


def beautify(string):
    d = {}
    d['Ttree'] = 'tree'
    d['T_str'] = 'STRING'
    d['Tspace'] = 'space'
    d['Tprimary'] = 'primary'
    d['Tfunction'] = 'function'
    d['T_id'] = 'ID'
    d['Tby'] = 'by'
    d['Tof'] = 'of'
    d["T|';'"] = ';'
    d["T|'='"] = '='
    d["T|'+'"] = '+'
    d["T|'-'"] = '-'
    d["T|' '"] = 'SPACE'
    d["T|'{'"] = '{'
    d["T|'}'"] = '}'
    d["T|':'"] = ':'
    d["T|'*'"] = '*'

    return d.get(string, string)


def expand(state, terminal):
    # bude obsahovat tuple (stav, terminal), ktore uz boli navstivene
    visited = set()
    global visited_code
    anchors = {}
    stack = Stack()
    finished = []
    contents = lang[state][terminal]
    stack.extend(contents[::-1])
    stacks = [stack]
    while stacks:
        stack = stacks.pop()
        while stack.stack:
            term = stack.pop()
            if term == 'START':
                stack.info = 'Prehladavanie ukoncene pri stave START\nZvysok za\
sobnika: ' + str(stack.stack)
                stack.stack = []
                break
            if term in lang:
                # jedna sa o prechod do ineho stavu
                terms = lang[term]
                # Predidenie zakernemu bugu, aby sme si neprepisovali
                # zasobniky, pri vytvarani novych stackov budeme
                # kopirovat povodny zasobnik, nie ten, co uz bol
                # upraveny
                old_stack = deepcopy(stack)
                for i, t in enumerate(terms):
                    # i su cisla od 0
                    # t su kluce do slovnika terminalov
                    if (term, t) not in visited:
                        if i > 0:
                            # vytvor novy stack
                            new_stack = old_stack.deepcopy()
                            new_stack.extend(terms[t][::-1])
                            visited.add((term, t))
                            anchors[(term, t)] = visited_code
                            new_stack.term_output(Flag(visited_code))
                            visited_code += 1
                            stacks.append(new_stack)
                            continue
                        contents = terms[t][::-1]
                        stack.extend(contents)
                        visited.add((term, t))
                        anchors[(term, t)] = visited_code
                        stack.term_output(Flag(visited_code))
                        visited_code += 1
                    else:
                        if i > 0:
                            new_stack = old_stack.deepcopy()
                            new_stack.extend(terms[t][::-1])
                            new_stack.term_output(Reference(anchors[(term, t)], term, t))
                            new_stack.info += 'Zvysok zasobnika: ' + str(old_stack.stack)
                            # Vyprazdnime zasobnik, aby sa uz dalej nespracovaval
                            new_stack.stack = []
                            stacks.append(new_stack)
                            continue
                        stack.term_output(Reference(anchors[(term, t)], term, t))
                        stack.info += 'Zvysok zasobnika: ' + str(stack.stack)
                        stack.stack = []
                # end for i, t in enumerate(terms)
            else:
                # Nejedna sa o stav
                stack.term_output(beautify(term))
            # end if term in lang
        # end while stack.stack
        finished.append(stack)
    # end while stacks:

    # Mozem vratit uz teraz, ak nechcem robit dalsi rozklad
    return finished, anchors

    # Nasleduje dalsie rozvinutie zasobnikov a hladanie cyklov
    # Vo finished sa nachadzaju zasobniky, ktore chceme spracovat
    # V stacks sa budu nachadzat hotove zasobniky
    while finished:
        stack = finished.pop()
        print('finished: ' + str(len(finished)))
        while (not stack.cycled()) and (not stack.finished()):
            continuing = Stack.flag_dict[stack.states[-1].code]
            old_stack = deepcopy(stack)
            for i, s in enumerate(continuing):
                if i > 0:
                    new_stack = old_stack.deepcopy()
                    copied_stack = s[0]
                    index = s[1]
                    new_stack.states.extend(copied_stack.states[index:])
                    finished.append(new_stack)
                    continue
                copied_stack = s[0]
                index = s[1]
                stack.states.extend(copied_stack.states[index:])
        stacks.append(stack)
    return stacks, anchors

prog = re.compile(r'{(.*),{(.*)},{(.*)}},')
lang = defaultdict(lambda: defaultdict(list))
visited_code = 100


def main():
    with open('language.txt') as f:
        for l in f:
            m = prog.match(l)
            state = m.group(1)
            column = m.group(2).split(',')[0]  # Okrem END na konci, alebo END ak je
                                               # to jediny terminal
            contents = m.group(3).split(',')[:-1] # Okrem END na konci
            lang[state][column] = contents

        # pprint.pprint(lang)

    states = [('START', 'Ttree'), ('START', 'Tspace'), ('START', 'Tprimary'),
              ('START', 'Tfunction'), ('START', 'T_id')]
    # states = [('START', 'Tspace')]

    for t in states:
        stacks, anchors = expand(*t)
        print('Pre stav ' + str(t))
        for i, s in enumerate(stacks, 1):
            # print('Pre stav ' + str(t) + ' verzia c. ' + str(i) + ':')
            print(s.print_states())
            # s.print_info()
            # print()
        print()
        # print('Zoznam odkazanych stavov:')
        # for i, s in anchors.items():
        #     print(str(i) + ' ' + str(s))
        # print('\n')

    # with open('lang.pickle', 'wb') as lang_f:
    #     pickle.dump(lang, lang_f)


if __name__ == '__main__':
    main()
