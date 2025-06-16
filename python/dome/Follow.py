class GrammarAnalyzer:
    def __init__(self, grammar):
        self.grammar = grammar
        self.non_terminals = set()
        self.terminals = set()
        self.productions = {}
        self.first = {}
        self.follow = {}
        self.epsilon = 'ε'
        
        self._parse_grammar()
    
    def _parse_grammar(self):
        """解析文法规则"""
        for rule in self.grammar:
            left, right = rule.split('->')
            left = left.strip()
            right = [s.strip() for s in right.split('|')]
            
            self.non_terminals.add(left)
            
            if left not in self.productions:
                self.productions[left] = []
                
            for prod in right:
                self.productions[left].append(prod)
                for symbol in prod.split():
                    if symbol != self.epsilon and not symbol.isupper() and not symbol.isdigit():
                        self.terminals.add(symbol)
                    elif symbol.isupper():
                        self.non_terminals.add(symbol)
    
    def compute_first(self):
        """计算所有非终结符的FIRST集合"""
        # 初始化
        for non_terminal in self.non_terminals:
            self.first[non_terminal] = set()
        
        changed = True
        while changed:
            changed = False
            for non_terminal in self.non_terminals:
                for production in self.productions[non_terminal]:
                    symbols = production.split()
                    # 处理产生式右部的每个符号
                    for i, symbol in enumerate(symbols):
                        if symbol == self.epsilon:
                            # 如果是ε，加入FIRST集
                            if self.epsilon not in self.first[non_terminal]:
                                self.first[non_terminal].add(self.epsilon)
                                changed = True
                            break
                        elif symbol in self.terminals:
                            # 如果是终结符，加入FIRST集并停止
                            if symbol not in self.first[non_terminal]:
                                self.first[non_terminal].add(symbol)
                                changed = True
                            break
                        else:
                            # 如果是非终结符，将其FIRST集(除ε)加入
                            before_size = len(self.first[non_terminal])
                            self.first[non_terminal].update(
                                self.first[symbol] - {self.epsilon}
                            )
                            if len(self.first[non_terminal]) != before_size:
                                changed = True
                            
                            # 如果该非终结符的FIRST集不含ε，停止
                            if self.epsilon not in self.first[symbol]:
                                break
                            
                            # 如果所有符号的FIRST集都含ε，则加入ε
                            if i == len(symbols) - 1:
                                if self.epsilon not in self.first[non_terminal]:
                                    self.first[non_terminal].add(self.epsilon)
                                    changed = True
        return self.first
    
    def compute_follow(self):
        """计算所有非终结符的FOLLOW集合"""
        if not self.first:
            self.compute_first()
        
        # 初始化
        for non_terminal in self.non_terminals:
            self.follow[non_terminal] = set()
        self.follow[next(iter(self.non_terminals))].add('$')  # 文法开始符号的FOLLOW集加入$
        
        changed = True
        while changed:
            changed = False
            for non_terminal in self.non_terminals:
                for production in self.productions[non_terminal]:
                    symbols = production.split()
                    for i, symbol in enumerate(symbols):
                        if symbol in self.non_terminals:
                            # 处理非终结符
                            j = i + 1
                            while j < len(symbols):
                                next_symbol = symbols[j]
                                if next_symbol in self.terminals:
                                    # 如果是终结符，直接加入FOLLOW集
                                    before_size = len(self.follow[symbol])
                                    self.follow[symbol].add(next_symbol)
                                    if len(self.follow[symbol]) != before_size:
                                        changed = True
                                    break
                                else:
                                    # 如果是非终结符，加入其FIRST集(除ε)
                                    before_size = len(self.follow[symbol])
                                    self.follow[symbol].update(
                                        self.first[next_symbol] - {self.epsilon}
                                    )
                                    if len(self.follow[symbol]) != before_size:
                                        changed = True
                                    
                                    # 如果FIRST集不含ε，停止
                                    if self.epsilon not in self.first[next_symbol]:
                                        break
                                    j += 1
                            
                            # 如果到达产生式末尾或后面所有符号的FIRST集都含ε
                            if j == len(symbols):
                                before_size = len(self.follow[symbol])
                                self.follow[symbol].update(self.follow[non_terminal])
                                if len(self.follow[symbol]) != before_size:
                                    changed = True
        return self.follow
    
    def print_first_sets(self):
        """打印FIRST集合"""
        print("FIRST集合:")
        for non_terminal in sorted(self.non_terminals):
            print(f"FIRST({non_terminal}) = {sorted(self.first.get(non_terminal, []))}")
    
    def print_follow_sets(self): 
        """打印FOLLOW集合"""
        print("FOLLOW集合:") 
        for non_terminal in sorted(self.non_terminals):
            print(f"FOLLOW({non_terminal}) = {sorted(self.follow.get(non_terminal, []))}")


# 示例用法
if __name__ == "__main__":
    # 示例文法
    grammar = [
        "E -> T E'",
        "E' -> + T E' | ε",
        "T -> F T'",
        "T' -> * F T' | ε",
        "F -> ( E ) | id"
    ]
    
    analyzer = GrammarAnalyzer(grammar)
    analyzer.compute_first()
    analyzer.compute_follow()
    
    analyzer.print_first_sets()
    analyzer.print_follow_sets()