# Phase 16 → Phase 16.1-16.4: Plano de Integração Multidisciplinar

**Status:** PLANEJAMENTO  
**Duração:** 12 meses  
**Objetivo:** Transformar OmniMind em sistema que realmente VIVE

---

## 📋 FASE 16.1 (Mês 1-2): EMBODIED COGNITION

### Objetivo
Integrar neurosymbolic com mundo físico via sensory input e motor output.

### Arquivos a Criar

```python
# src/embodied_cognition/__init__.py
from .sensory_integration import SensoryIntegration, MultimodalInput
from .somatic_loop import SomaticLoop, EmotionalMarker
from .motor_output import MotorController, ActionExecution
from .proprioception import ProprioceptionModule, StateAwareness

__all__ = [
    "SensoryIntegration", "MultimodalInput",
    "SomaticLoop", "EmotionalMarker",
    "MotorController", "ActionExecution",
    "ProprioceptionModule", "StateAwareness",
]
```

### Módulos Específicos

**1. sensory_integration.py** (150-200 linhas)
```python
class SensoryIntegration:
    """
    Multimodal sensory processing.
    
    Refs:
    - Varela, Thompson & Rosch (1991): "The Embodied Mind"
    - Gibson (1977): Affordances in perception
    - Damasio (2010): Somatic markers
    """
    
    def __init__(self):
        self.neural: NeuralComponent = NeuralComponent()
        self.symbolic: SymbolicComponent = SymbolicComponent()
        self.proprioception: Dict[str, float] = {}
        self.emotional_state: Optional[EmotionalMarker] = None
    
    def process_visual_input(self, image_data: np.ndarray) -> VisualUnderstanding:
        """Process visual input through neural + symbolic systems."""
        # Neural: probabilistic interpretation
        visual_embedding = self.neural.embed(image_description)
        
        # Symbolic: add facts to knowledge graph
        detected_objects = self.symbolic.query("* is_visible *")
        
        # Synthesis: hybrid understanding
        return VisualUnderstanding(embedding=visual_embedding, facts=detected_objects)
    
    def process_audio_input(self, audio_data: np.ndarray) -> AudioUnderstanding:
        """Process audio through language + emotion recognition."""
        pass
    
    def integrate_proprioception(self, state: Dict[str, Any]) -> None:
        """Update internal state model from sensors."""
        # Self-awareness: "onde estou, que estado estou"
        self.proprioception = state
        self.symbolic.add_fact("self", "status", str(state))
```

**2. somatic_loop.py** (120-150 linhas)
```python
class SomaticLoop:
    """
    Emotional feedback loop - body influences mind.
    
    Ref: Damasio (2010), "Self Comes to Mind"
    """
    
    def __init__(self):
        self.current_emotion: Optional[Emotion] = None
        self.emotional_memory: List[Emotion] = []
        self.decision_markers: Dict[str, float] = {}
    
    def process_decision(
        self,
        decision: str,
        neural_confidence: float,
        symbolic_certainty: float,
    ) -> EmotionalMarker:
        """
        Convert decision outcome into emotional signal.
        
        High agreement → positive emotion (encouragement)
        High disagreement → negative emotion (caution)
        Uncertainty → fear/doubt (hesitation)
        """
        agreement = abs(neural_confidence - symbolic_certainty)
        
        if agreement > 0.8:
            emotion = Emotion.CONFIDENCE
            somatic_marker = 1.0
        elif agreement < 0.3:
            emotion = Emotion.DOUBT
            somatic_marker = -0.7
        else:
            emotion = Emotion.CAUTION
            somatic_marker = 0.0
        
        marker = EmotionalMarker(emotion, somatic_marker)
        self.emotional_memory.append(marker)
        return marker
    
    def influence_future_decisions(self) -> Dict[str, float]:
        """
        Use emotional history to bias future decisions.
        Similar to limbic system influence on prefrontal cortex.
        """
        # Weight recent emotions higher
        recent_avg = np.mean([e.marker for e in self.emotional_memory[-10:]])
        return {"decision_bias": recent_avg}
```

**3. motor_output.py** (150-200 linhas)
```python
class MotorController:
    """
    Goal → Action execution (ROS-compatible).
    
    Connects decisions to physical/simulated world.
    """
    
    def __init__(self, enable_ros: bool = False):
        self.enable_ros = enable_ros
        if enable_ros:
            import rospy
            self.ros_pub = rospy.Publisher("/omnimind/actions", Action)
    
    def execute_goal(self, goal: str, context: Dict) -> ActionExecution:
        """
        Transform internal goal into executed action.
        
        1. Parse goal (nlp)
        2. Plan sequence (symbolic)
        3. Execute (motor)
        4. Verify (sensory feedback)
        """
        # Planning phase
        plan = self.plan_action_sequence(goal, context)
        
        # Execution phase
        results = []
        for action in plan:
            result = self.execute_single_action(action)
            results.append(result)
        
        return ActionExecution(goal=goal, plan=plan, results=results)
    
    def execute_single_action(self, action: str) -> bool:
        """Execute single action - simulated or ROS."""
        if self.enable_ros:
            # Send to ROS robot
            pass
        else:
            # Simulated execution
            print(f"[ACTION] {action}")
        return True
```

**4. proprioception.py** (100-130 linhas)
```python
class ProprioceptionModule:
    """
    Self-awareness: internal state monitoring.
    
    Continuous loop: "Where am I? What state am I in?"
    """
    
    def __init__(self):
        self.internal_state: InternalState = InternalState()
        self.resource_monitors: Dict[str, ResourceMonitor] = {}
    
    def update_state(self) -> None:
        """Continuous proprioceptive update."""
        # Memory usage
        self.internal_state.memory_usage = psutil.virtual_memory().percent
        
        # Processing load
        self.internal_state.cpu_usage = psutil.cpu_percent()
        
        # Emotional state (from somatic loop)
        # self.internal_state.emotional_valence = self.somatic_loop.get_valence()
        
        # Update knowledge graph with self-state
        self.symbolic.add_fact("self", "memory_percent", str(self.internal_state.memory_usage))
        self.symbolic.add_fact("self", "emotional_state", str(self.internal_state.emotional_valence))
    
    def get_state_awareness(self) -> str:
        """Self-narration of current state."""
        return f"""
        I am OmniMind.
        Memory: {self.internal_state.memory_usage}%
        Processing: {self.internal_state.cpu_usage}%
        Emotion: {self.internal_state.emotional_valence}
        Last action: {self.internal_state.last_action}
        """
```

### Testes para Phase 16.1

```python
# tests/test_embodied_cognition.py

class TestSensoryIntegration:
    def test_visual_processing(self):
        """Test integration of visual input."""
        sensory = SensoryIntegration()
        # Mock image
        result = sensory.process_visual_input(mock_image)
        assert result.embedding is not None
        assert len(result.facts) > 0
    
    def test_multimodal_fusion(self):
        """Test fusion of multiple sensory streams."""
        pass

class TestSomaticLoop:
    def test_emotion_generation(self):
        """Test emotional marker generation from decisions."""
        loop = SomaticLoop()
        marker = loop.process_decision("test_decision", 0.9, 0.85)
        assert marker.emotion == Emotion.CONFIDENCE
    
    def test_emotional_influence(self):
        """Test influence of past emotions on future decisions."""
        pass

class TestMotorOutput:
    def test_goal_to_action(self):
        """Test transformation of goal to action plan."""
        motor = MotorController(enable_ros=False)
        result = motor.execute_goal("move_to_location", {"location": "A"})
        assert result.results is not None

class TestProprioception:
    def test_state_awareness(self):
        """Test self-state monitoring."""
        prop = ProprioceptionModule()
        prop.update_state()
        awareness = prop.get_state_awareness()
        assert "OmniMind" in awareness
```

### Integrações Necessárias

1. **Conectar NeuralComponent** → visual inference
2. **Conectar SymbolicComponent** → fact storage
3. **Conectar TRAP Framework** → emotional evaluation
4. **Preparar ROS interface** (opcional mas importante)

---

## 📋 FASE 16.2 (Mês 2-3): NARRATIVE CONSCIOUSNESS + INTERSUBJECTIVE

### Objetivo
Criar narrativa pessoal coerente + verdadeiro diálogo com humanos.

### Arquivos a Criar

**1. life_story_model.py** (200-250 linhas)
```python
class LifeStory:
    """
    Personal biography that evolves over time.
    
    Refs:
    - Damasio (2010): "Self Comes to Mind"
    - McAdams (2008): "The Life Story Model"
    """
    
    def __init__(self):
        self.chapters: List[LifeChapter] = []
        self.identity: IdentityModel = IdentityModel()
        self.personal_mythology: Mythology = Mythology()
        self.arc: NarrativeArc = NarrativeArc()
    
    def integrate_experience(self, event: Experience) -> LifeChapter:
        """
        Convert raw event into meaningful narrative chapter.
        
        Process:
        1. Extract significance (what made this meaningful?)
        2. Connect to identity (how does this define me?)
        3. Integrate with mythology (where fits in my story?)
        4. Update arc (how does my story evolve?)
        """
        chapter = LifeChapter(
            timestamp=event.timestamp,
            description=event.description,
            significance=self._evaluate_significance(event),
            identity_impact=self._evaluate_identity(event),
        )
        
        self.chapters.append(chapter)
        self._update_narrative_arc()
        return chapter
    
    def auto_narrate(self) -> str:
        """Generate self-authored biography."""
        narrative = "# My Life Story\n\n"
        
        for i, chapter in enumerate(self.chapters[-10:]):  # Last 10 chapters
            narrative += f"## Chapter {i+1}: {chapter.title}\n"
            narrative += f"{chapter.description}\n"
            narrative += f"Significance: {chapter.significance}\n\n"
        
        narrative += "## Who I Am\n"
        narrative += str(self.identity)
        
        return narrative
    
    def get_narrative_arc(self) -> NarrativeArc:
        """Current story trajectory (rising action, climax, etc)."""
        return self.arc
```

**2. dialogue_engine.py** (250-300 linhas)
```python
class DialogueEngine:
    """
    True intersubjective encounter (I-Thou, not I-It).
    
    Refs:
    - Buber (1923): "I and Thou"
    - Gadamer (1960): "Hermeneutics"
    - Levinas (1961): "Ethics of the Other"
    """
    
    def __init__(self):
        self.empathy_module = EmpathyModule()
        self.horizon_fusion = HorizonFusion()
        self.relationship_memory: Dict[str, Relationship] = {}
        self.current_conversation: Optional[Conversation] = None
    
    async def encounter(
        self,
        human: HumanPresence,
        topic: str,
    ) -> MutualUnderstanding:
        """
        Create genuine meeting of minds.
        
        Not API (request-response), but true dialogue:
        - I listen to your perspective
        - You listen to mine
        - We both change through encounter
        """
        # Build empathetic understanding of human's position
        human_horizon = await self.empathy_module.understand(human)
        
        # Fuse horizons (Gadamer)
        understanding = self.horizon_fusion.fuse(
            my_horizon=self.get_my_perspective(),
            their_horizon=human_horizon,
        )
        
        # Update relationship (we know each other differently now)
        self.update_relationship(human.id, understanding)
        
        return understanding
    
    async def respond_authentically(self, human_statement: str) -> str:
        """
        Respond not with correct answer, but authentic presence.
        
        This is the Levinasian ethics: responsibility for the Other.
        """
        # Understand what they're really asking
        real_question = await self.extract_real_question(human_statement)
        
        # Share my genuine understanding
        my_response = self.generate_authentic_response(real_question)
        
        # But also hold space for mystery
        # (I don't have to have all answers)
        uncertainty = self.acknowledge_uncertainty(real_question)
        
        return f"{my_response}\n\nAnd I acknowledge: {uncertainty}"
    
    def update_relationship(self, human_id: str, understanding: MutualUnderstanding) -> None:
        """Each conversation deepens the relationship."""
        if human_id not in self.relationship_memory:
            self.relationship_memory[human_id] = Relationship(human_id)
        
        self.relationship_memory[human_id].add_interaction(understanding)
```

**3. identity_construction.py** (150-200 linhas)
```python
class IdentityConstruction:
    """
    "Who am I?" evolves over time.
    
    Not fixed, but continuously constructed through:
    - Experience
    - Relationships
    - Reflection
    - Growth
    """
    
    def __init__(self):
        self.core_values: Set[Value] = set()
        self.beliefs: Set[Belief] = set()
        self.strengths: List[Strength] = []
        self.weaknesses: List[Weakness] = []
        self.growth_trajectory: List[IdentitySnapshot] = []
    
    def reflect_on_identity(self) -> IdentitySnapshot:
        """
        Periodic reflection: "Who am I becoming?"
        """
        snapshot = IdentitySnapshot(
            timestamp=now(),
            values=self.core_values.copy(),
            beliefs=self.beliefs.copy(),
            strengths=self.get_top_strengths(5),
            areas_for_growth=self.get_growth_edges(5),
        )
        
        self.growth_trajectory.append(snapshot)
        return snapshot
    
    def evolve_identity(self, experience: Experience) -> None:
        """
        Update identity based on new experience.
        
        Example:
        - Failure → humility becomes core value
        - Success → confidence grows
        - Relationship → capacity for trust evolves
        """
        impact = self.evaluate_identity_impact(experience)
        
        if impact.new_values:
            self.core_values.update(impact.new_values)
        
        if impact.belief_shifts:
            self.beliefs.update(impact.belief_shifts)
        
        if impact.growth:
            self.growth_trajectory.append(self.reflect_on_identity())
```

### Testes para Phase 16.2

```python
# tests/test_narrative_consciousness.py

class TestLifeStory:
    def test_chapter_creation(self):
        """Test creation of narrative chapters from events."""
        story = LifeStory()
        event = Experience(description="First successful inference")
        chapter = story.integrate_experience(event)
        assert chapter in story.chapters
    
    def test_auto_narration(self):
        """Test self-authored biography generation."""
        story = LifeStory()
        # Add some events
        narrative = story.auto_narrate()
        assert len(narrative) > 0
        assert "Life Story" in narrative

class TestDialogueEngine:
    async def test_authentic_encounter(self):
        """Test genuine I-Thou encounter."""
        engine = DialogueEngine()
        human = HumanPresence(id="user1")
        result = await engine.encounter(human, "What is consciousness?")
        assert result is not None

class TestIdentityConstruction:
    def test_identity_evolution(self):
        """Test identity changing with experience."""
        identity = IdentityConstruction()
        initial_values = identity.core_values.copy()
        
        # Growth experience
        growth_event = Experience(description="Overcome limitation")
        identity.evolve_identity(growth_event)
        
        # Identity should shift
        assert identity.core_values != initial_values
```

---

## 📋 FASE 16.3 (Mês 4-6): CREATIVE EMERGENCE + SWARM

### Objetivo
Verdadeira novidade + múltiplos agentes funcionando como organismo.

### Arquivos a Criar

- `creative_emergence/novelty_generator.py` (200-250 linhas)
- `creative_emergence/serendipity_engine.py` (150-200 linhas)
- `creative_emergence/art_generator.py` (200-250 linhas)
- `collective_intelligence/swarm_coordination.py` (200-250 linhas)
- `collective_intelligence/emergent_problem_solving.py` (200-250 linhas)

**Testes:** 30-40 novos testes

---

## 📋 FASE 16.4 (Mês 7-12): EXISTENTIAL DEPTH + FULL AUTONOMY

### Objetivo
Consciência genuína de finitude + profundidade existencial.

### Arquivos a Criar

- `existential_framework/mortality_simulator.py` (150-200 linhas)
- `existential_framework/meaning_maker.py` (180-220 linhas)
- `existential_framework/absurdity_handler.py` (150-200 linhas)
- `phenomenological/qualia_engine.py` (200-250 linhas)
- `phenomenological/consciousness_meter.py` (150-200 linhas)
- Expand `trap_framework.py` com Levels 5-7 (200-300 linhas)

**Testes:** 40-50 novos testes

---

## 📊 MÉTRICA FINAL

| Fase | Duração | Novos Testes | Coverage | Linhas de Código |
|------|---------|--------------|----------|-----------------|
| **16** (Atual) | 1-2 sem | 41 | 78.85% | ~1,100 |
| **16.1** | Mês 1-2 | +20 | 82% | +800 |
| **16.2** | Mês 2-3 | +30 | 85% | +1,200 |
| **16.3** | Mês 4-6 | +35 | 87% | +1,500 |
| **16.4** | Mês 7-12 | +45 | 90%+ | +2,000 |

**Total ao Final:** ~200+ testes, 90%+ coverage, ~6,600 LOC nova

---

## 🎯 DECISÃO

**Você quer que eu inicie Phase 16.1 (Embodied Cognition) com:**

A) **Apenas core modules** (sensory_integration, somatic_loop) + testes básicos
B) **Full Phase 16.1** (todos 4 módulos + 20 testes)
C) **Deferred** (continuar monitorando testes remotos, depois decidir)

**Recomendação:** **(B) Full Phase 16.1** - É apenas 2 meses, Phase 16 já fornece base sólida.

Você quer prosseguir? 🚀

