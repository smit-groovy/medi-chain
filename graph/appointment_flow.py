from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from agent.medical_agent import get_medical_explainer, get_symptom_validator
from utils.appointments import save_appointment


class AppointmentState(BaseModel):
    user: str
    doctor: str
    symptoms: str
    datetime: str
    wallet: str
    explanation: str = ""
    cid: str = ""
    valid: bool = True  # default to True


def get_graph_chain():
    graph = StateGraph(state_schema=AppointmentState)

    # Node 1: Ask symptoms (placeholder)
    def ask_symptoms(state: AppointmentState):
        return {}

    # Node 2: Validate symptoms
    def validate_symptoms_node(state: AppointmentState):
        validator = get_symptom_validator()
        result = validator.invoke(state.symptoms)
        response = result.content.strip().lower()
        return {"valid": "yes" in response}

    # Node 3a: If valid, run explainer
    def ai_explainer_node(state: AppointmentState):
        chain = get_medical_explainer()
        result = chain.invoke(state.symptoms)
        explanation = result.content if hasattr(result, "content") else str(result)
        return {"explanation": explanation.strip()}

    # Node 3b: If invalid, skip
    def early_exit_node(state: AppointmentState):
        return {}  # no-op, ends early

    # Node 4: Save + Upload to IPFS
    def confirm_and_save(state: AppointmentState):
        appointment = {
            "user": state.user,
            "doctor": state.doctor,
            "symptoms": state.symptoms,
            "datetime": state.datetime,
            "explanation": state.explanation,
        }

        try:
            cid = save_appointment(wallet=state.wallet, **appointment)
            return {"cid": cid}
        except Exception as e:
            print("⚠️ IPFS Upload Failed:", e)
            return {"cid": "Upload failed"}

    # ---- Register Nodes
    graph.add_node("ask_symptoms", ask_symptoms)
    graph.add_node("validate", validate_symptoms_node)
    graph.add_node("ai_explainer", ai_explainer_node)
    graph.add_node("early_exit", early_exit_node)
    graph.add_node("confirm_save", confirm_and_save)

    # ---- Define Flow
    graph.set_entry_point("ask_symptoms")
    graph.add_edge("ask_symptoms", "validate")

    # Conditional on `valid`
    graph.add_conditional_edges(
    "validate",
    lambda state: state.valid,
    {
        True: "ai_explainer",
        False: "early_exit"
    }
)

    graph.add_edge("ai_explainer", "confirm_save")
    graph.add_edge("early_exit", END)
    graph.add_edge("confirm_save", END)

    return graph.compile()


def run_appointment_chain(state_dict: dict):
    graph = get_graph_chain()
    return graph.invoke(state_dict)

def get_flow_mermaid_png_bytes():
    graph = get_graph_chain()
    try:
        png_bytes = graph.get_graph().draw_mermaid_png()
        return png_bytes
    except Exception as e:
        print(f"⚠️ Mermaid PNG generation failed: {e}")
        return None
