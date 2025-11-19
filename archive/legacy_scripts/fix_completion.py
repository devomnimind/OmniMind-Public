# Fix completion flag in ReactAgent

file_path = "src/agents/react_agent.py"
with open(file_path, "r") as f:
    content = f.read()

# Fix 1: Modify _observe_node to set completion flags
old_observe = '''    def _observe_node(self, state: AgentState) -> AgentState:
        """Process action results and create observations."""
        if state['actions_taken']:
            last_action = state['actions_taken'][-1]
            observation = f"Action '{last_action['action']}' completed. Result: {last_action['result'][:200]}"
            
            state['observations'].append(observation)
            state['messages'].append(f"[OBSERVE] {observation}")
        
        state['iteration'] += 1
        return state'''

new_observe = '''    def _observe_node(self, state: AgentState) -> AgentState:
        """Process action results and create observations."""
        if state['actions_taken']:
            last_action = state['actions_taken'][-1]
            observation = f"Action '{last_action['action']}' completed. Result: {last_action['result'][:200]}"
            
            state['observations'].append(observation)
            state['messages'].append(f"[OBSERVE] {observation}")
            
            # Check if task is completed based on observation
            success_keywords = ['success', 'completed', 'done', 'written']
            if any(word in observation.lower() for word in success_keywords):
                state['completed'] = True
                state['final_result'] = observation
        
        state['iteration'] += 1
        return state'''

content = content.replace(old_observe, new_observe)

# Fix 2: Simplify _should_continue to just check flags
old_should = '''    def _should_continue(self, state: AgentState) -> str:
        """Decide if agent should continue or terminate."""
        # Check max iterations
        if state['iteration'] >= state['max_iterations']:
            state['completed'] = True
            state['final_result'] = "Max iterations reached"
            return "end"
        
        # Check if task appears completed (simple heuristic)
        if state['observations']:
            last_obs = state['observations'][-1].lower()
            if any(word in last_obs for word in ['success', 'completed', 'done', 'written']):
                state['completed'] = True
                state['final_result'] = last_obs
                return "end"
        
        return "continue"'''

new_should = '''    def _should_continue(self, state: AgentState) -> str:
        """Decide if agent should continue or terminate."""
        # Check max iterations
        if state['iteration'] >= state['max_iterations']:
            return "end"
        
        # Check if task is completed (flag set in _observe_node)
        if state['completed']:
            return "end"
        
        return "continue"'''

content = content.replace(old_should, new_should)

with open(file_path, "w") as f:
    f.write(content)

print("✅ Fixed completion logic:")
print("   - Moved completion detection to _observe_node")
print("   - _should_continue now only checks flags")
print("   - State mutations happen in nodes, not in conditional edges")
